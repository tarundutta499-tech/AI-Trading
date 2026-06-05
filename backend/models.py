from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
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
