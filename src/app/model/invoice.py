from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.app.config.base import Base

class InvoiceStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    late = "late"

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Billing Period
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)   # 2024
    
    amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    
    due_date = Column(Date, nullable=False)  # e.g., 5th of month
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.pending)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    room = relationship("Room", back_populates="invoices")
    tenant = relationship("Tenant", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete")