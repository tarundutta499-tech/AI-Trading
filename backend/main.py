from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import SignalHistory, PortfolioPosition, MarketNews, SystemSettings
from tickers import NIFTY_TICKERS, MARKET_INDEX
from data_fetcher import get_stock_data, get_fundamentals, get_index_data, clear_index_cache
from indicator_calc import calculate_indicators
from sentiment_analyzer import get_news_sentiment
from signal_generator import generate_signals
from portfolio_manager import update_portfolio
from broker_angelone import broker as angel_broker

import logging
from datetime import datetime, timezone
from pydantic import BaseModel
import yfinance as yf

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_analysis_cycle():
    logger.info("Starting analysis cycle...")
    # Setup a new session for the background task
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        clear_index_cache()
        market_df = get_index_data(MARKET_INDEX)
        if market_df is not None:
            market_df = calculate_indicators(market_df)
            
        for ticker, sector_idx in NIFTY_TICKERS.items():
            try:
                logger.info(f"Analyzing {ticker}...")
                
                sector_df = get_index_data(sector_idx)
                if sector_df is not None:
                    sector_df = calculate_indicators(sector_df)
                
                # 1. Fetch Data
                df = get_stock_data(ticker)
                if df is None or df.empty:
                    continue
                    
                fundamentals = get_fundamentals(ticker)
                
                # 2. Indicators
                df = calculate_indicators(df)
                
                # 3. Sentiment
                sentiment_stats, recent_news = get_news_sentiment(ticker)
                
                # Save to MarketNews
                for n in recent_news:
                    existing = db.query(MarketNews).filter(MarketNews.link == n['link']).first()
                    if not existing:
                        db.add(MarketNews(
                            ticker=n['ticker'],
                            title=n['title'],
                            link=n['link'],
                            published_at=n['published'],
                            sentiment_score=n['sentiment']
                        ))
                
                # 4. Signal
                signal_data = generate_signals(ticker, df, fundamentals, sentiment_stats, market_df, sector_df)
                
                if not signal_data:
                    continue
                    
                # 5. Save Signal
                new_signal = SignalHistory(
                    ticker=ticker,
                    signal=signal_data['signal'],
                    score=signal_data['score'],
                    technical_score=signal_data['technical_score'],
                    fundamental_score=signal_data['fundamental_score'],
                    sentiment_score=signal_data['sentiment_score'],
                    risk_score=signal_data['risk_score'],
                    market_score=signal_data['market_score'],
                    sector_score=signal_data['sector_score'],
                    confidence_score=signal_data['confidence_score'],
                    reasons=signal_data['reasons'],
                    warnings=signal_data['warnings'],
                    tech_details=signal_data['tech_details']
                )
                db.add(new_signal)
                
                # 6. Portfolio Update & Alerts
                alerts = update_portfolio(db, signal_data)
                for alert in alerts:
                    logger.info(f"ALERT: {alert}")
                    
                db.commit()
                
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                db.rollback()
    finally:
        db.close()
        logger.info("Analysis cycle completed.")

