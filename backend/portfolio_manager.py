from models import PortfolioPosition, SystemSettings
from datetime import datetime, timezone

def update_portfolio(db, signal_data):
    """
    Updates the current prices of existing portfolio positions based on new signal data.
    If Auto Paper Trading is ON, it will execute virtual buy/sell orders.
    """
    ticker = signal_data['ticker']
    price = signal_data['current_price']
    gap_pct = signal_data['gap_pct']
    
    high_risk = abs(gap_pct) > 2.0
    
    position = db.query(PortfolioPosition).filter(PortfolioPosition.ticker == ticker).first()
    
    # Check paper trading settings
    auto_setting = db.query(SystemSettings).filter(SystemSettings.key == "auto_paper_trade").first()
    auto_trade = auto_setting.value == "true" if auto_setting else False
    
    cash_setting = db.query(SystemSettings).filter(SystemSettings.key == "cash_balance").first()
    if not cash_setting:
        cash_setting = SystemSettings(key="cash_balance", value="1000000.0")
        db.add(cash_setting)
        db.commit()
    cash_balance = float(cash_setting.value)
    
    alerts = []
    
    if position:
        # Just update the current price and risk status of manually held positions
        position.current_price = price
        position.high_risk = high_risk
        position.updated_at = datetime.now(timezone.utc)
        
        if price <= position.stop_loss:
            alerts.append(f"WARNING: {ticker} has dropped below Stop Loss of {position.stop_loss:.2f}!")
            if auto_trade:
                # Execute auto paper sell for stop loss
                revenue = position.shares * price
                cash_balance += revenue
                cash_setting.value = str(cash_balance)
                db.delete(position)
                alerts.append(f"AUTO PAPER TRADE: Sold {ticker} at Stop Loss.")
        elif signal_data['signal'] == "SELL":
            alerts.append(f"WARNING: AI generated a SELL signal for {ticker}!")
            if auto_trade:
                # Execute auto paper sell
                revenue = position.shares * price
                cash_balance += revenue
                cash_setting.value = str(cash_balance)
                db.delete(position)
                alerts.append(f"AUTO PAPER TRADE: Sold {ticker} on SELL signal.")
                
    elif auto_trade and signal_data['signal'] == "BUY":
        # Check if we should buy
        allocation = min(cash_balance, 1000000.0 * 0.05) # Max 5% of portfolio per trade
        shares = int(allocation / price)
        if shares > 0:
            cost = shares * price
            cash_balance -= cost
            cash_setting.value = str(cash_balance)
            
            new_pos = PortfolioPosition(
                ticker=ticker,
                entry_price=price,
                current_price=price,
                shares=shares,
                stop_loss=price * 0.90, # default 10% stop loss
                high_risk=high_risk
            )
            db.add(new_pos)
            alerts.append(f"AUTO PAPER TRADE: Bought {shares} shares of {ticker} on BUY signal.")
            
    db.commit()
    return alerts
