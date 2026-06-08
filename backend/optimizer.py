import logging
from database import SessionLocal
from models import BacktestSession
from backtester import run_backtest
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_strategy(ticker: str, years: int = 3, trailing_stop_pct: float = 10.0):
    logger.info(f"Starting Strategy Optimization for {ticker} over {years} years...")
    db: Session = SessionLocal()
    
    best_profit_factor = 0.0
    best_params = {}
    best_session_id = None
    
    # Grid search for BUY and SELL thresholds
    # BUY: 55, 60, 65, 70
    # SELL: 25, 30, 35, 40
    buy_thresholds = [55, 60, 65, 70]
    sell_thresholds = [25, 30, 35, 40]
    
    try:
        for buy_t in buy_thresholds:
            for sell_t in sell_thresholds:
                if sell_t >= buy_t:
                    continue # Invalid logic
                    
                logger.info(f"Testing BUY: {buy_t}, SELL: {sell_t}...")
                session_id = run_backtest(
                    ticker=ticker,
                    years=years,
                    trailing_stop_pct=trailing_stop_pct,
                    buy_threshold=buy_t,
                    sell_threshold=sell_t
                )
                
                bs = db.query(BacktestSession).filter(BacktestSession.id == session_id).first()
                if bs:
                    pf = bs.profit_factor
                    logger.info(f"Result -> Profit Factor: {pf:.2f}, Return: {bs.total_roi:.2f}%")
                    if pf > best_profit_factor:
                        best_profit_factor = pf
                        best_params = {"buy": buy_t, "sell": sell_t}
                        best_session_id = session_id
                        
        if best_session_id:
            logger.info(f"Optimization Complete for {ticker}! Best Parameters: {best_params} (PF: {best_profit_factor:.2f})")
            return {
                "ticker": ticker,
                "best_buy_threshold": best_params["buy"],
                "best_sell_threshold": best_params["sell"],
                "best_profit_factor": best_profit_factor,
                "best_session_id": best_session_id
            }
        else:
            return {"error": "Failed to find optimal parameters."}
            
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    optimize_strategy(ticker)
