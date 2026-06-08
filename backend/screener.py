import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database import SessionLocal
from models import BacktestSession, GoldenScreenerResult, SignalHistory
from tickers import NIFTY_TICKERS
from backtester import run_backtest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_screener():
    logger.info("Starting Golden Screener...")
    db: Session = SessionLocal()
    
    try:
        # Clear previous day's results to keep the table fresh
        today = datetime.now(timezone.utc).date()
        db.query(GoldenScreenerResult).filter(GoldenScreenerResult.date == today).delete()
        db.commit()
        
        for ticker in NIFTY_TICKERS.keys():
            logger.info(f"Screening {ticker}...")
            
            # Run 3-year backtest
            # We'll use a 10% trailing stop by default for the screener tests to optimize safety
            try:
                session_id = run_backtest(ticker, initial_capital=100000.0, years=3, trailing_stop_pct=10.0)
                
                bs = db.query(BacktestSession).filter(BacktestSession.id == session_id).first()
                if not bs or bs.total_trades == 0:
                    continue
                    
                # The Golden Checklist
                passes = True
                if bs.total_roi <= bs.benchmark_return:
                    passes = False
                if bs.profit_factor < 1.5:
                    passes = False
                if bs.sharpe_ratio < 0.5: # Slightly relaxed sharpe for automated screening
                    passes = False
                    
                if passes:
                    logger.info(f"*** {ticker} PASSED THE GOLDEN CHECKLIST ***")
                    
                    # Get live signal
                    latest_sig = db.query(SignalHistory).filter(SignalHistory.ticker == ticker).order_by(SignalHistory.id.desc()).first()
                    live_signal = latest_sig.signal if latest_sig else "UNKNOWN"
                    
                    res = GoldenScreenerResult(
                        ticker=ticker,
                        date=today,
                        strategy_return=bs.total_roi,
                        benchmark_return=bs.benchmark_return,
                        profit_factor=bs.profit_factor,
                        sharpe_ratio=bs.sharpe_ratio,
                        max_drawdown=bs.max_drawdown,
                        win_rate=bs.win_rate,
                        live_signal=live_signal
                    )
                    db.add(res)
                    db.commit()
            except Exception as e:
                logger.error(f"Error screening {ticker}: {e}")
                db.rollback()
                
    finally:
        db.close()
        logger.info("Golden Screener completed.")

if __name__ == "__main__":
    run_screener()
