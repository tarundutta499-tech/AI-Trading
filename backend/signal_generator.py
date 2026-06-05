import pandas as pd
import numpy as np
import json

def dynamic_weighting(scores, standard_weights):
    """
    scores: dict of {factor_name: score_value_or_none}
    standard_weights: dict of {factor_name: weight_percentage}
    Returns: Final composite score
    """
    available_weights_sum = sum(standard_weights[k] for k, v in scores.items() if v is not None)
    if available_weights_sum == 0:
        return 0
        
    composite = 0
    for k, v in scores.items():
        if v is not None:
            adjusted_weight = standard_weights[k] / available_weights_sum
            composite += v * adjusted_weight
            
    return composite

def generate_signals(ticker, df, fundamentals, sentiment_stats, market_df, sector_df):
    if df is None or len(df) == 0:
        return None
        
    latest = df.iloc[-1]
    reasons = []
    warnings = []
    
    # 1. TECH SCORE (Max 100)
    tech_score = 0
    tech_details = {}
    
    rsi = latest.get('RSI', 50)
    if pd.notna(rsi):
        tech_details['rsi_score'] = rsi
        if rsi < 35: tech_score += 20; reasons.append(f"RSI Oversold ({rsi:.1f})")
        elif rsi > 70: warnings.append(f"RSI Overbought ({rsi:.1f})")
        elif rsi > 50: tech_score += 10
            
    macd = latest.get('MACD', 0)
    macd_signal = latest.get('MACD_Signal', 0)
    if pd.notna(macd) and pd.notna(macd_signal):
        tech_details['macd_score'] = macd
        if macd > macd_signal: 
            tech_score += 15
            reasons.append("MACD Bullish Crossover")
        else:
            warnings.append("MACD Bearish")
            
    ema_50 = latest.get('EMA_50', latest['Close'])
    if pd.notna(ema_50):
        tech_details['moving_average_score'] = ema_50
        if latest['Close'] > ema_50: 
            tech_score += 15
            reasons.append("Price above EMA-50")
            
    vol_sma = latest.get('Vol_SMA_20', 0)
    vol = latest.get('Volume', 0)
    if pd.notna(vol_sma) and pd.notna(vol) and vol_sma > 0:
        vol_pct = ((vol - vol_sma) / vol_sma) * 100
        tech_details['volume_score'] = vol_pct
        if vol_pct > 20 and len(df) > 1 and latest['Close'] > df.iloc[-2]['Close']:
            tech_score += 15
            reasons.append(f"Volume {vol_pct:.0f}% above avg on up-day")
            
    bb_upper = latest.get('BB_Upper', 0)
    bb_lower = latest.get('BB_Lower', 0)
    if pd.notna(bb_upper) and latest['Close'] >= bb_upper:
        tech_score += 10
        reasons.append("Bollinger Upper Band Breakout")
    elif pd.notna(bb_lower) and latest['Close'] <= bb_lower:
        warnings.append("Bollinger Lower Band Breakdown")
    tech_details['bollinger_score'] = bb_upper if pd.notna(bb_upper) else 0
        
    adx = latest.get('ADX', 0)
    tech_details['adx_score'] = adx if pd.notna(adx) else 0
    if pd.notna(adx) and adx > 25:
        tech_score += 10
        reasons.append(f"Strong Trend (ADX {adx:.1f})")
        
    high_52 = latest.get('High_52W', 0)
    tech_details['breakout_score'] = high_52 if pd.notna(high_52) else 0
    if pd.notna(high_52) and high_52 > 0 and latest['Close'] >= high_52 * 0.95:
        tech_score += 15
        reasons.append("Approaching/Crossing 52-Week High")
        
    tech_score = min(100, tech_score)
    
    # 2. FUND SCORE
    fund_score = None
    if fundamentals and fundamentals.get("pe_ratio") is not None:
        fund_score = 0
        pe = fundamentals.get('pe_ratio')
        if pe and 0 < pe < 25: fund_score += 40; reasons.append("Attractive P/E")
        elif pe and pe >= 25: fund_score += 10; warnings.append("High P/E")
            
        eps = fundamentals.get('eps_growth')
        if eps and eps > 0: fund_score += 30; reasons.append("Positive EPS Growth")
        elif eps and eps < 0: warnings.append("Negative EPS Growth")
            
        debt = fundamentals.get('debt_to_equity')
        if debt and debt < 100: fund_score += 30; reasons.append("Low Debt/Equity")
    elif fundamentals:
        warnings.append("Fundamental data unavailable (N/A)")
        
    # 3. SENT SCORE
    sent_score = sentiment_stats['sentiment_score']
    if sent_score > 60: reasons.append("Positive News Sentiment")
    elif sent_score < 40: warnings.append("Negative News Sentiment")
    
    # 4. RISK SCORE
    drawdown = 0
    if len(df) > 200:
        max_high = df['High'].rolling(252, min_periods=1).max()
        dd = ((df['Close'] - max_high) / max_high).min() * 100
        drawdown = abs(dd)
    
    volatility = df['Daily_Return'].std() * np.sqrt(252) * 100 if 'Daily_Return' in df.columns else 20
    beta = fundamentals.get("beta", 1.0) if fundamentals else 1.0
    beta = beta if beta is not None else 1.0
    
    r_score = 100
    if volatility > 40: r_score -= 30; warnings.append("High Volatility")
    elif volatility > 25: r_score -= 15
    
    if beta > 1.5: r_score -= 20; warnings.append("High Beta (> 1.5)")
    if drawdown > 30: r_score -= 20; warnings.append(f"Large Drawdown ({drawdown:.1f}%)")
    
    risk_score = max(0, r_score)
    
    # 5. MARKET SCORE
    market_score = 50
    if market_df is not None and len(market_df) > 50:
        m_latest = market_df.iloc[-1]
        m_ema50 = m_latest.get('EMA_50', m_latest['Close'])
        if pd.notna(m_ema50) and m_latest['Close'] > m_ema50:
            market_score += 20
            reasons.append("Market in Uptrend")
        else:
            market_score -= 20
            warnings.append("Market in Downtrend")
            
    # 6. SECTOR SCORE
    sector_score = 50
    if sector_df is not None and len(sector_df) > 50:
        s_latest = sector_df.iloc[-1]
        s_ema50 = s_latest.get('EMA_50', s_latest['Close'])
        if pd.notna(s_ema50) and s_latest['Close'] > s_ema50:
            sector_score += 20
            reasons.append("Sector Outperforming")
        else:
            sector_score -= 20
            warnings.append("Sector Underperforming")
            
    # DYNAMIC WEIGHTING
    scores = {
        'TECH': tech_score,
        'FUND': fund_score,
        'SENT': sent_score,
        'RISK': risk_score,
        'MARKET': market_score,
        'SECTOR': sector_score
    }
    
    weights = {
        'TECH': 0.30,
        'FUND': 0.25,
        'SENT': 0.15,
        'RISK': 0.15,
        'MARKET': 0.10,
        'SECTOR': 0.05
    }
    
    composite_score = dynamic_weighting(scores, weights)
    
    # Earnings check
    if fundamentals and fundamentals.get("earnings_in_3_days"):
        warnings.append("Earnings in <3 Days (Risk)")
        if composite_score > 65:
            composite_score = 64
            
    if composite_score > 65: signal = "BUY"
    elif composite_score >= 40: signal = "HOLD"
    else: signal = "SELL"
    
    # Confidence Score
    conf = 100
    if fund_score is None: conf -= 15
    if market_df is None: conf -= 5
    if sector_df is None: conf -= 5
    if sent_score == 50 and sentiment_stats.get('positive_articles', 0) == 0: conf -= 10
    
    if fund_score is not None:
        diff = abs(tech_score - fund_score)
        if diff > 40:
            conf -= 15
            warnings.append("Tech/Fund Disagreement")
            
    confidence_score = max(0, min(100, conf))
    
    def convert_numpy(obj):
        if isinstance(obj, np.generic):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        return obj
        
    tech_details = convert_numpy(tech_details)
    
    return {
        "ticker": ticker,
        "score": float(composite_score),
        "signal": signal,
        "technical_score": float(tech_score),
        "fundamental_score": float(fund_score) if fund_score is not None else None,
        "sentiment_score": float(sent_score),
        "risk_score": float(risk_score),
        "market_score": float(market_score),
        "sector_score": float(sector_score),
        "confidence_score": float(confidence_score),
        "current_price": float(latest['Close']),
        "gap_pct": float(latest.get('Gap_Pct', 0) if pd.notna(latest.get('Gap_Pct')) else 0),
        "reasons": json.dumps(reasons),
        "warnings": json.dumps(warnings),
        "tech_details": json.dumps(tech_details)
    }
