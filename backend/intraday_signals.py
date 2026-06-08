import pandas as pd
import numpy as np
import json

def calculate_intraday_indicators(df):
    if df.empty or len(df) < 50:
        return df
        
    df = df.copy()
    
    # VWAP
    # Normally VWAP resets daily, but for a continuous 5m feed across days, 
    # we can approximate or calculate it per day.
    # Group by date and calculate VWAP
    df['Date'] = df.index.date
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['Vol_x_TP'] = df['Volume'] * df['Typical_Price']
    
    df['Cumulative_Vol'] = df.groupby('Date')['Volume'].cumsum()
    df['Cumulative_Vol_x_TP'] = df.groupby('Date')['Vol_x_TP'].cumsum()
    df['VWAP'] = df['Cumulative_Vol_x_TP'] / df['Cumulative_Vol']
    
    # RSI 5m (using 14 periods)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_5m'] = 100 - (100 / (1 + rs))
    
    # MACD 5m (fast=12, slow=26, signal=9)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # EMA 9 and EMA 21 for rapid crossovers
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # ATR for stop loss calculation
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR_14'] = true_range.rolling(14).mean()
    
    return df

def generate_intraday_signals(ticker, df):
    if df is None or len(df) < 50:
        return None
        
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    reasons = []
    warnings = []
    
    score = 50
    signal = "HOLD"
    
    # 1. VWAP Check
    vwap = latest.get('VWAP', 0)
    current_price = latest['Close']
    if pd.notna(vwap) and vwap > 0:
        if current_price > vwap:
            score += 15
            reasons.append("Price above VWAP (Bullish)")
        else:
            score -= 15
            warnings.append("Price below VWAP (Bearish)")
            
    # 2. RSI Check
    rsi = latest.get('RSI_5m', 50)
    if pd.notna(rsi):
        if rsi < 30:
            score += 20
            reasons.append(f"Oversold (RSI: {rsi:.1f})")
        elif rsi > 70:
            score -= 20
            warnings.append(f"Overbought (RSI: {rsi:.1f})")
            
    # 3. MACD Check
    macd_hist = latest.get('MACD_Hist', 0)
    prev_macd_hist = prev.get('MACD_Hist', 0)
    if pd.notna(macd_hist) and pd.notna(prev_macd_hist):
        if macd_hist > 0 and prev_macd_hist <= 0:
            score += 20
            reasons.append("MACD Bullish Crossover")
        elif macd_hist < 0 and prev_macd_hist >= 0:
            score -= 20
            warnings.append("MACD Bearish Crossover")
        elif macd_hist > 0:
            score += 5
        elif macd_hist < 0:
            score -= 5
            
    # 4. EMA Crossover
    ema9 = latest.get('EMA_9', 0)
    ema21 = latest.get('EMA_21', 0)
    prev_ema9 = prev.get('EMA_9', 0)
    prev_ema21 = prev.get('EMA_21', 0)
    
    if pd.notna(ema9) and pd.notna(ema21):
        if ema9 > ema21 and prev_ema9 <= prev_ema21:
            score += 15
            reasons.append("EMA 9 crossing above EMA 21")
        elif ema9 < ema21 and prev_ema9 >= prev_ema21:
            score -= 15
            warnings.append("EMA 9 crossing below EMA 21")
            
    score = max(0, min(100, score))
    
    if score >= 75:
        signal = "BUY"
    elif score <= 25:
        signal = "SELL"
        
    return {
        "ticker": ticker,
        "signal": signal,
        "score": float(score),
        "current_price": float(current_price),
        "vwap": float(vwap) if pd.notna(vwap) else None,
        "rsi_5m": float(rsi) if pd.notna(rsi) else None,
        "macd_histogram": float(macd_hist) if pd.notna(macd_hist) else None,
        "reasons": json.dumps(reasons),
        "warnings": json.dumps(warnings)
    }
