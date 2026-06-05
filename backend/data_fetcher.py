import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Global cache for index data during an analysis cycle
index_cache = {}

def get_index_data(index_ticker):
    if index_ticker in index_cache:
        return index_cache[index_ticker]
        
    try:
        ticker = yf.Ticker(index_ticker)
        df = ticker.history(period="1y", interval="1d")
        index_cache[index_ticker] = df
        return df
    except Exception as e:
        print(f"Error fetching index data for {index_ticker}: {e}")
        return None

def clear_index_cache():
    global index_cache
    index_cache = {}

def get_stock_data(ticker_symbol, period="1y", interval="1d"):
    """
    Fetches OHLCV data for a given ticker.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None

def get_fundamentals(ticker_symbol):
    """
    Fetches fundamental data for scoring and risk management.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # We need PE, EPS growth, debt to equity, and upcoming earnings
        pe_ratio = info.get("trailingPE", None)
        eps_growth = info.get("earningsQuarterlyGrowth", 0)  # sometimes missing
        debt_to_equity = info.get("debtToEquity", None)
        
        # Check earnings date
        earnings_date_str = None
        earnings_in_3_days = False
        
        calendar = ticker.calendar
        if calendar is not None and not calendar.empty:
            try:
                if 'Earnings Date' in calendar.index:
                    dates = calendar.loc['Earnings Date'].values
                    if len(dates) > 0 and pd.notnull(dates[0]):
                        next_earnings = pd.to_datetime(dates[0]).tz_localize(None)
                        days_to_earnings = (next_earnings - datetime.now()).days
                        if 0 <= days_to_earnings <= 3:
                            earnings_in_3_days = True
            except Exception as ex:
                print(f"Error parsing earnings for {ticker_symbol}: {ex}")

        return {
            "pe_ratio": pe_ratio,
            "eps_growth": eps_growth,
            "debt_to_equity": debt_to_equity,
            "earnings_in_3_days": earnings_in_3_days,
            "sector": info.get("sector", "Unknown"),
            "current_price": info.get("currentPrice", info.get("previousClose", 0)),
            "beta": info.get("beta", None)
        }
    except Exception as e:
        print(f"Error fetching fundamentals for {ticker_symbol}: {e}")
        return None