scheduler = BackgroundScheduler()
# Run every 30 mins during market hours (9:15 to 15:30 IST) Mon-Fri
scheduler.add_job(
    run_analysis_cycle,
    CronTrigger(day_of_week='mon-fri', hour='9-15', minute='*/30', timezone='Asia/Kolkata')
)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    # Get latest signals
    signals = []
    for ticker in NIFTY_TICKERS.keys():
        latest = db.query(SignalHistory).filter(SignalHistory.ticker == ticker).order_by(SignalHistory.id.desc()).first()
        if latest:
            import json
            signals.append({
                "ticker": latest.ticker,
                "signal": latest.signal,
                "score": round(latest.score, 2),
                "technical_score": round(latest.technical_score, 2) if latest.technical_score else None,
                "fundamental_score": round(latest.fundamental_score, 2) if latest.fundamental_score else None,
                "sentiment_score": round(latest.sentiment_score, 2) if latest.sentiment_score else None,
                "risk_score": round(latest.risk_score, 2) if latest.risk_score else None,
                "market_score": round(latest.market_score, 2) if latest.market_score else None,
                "sector_score": round(latest.sector_score, 2) if latest.sector_score else None,
                "confidence_score": round(latest.confidence_score, 2) if latest.confidence_score else None,
                "reasons": json.loads(latest.reasons) if latest.reasons else [],
                "warnings": json.loads(latest.warnings) if latest.warnings else [],
                "tech_details": json.loads(latest.tech_details) if latest.tech_details else {},
                "created_at": latest.created_at
            })
            
    # Sort for top 5 BUY
    signals.sort(key=lambda x: x["score"], reverse=True)
    top_5 = signals[:5]
    
    positions = db.query(PortfolioPosition).all()
    
    # Fetch recent news globally from MarketNews
    news_records = db.query(MarketNews).order_by(MarketNews.published_at.desc()).limit(50).all()
    top_news = []
    for r in news_records:
        top_news.append({
            "ticker": r.ticker,
            "title": r.title,
            "link": r.link,
            "published": r.published_at,
            "sentiment": r.sentiment_score
        })

    return {
        "top_signals": top_5,
        "all_signals": signals,
        "positions": positions,
        "heatmap": [{"ticker": s["ticker"], "sentiment": s["sentiment_score"], "score": s["score"]} for s in signals],
        "news": top_news
    }

@app.post("/api/force-run")
def force_run(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_analysis_cycle)
    return {"message": "Analysis cycle started in background"}

@app.get("/api/news/{ticker}")
def get_news(ticker: str):
    _, news = get_news_sentiment(ticker)
    return news

@app.get("/api/quote/{ticker}")
def get_quote(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return {"price": hist['Close'].iloc[-1]}
    except:
        pass
    return {"price": None}

@app.get("/api/portfolio")
def get_portfolio(db: Session = Depends(get_db)):
    cash_setting = db.query(SystemSettings).filter(SystemSettings.key == "cash_balance").first()
    if not cash_setting:
        cash_setting = SystemSettings(key="cash_balance", value="1000000.0")
        db.add(cash_setting)
        db.commit()
    
    cash_balance = float(cash_setting.value)
    positions = db.query(PortfolioPosition).all()
    
    unrealized_pnl = sum((p.current_price - p.entry_price) * p.shares for p in positions)
    total_equity = cash_balance + sum(p.current_price * p.shares for p in positions)
        
    return {
        "cash_balance": cash_balance,
        "unrealized_pnl": unrealized_pnl,
        "total_equity": total_equity,
        "positions": positions
    }

@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)):
    live_trading = db.query(SystemSettings).filter(SystemSettings.key == "live_trading").first()
    is_live = live_trading.value == "true" if live_trading else False
    return {"live_trading": is_live}

@app.post("/api/settings/live-trading")
def toggle_live_trading(db: Session = Depends(get_db)):
    live_trading = db.query(SystemSettings).filter(SystemSettings.key == "live_trading").first()
    if not live_trading:
        live_trading = SystemSettings(key="live_trading", value="true")
        db.add(live_trading)
    else:
        live_trading.value = "false" if live_trading.value == "true" else "true"
        
    is_live = live_trading.value == "true"
    
    # Try connecting to Angel One if turning ON
    if is_live:
        connected = angel_broker.connect()
        if not connected:
            live_trading.value = "false"
            db.commit()
            return {"error": "Failed to connect to Angel One. Check your .env credentials."}
            
    db.commit()
    return {"message": f"Live trading is now {'ON' if is_live else 'OFF'}", "live_trading": is_live}

class TradeRequest(BaseModel):
    ticker: str
    shares: int = None

