from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..config.base import Base

class PaymentStatus(str, enum.Enum):
    completed = "completed"
    failed = "failed"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    
    amount = Column(Float, nullable=False)
    image = Column(String, nullable=True)  # Receipt image
    status = Column(Enum(PaymentStatus), default=PaymentStatus.completed)
    paid_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="payments")