"""User profile — bank selection, preferences, simulated wallet."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bank = Column(String(100), nullable=True)             # e.g. "CIB", "Banque Misr"
    preferred_currency = Column(String(10), default="USD")
    simulated_balance = Column(Float, default=1000.0)     # demo wallet
    avatar_url = Column(String(255), nullable=True)
    full_name = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())