import pandas as pd
import numpy as np

def calculate_indicators(df):
    if df is None or len(df) < 50:
        return None
    
    df = df.copy()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # EMA 20 & 50
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # MACD (12, 26, 9)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Gap detection
    df['Gap_Pct'] = ((df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)) * 100
    
    # Volume 20-day SMA
    if 'Volume' in df.columns:
        df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
    
    # Bollinger Bands (20, 2)
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Mid'] + (2 * std)
    df['BB_Lower'] = df['BB_Mid'] - (2 * std)
    
    # ADX (14) - manual
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = minus_dm.abs()
    
    plus_dm_series = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
    minus_dm_series = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.rolling(14).mean()
    plus_di = 100 * (pd.Series(plus_dm_series, index=df.index).rolling(14).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm_series, index=df.index).rolling(14).mean() / atr)
    
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    df['ADX'] = dx.rolling(14).mean()
    
    # 52-Week High (252 trading days)
    df['High_52W'] = df['High'].rolling(window=252).max()
    
    # Volatility / Returns for Risk score
    df['Daily_Return'] = df['Close'].pct_change()
    
    return df
