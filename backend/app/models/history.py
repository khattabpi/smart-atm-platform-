from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base


class UserHistory(Base):
    __tablename__ = "user_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    atm_id = Column(Integer, ForeignKey("atms.id"), nullable=False, index=True)
    user_lat = Column(Float)
    user_lng = Column(Float)
    used_at = Column(DateTime(timezone=True), server_default=func.now())