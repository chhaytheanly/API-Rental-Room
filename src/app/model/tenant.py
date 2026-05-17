from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Identity
from sqlalchemy.orm import relationship
from datetime import datetime

from src.app.config.base import Base

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, Identity(start=1), primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), unique=True)
    
    # Tenant Info
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    id_card = Column(String(100), nullable=True)
    photo = Column(String(255), nullable=True)  
    
    # Status
    is_active = Column(Boolean, default=True)  # False = moved out
    check_in_date = Column(DateTime, default=datetime.utcnow)
    check_out_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    room = relationship("Room", back_populates="tenant")
    invoices = relationship("Invoice", back_populates="tenant")
