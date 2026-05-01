"""
ATM model: stores bank info, location, services and status.
Services and currencies stored as JSON strings for portability between SQLite and Postgres.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class ATM(Base):
    __tablename__ = "atms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    bank = Column(String(100), nullable=False, index=True)
    address = Column(String(255))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Services
    cash_withdrawal = Column(Boolean, default=True)
    cash_deposit = Column(Boolean, default=False)
    ewallet_support = Column(Boolean, default=False)
    currency_exchange = Column(Boolean, default=False)
    supported_currencies = Column(JSON, default=list)  # e.g. ["USD","EUR"]

    # Status
    is_working = Column(Boolean, default=True)
    rating = Column(Float, default=4.0)  # 0-5
    reliability_score = Column(Float, default=1.0)  # adjusts via reports

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())