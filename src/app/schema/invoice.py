
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class InvoiceResponse(BaseModel):
    id: int
    room_id: int
    tenant_id: int
    month: int
    year: int
    amount: float
    amount_paid: float
    status: str
    due_date: date
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True