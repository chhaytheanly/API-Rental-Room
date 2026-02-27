import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, Float, String
from sqlalchemy.orm import relationship
from ..config.base import Base


class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    tenant = relationship("Tenant", back_populates="room", uselist=False)
    invoices = relationship("Invoice", back_populates="room")