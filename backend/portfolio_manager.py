from models import PortfolioPosition
from datetime import datetime, timezone

def update_portfolio(db, signal_data):
    """
    Updates the current prices of existing portfolio positions based on new signal data.
    Auto-trading is DISABLED for the Paper Trading Simulator.
    """
    ticker = signal_data['ticker']
    price = signal_data['current_price']
    gap_pct = signal_data['gap_pct']
    
    high_risk = abs(gap_pct) > 2.0
    
    position = db.query(PortfolioPosition).filter(PortfolioPosition.ticker == ticker).first()
    
    alerts = []
    
    if position:
        # Just update the current price and risk status of manually held positions
        position.current_price = price
        position.high_risk = high_risk
        position.updated_at = datetime.now(timezone.utc)
        
        # We don't auto-sell here anymore, the user must do it via the UI
        # We can still emit an alert if it hits stop loss or a sell signal, but we don't close it.
        if price <= position.stop_loss:
            alerts.append(f"WARNING: {ticker} has dropped below Stop Loss of {position.stop_loss:.2f}!")
        elif signal_data['signal'] == "SELL":
            alerts.append(f"WARNING: AI generated a SELL signal for {ticker}!")
            
    db.commit()
    return alerts
