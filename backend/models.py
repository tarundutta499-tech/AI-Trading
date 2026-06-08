from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Date
from datetime import datetime, timezone
from database import Base

class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    entry_price = Column(Float)
    current_price = Column(Float)
    shares = Column(Integer)
    stop_loss = Column(Float)
    high_risk = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SignalHistory(Base):
    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    signal = Column(String) # BUY, SELL, HOLD
    score = Column(Float)
    technical_score = Column(Float, nullable=True)
    fundamental_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    market_score = Column(Float, nullable=True)
    sector_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    reasons = Column(String, nullable=True) # JSON string
    warnings = Column(String, nullable=True) # JSON string
    tech_details = Column(String, nullable=True) # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

class MarketNews(Base):
    __tablename__ = "market_news"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    title = Column(String)
    link = Column(String)
    published_at = Column(String) # ISO 8601 string
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BacktestSession(Base):
    __tablename__ = "backtest_sessions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_capital = Column(Float)
    final_capital = Column(Float)
    total_roi = Column(Float)
    win_rate = Column(Float)
    max_drawdown = Column(Float)
    total_trades = Column(Integer)
    buy_signals = Column(Integer, default=0)
    sell_signals = Column(Integer, default=0)
    completed_trades = Column(Integer, default=0)
    avg_trade_duration = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    benchmark_return = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BacktestTrade(Base):
    __tablename__ = "backtest_trades"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    ticker = Column(String)
    entry_date = Column(DateTime)
    exit_date = Column(DateTime, nullable=True)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    shares = Column(Integer)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    signal = Column(String) # BUY / SELL / STOP_LOSS

class GoldenScreenerResult(Base):
    __tablename__ = "golden_screener_results"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    ticker = Column(String, index=True)
    
    # Passing checks
    beats_benchmark = Column(Boolean)
    profit_factor_pass = Column(Boolean)
    win_rate_pass = Column(Boolean)
    drawdown_pass = Column(Boolean)
    
    # 5-Year Metrics
    profit_factor = Column(Float)
    win_rate = Column(Float)
    max_drawdown = Column(Float)
    strategy_return = Column(Float)
    benchmark_return = Column(Float)

class IntradaySignal(Base):
    __tablename__ = "intraday_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    signal = Column(String)  # BUY, SELL, HOLD
    score = Column(Float)
    current_price = Column(Float)
    vwap = Column(Float)
    rsi_5m = Column(Float)
    macd_histogram = Column(Float)
    reasons = Column(String) # JSON
    warnings = Column(String) # JSON
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
