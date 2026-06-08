import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from database import SessionLocal
from models import BacktestSession, BacktestTrade
from indicator_calc import calculate_indicators
from signal_generator import generate_signals

def run_backtest(ticker: str, initial_capital: float = 100000.0, years: int = 1, trailing_stop_pct: float = None, buy_threshold: int = 65, sell_threshold: int = 35):
    db: Session = SessionLocal()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    try:
        # Create session
        session = BacktestSession(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=initial_capital,
            total_roi=0.0,
            win_rate=0.0,
            max_drawdown=0.0,
            total_trades=0
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
        
        # Fetch data
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        if df.empty:
            return session.id
            
        # Clean data to prevent NaNs in JSON
        df['Close'] = df['Close'].ffill()
        df = df.dropna(subset=['Close'])
        
        df = calculate_indicators(df)
        
        capital = initial_capital
        position_shares = 0
        entry_price = 0.0
        entry_date = None
        trade_high_price = 0.0
        
        trades = []
        peak_capital = initial_capital
        max_dd = 0.0
        
        # Track metrics
        buy_signals = 0
        sell_signals = 0
        daily_portfolio_values = []
        
        # Start from day 50 to allow indicators to warm up
        for i in range(50, len(df)):
            current_date = df.index[i]
            current_price = df.iloc[i]['Close']
            
            # Slice df up to current day to simulate real-time
            slice_df = df.iloc[:i+1]
            
            # Generate signal (TECHNICAL ONLY)
            signal_data = generate_signals(ticker, slice_df, None, None, None, None, is_backtest=True, buy_threshold=buy_threshold, sell_threshold=sell_threshold)
            
            if not signal_data:
                daily_portfolio_values.append(capital + (position_shares * current_price))
                continue
                
            signal = signal_data['signal']
            if signal == "BUY": buy_signals += 1
            if signal == "SELL": sell_signals += 1
            
            if signal == "BUY" and position_shares == 0:
                # Buy logic
                shares = int(capital / current_price)
                if shares > 0:
                    position_shares = shares
                    entry_price = current_price
                    entry_date = current_date
                    trade_high_price = current_price
                    capital -= (shares * current_price)
                    
            elif position_shares > 0:
                # Update highest price seen during trade
                if current_price > trade_high_price:
                    trade_high_price = current_price
                    
                # Check for Trailing Stop OR Standard Sell Signal
                is_stop_triggered = False
                if trailing_stop_pct is not None:
                    stop_price = trade_high_price * (1 - (trailing_stop_pct / 100.0))
                    if current_price <= stop_price:
                        is_stop_triggered = True
                        
                if signal == "SELL" or is_stop_triggered:
                    # Sell logic
                    exit_price = current_price
                    revenue = position_shares * exit_price
                    pnl = revenue - (position_shares * entry_price)
                    pnl_percent = (pnl / (position_shares * entry_price)) * 100
                    capital += revenue
                    
                    trade = BacktestTrade(
                        session_id=session.id,
                        ticker=ticker,
                        entry_date=entry_date,
                        exit_date=current_date,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        shares=position_shares,
                        pnl=pnl,
                        pnl_percent=pnl_percent,
                        signal="STOP_LOSS" if is_stop_triggered else "SELL"
                    )
                    db.add(trade)
                    trades.append(trade)
                    
                    position_shares = 0
                    entry_price = 0.0
                    entry_date = None
                    trade_high_price = 0.0
                
            # Track Max Drawdown and daily values
            current_portfolio_value = capital + (position_shares * current_price)
            daily_portfolio_values.append(current_portfolio_value)
            
            if current_portfolio_value > peak_capital:
                peak_capital = current_portfolio_value
            else:
                dd = ((peak_capital - current_portfolio_value) / peak_capital) * 100
                if dd > max_dd:
                    max_dd = dd

        # Sell remaining position at the end
        if position_shares > 0:
            exit_price = df.iloc[-1]['Close']
            revenue = position_shares * exit_price
            pnl = revenue - (position_shares * entry_price)
            pnl_percent = (pnl / (position_shares * entry_price)) * 100
            capital += revenue
            trade = BacktestTrade(
                session_id=session.id,
                ticker=ticker,
                entry_date=entry_date,
                exit_date=df.index[-1],
                entry_price=entry_price,
                exit_price=exit_price,
                shares=position_shares,
                pnl=pnl,
                pnl_percent=pnl_percent,
                signal="SELL"
            )
            # Not adding to DB for forced close as a regular completed trade, 
            # but we still want it logged. Let's add it.
            db.add(trade)
            trades.append(trade)

        session.final_capital = capital
        session.total_roi = ((capital - initial_capital) / initial_capital) * 100
        
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        session.win_rate = (winning_trades / len(trades)) * 100 if trades else 0.0
        session.max_drawdown = max_dd
        session.total_trades = len(trades)
        
        session.buy_signals = buy_signals
        session.sell_signals = sell_signals
        
        # Benchmark return
        start_price = df.iloc[50]['Close']
        end_price = df.iloc[-1]['Close']
        session.benchmark_return = ((end_price - start_price) / start_price) * 100
        
        # New Metrics
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        session.profit_factor = float(gross_profit / gross_loss) if gross_loss > 0 else float(gross_profit if gross_profit > 0 else 0)
        
        # Trade duration
        completed_trades_list = [t for t in trades if t.exit_date != df.index[-1] or position_shares == 0] # exclude forced unless it naturally sold on last day
        # Actually count all trades
        session.completed_trades = len(trades)
        
        durations = [(t.exit_date - t.entry_date).days for t in trades]
        session.avg_trade_duration = sum(durations) / len(durations) if durations else 0.0
        
        import numpy as np
        if len(daily_portfolio_values) > 1:
            daily_returns = np.diff(daily_portfolio_values) / daily_portfolio_values[:-1]
            mean_return = np.mean(daily_returns)
            std_return = np.std(daily_returns)
            if std_return > 0:
                session.sharpe_ratio = float((mean_return / std_return) * np.sqrt(252))
            else:
                session.sharpe_ratio = 0.0
        else:
            session.sharpe_ratio = 0.0
        
        db.commit()
    except Exception as e:
        print(f"Error in backtester: {e}")
        db.rollback()
    finally:
        db.close()
        
    return session_id

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    print(f"Running backtest for {ticker}...")
    session_id = run_backtest(ticker)
    print(f"Backtest completed. Session ID: {session_id}")
