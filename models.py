from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class TradeCall(Base):
    """Store daily trade recommendations"""
    __tablename__ = 'trade_calls'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False)
    call_date = Column(DateTime, default=datetime.now, nullable=False)
    recommendation = Column(String(10), nullable=False)  # BUY/SELL
    entry_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    stop_loss = Column(Float)
    reasoning = Column(Text)
    market_state = Column(String(10))  # UP/DOWN/FLAT
    conviction_score = Column(Integer)  # 0-100
    potential_gain_percent = Column(Float)
    
    # Relationship to performance
    performance = relationship("TradePerformance", back_populates="trade_call", uselist=False)
    
    def __repr__(self):
        return f"<TradeCall {self.symbol} {self.recommendation} @ {self.entry_price}>"


class TradePerformance(Base):
    """Track actual performance of trades"""
    __tablename__ = 'trade_performance'
    
    id = Column(Integer, primary_key=True)
    trade_call_id = Column(Integer, ForeignKey('trade_calls.id'), nullable=False)
    actual_entry_price = Column(Float)
    actual_exit_price = Column(Float)
    exit_time = Column(DateTime)
    gain_loss_percent = Column(Float)
    gain_loss_amount = Column(Float)
    status = Column(String(20), default='OPEN')  # OPEN/CLOSED/CANCELLED
    notes = Column(Text)
    
    # Relationship
    trade_call = relationship("TradeCall", back_populates="performance")
    
    def __repr__(self):
        return f"<TradePerformance {self.status} {self.gain_loss_percent}%>"


class MarketIndicators(Base):
    """Store daily market ratios and indicators"""
    __tablename__ = 'market_indicators'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now, nullable=False, unique=True)
    gold_price = Column(Float)
    nifty_value = Column(Float)
    gold_nifty_ratio = Column(Float)
    vix = Column(Float)
    put_call_ratio = Column(Float)
    fii_net = Column(Float)  # FII net buy/sell in crores
    dii_net = Column(Float)  # DII net buy/sell in crores
    nifty_change_percent = Column(Float)
    market_sentiment = Column(String(20))  # BULLISH/BEARISH/NEUTRAL
    
    def __repr__(self):
        return f"<MarketIndicators {self.date.date()} Gold/Nifty: {self.gold_nifty_ratio}>"


class ConvictionInsights(Base):
    """Store transcript analysis and conviction factors"""
    __tablename__ = 'conviction_insights'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False)
    analysis_date = Column(DateTime, default=datetime.now, nullable=False)
    quarter = Column(String(10))  # e.g., 'Q3 FY26'
    transcript_summary = Column(Text)
    key_insights = Column(JSON)  # List of key points
    conviction_factors = Column(JSON)  # Dict with factors and scores
    overall_score = Column(Integer)  # 0-100
    sentiment = Column(String(20))  # POSITIVE/NEUTRAL/NEGATIVE
    revenue_growth = Column(Float)
    margin_trend = Column(String(20))  # EXPANDING/STABLE/CONTRACTING
    order_book_strength = Column(String(20))  # STRONG/MODERATE/WEAK
    full_analysis = Column(JSON)  # Store the complete 15-section report
    
    def __repr__(self):
        return f"<ConvictionInsights {self.symbol} Score: {self.overall_score}>"


# Database connection and session management
def get_database_url():
    """Get PostgreSQL database URL from environment or use default"""
    return os.getenv('DATABASE_URL', 'postgresql://localhost/beInformed')


def init_db():
    """Initialize database and create all tables"""
    engine = create_engine(get_database_url(), echo=True)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get a new database session"""
    engine = create_engine(get_database_url(), echo=False)
    Session = sessionmaker(bind=engine)
    return Session()