@app.post("/api/portfolio/buy")
def buy_stock(req: TradeRequest, db: Session = Depends(get_db)):
    cash_setting = db.query(SystemSettings).filter(SystemSettings.key == "cash_balance").first()
    if not cash_setting:
        cash_setting = SystemSettings(key="cash_balance", value="1000000.0")
        db.add(cash_setting)
        db.commit()
        
    cash = float(cash_setting.value)
    
    try:
        stock = yf.Ticker(req.ticker)
        hist = stock.history(period="1d")
        if hist.empty:
            return {"error": "Failed to fetch current price"}
        price = hist['Close'].iloc[-1]
    except:
        return {"error": "Failed to fetch current price"}
        
    if req.shares and req.shares > 0:
        shares_to_buy = req.shares
    else:
        allocation = min(cash, 1000000.0 * 0.05)
        shares_to_buy = int(allocation / price)
    
    if shares_to_buy == 0:
        return {"error": "Quantity must be at least 1"}
        
    is_live = db.query(SystemSettings).filter(SystemSettings.key == "live_trading").first()
    
    if is_live and is_live.value == "true":
        # Route to Angel One
        res = angel_broker.place_order(req.ticker.replace(".NS", ""), shares_to_buy, "BUY")
        if not res["status"]:
            return {"error": res["message"]}
        # For simulator tracking, we still save it in DB
    
    cost = shares_to_buy * price
    if cash < cost:
        return {"error": f"Not enough cash. Cost is {cost:.2f} but you have {cash:.2f}"}
        
    cash -= cost
    cash_setting.value = str(cash)
    
    existing = db.query(PortfolioPosition).filter(PortfolioPosition.ticker == req.ticker).first()
    if existing:
        total_cost = (existing.entry_price * existing.shares) + cost
        existing.shares += shares_to_buy
        existing.entry_price = total_cost / existing.shares
        existing.current_price = price
        existing.updated_at = datetime.now(timezone.utc)
    else:
        new_pos = PortfolioPosition(
            ticker=req.ticker,
            entry_price=price,
            current_price=price,
            shares=shares_to_buy,
            stop_loss=price * 0.95,
            high_risk=False
        )
        db.add(new_pos)
        
    db.commit()
    msg = f"LIVE ORDER: Bought {shares_to_buy} shares of {req.ticker}" if (is_live and is_live.value == "true") else f"Bought {shares_to_buy} shares of {req.ticker}"
    return {"message": msg}

@app.post("/api/portfolio/sell")
def sell_stock(req: TradeRequest, db: Session = Depends(get_db)):
    position = db.query(PortfolioPosition).filter(PortfolioPosition.ticker == req.ticker).first()
    if not position:
        return {"error": "Position not found"}
        
    shares_to_sell = req.shares if (req.shares and req.shares > 0) else position.shares
    if shares_to_sell > position.shares:
        return {"error": f"You only have {position.shares} shares"}
        
    try:
        stock = yf.Ticker(req.ticker)
        hist = stock.history(period="1d")
        price = hist['Close'].iloc[-1] if not hist.empty else position.current_price
    except:
        price = position.current_price
        
    is_live = db.query(SystemSettings).filter(SystemSettings.key == "live_trading").first()
    
    if is_live and is_live.value == "true":
        res = angel_broker.place_order(req.ticker.replace(".NS", ""), shares_to_sell, "SELL")
        if not res["status"]:
            return {"error": res["message"]}

    revenue = shares_to_sell * price
    
    cash_setting = db.query(SystemSettings).filter(SystemSettings.key == "cash_balance").first()
    cash = float(cash_setting.value) + revenue
    cash_setting.value = str(cash)
    
    if shares_to_sell == position.shares:
        db.delete(position)
    else:
        position.shares -= shares_to_sell
        
    db.commit()
    
    msg = f"LIVE ORDER: Sold {shares_to_sell} shares of {req.ticker}" if (is_live and is_live.value == "true") else f"Sold {shares_to_sell} shares of {req.ticker} for {revenue:.2f}"
    return {"message": msg}
