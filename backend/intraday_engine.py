import logging
import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal
from models import IntradaySignal
from intraday_signals import calculate_intraday_indicators, generate_intraday_signals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intraday tickers for F&O and Commodity (Simulated with Yahoo Finance available tickers)
INTRADAY_TICKERS = [
    "^NSEI",       # Nifty 50 Index
    "^NSEBANK",    # Nifty Bank Index
    "GC=F",        # Gold Futures
    "CL=F",        # Crude Oil Futures
    "RELIANCE.NS"  # Heavyweight stock for intraday
]

def analyze_intraday_ticker(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="5d", interval="5m")
    
    if df.empty:
        return None
        
    df = calculate_intraday_indicators(df)
    signal_data = generate_intraday_signals(ticker, df)
    return signal_data

def run_intraday_cycle():
    logger.info("Starting Intraday Analysis Cycle (5m)...")
    db = SessionLocal()
    
    try:
        for ticker in INTRADAY_TICKERS:
            try:
                # Fetch 5-minute data for the last 5 days
                stock = yf.Ticker(ticker)
                df = stock.history(period="5d", interval="5m")
                
                if df.empty:
                    logger.warning(f"No intraday data for {ticker}")
                    continue
                    
                df = calculate_intraday_indicators(df)
                signal_data = generate_intraday_signals(ticker, df)
                
                if not signal_data:
                    continue
                    
                # Store the signal
                new_signal = IntradaySignal(
                    ticker=ticker,
                    signal=signal_data['signal'],
                    score=signal_data['score'],
                    current_price=signal_data['current_price'],
                    vwap=signal_data['vwap'],
                    rsi_5m=signal_data['rsi_5m'],
                    macd_histogram=signal_data['macd_histogram'],
                    reasons=signal_data['reasons'],
                    warnings=signal_data['warnings']
                )
                db.add(new_signal)
                db.commit()
                
            except Exception as e:
                logger.error(f"Error processing intraday for {ticker}: {e}")
                db.rollback()
    finally:
        db.close()
        logger.info("Intraday cycle completed.")

def start_intraday_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 5 minutes during standard market hours
    # Note: Commodity hours are longer, but we will simplify to 9am - 11:30pm for MCX 
    # For now, just run it every 5 mins.
    scheduler.add_job(
        run_intraday_cycle,
        CronTrigger(minute='*/5')
    )
    scheduler.start()
    return scheduler
