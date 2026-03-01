from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum

class InvoiceStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    late = "late"
    no_invoice = "no_invoice"


class PaymentStatus(str, Enum):
    completed = "completed"
    pending = "pending"
    failed = "failed"


# ===== REQUEST SCHEMAS =====

class InvoiceCreate(BaseModel):
    tenant_id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)
    for_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # ISO date string
    is_first_invoice: Optional[bool] = False
    check_in_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    
    @field_validator('for_date', 'check_in_date')
    @classmethod
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in ISO format: YYYY-MM-DD")


class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    image: Optional[str] = None  # URL or base64 of receipt


class InvoiceFilterParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    status: Optional[InvoiceStatus] = None
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2000)
    tenant_id: Optional[int] = None
    room_id: Optional[int] = None


# ===== RESPONSE SCHEMAS =====

class TenantSummary(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]

class RoomSummary(BaseModel):
    id: int
    name: str
    price: float

class PaymentSummary(BaseModel):
    id: int
    amount: float
    image: Optional[str]
    status: PaymentStatus
    paid_at: Optional[datetime] = None

class InvoiceResponse(BaseModel):
    id: int
    room_id: int
    tenant_id: int
    month: int
    year: int
    amount: float
    amount_paid: float
    due_date: date
    status: InvoiceStatus
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    # Optional nested data (use with selectinload)
    room: Optional[RoomSummary] = None
    tenant: Optional[TenantSummary] = None
    payments: Optional[list[PaymentSummary]] = None

    
    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: float
    image: Optional[str]
    status: PaymentStatus
    paid_at: datetime
    
    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import List, Optional

class MetaResponse(BaseModel):
    page: int
    limit: int
    total: int

class PaginatedInvoiceResponse(BaseModel):
    data: List["InvoiceResponse"]
    meta: MetaResponse


class GenerateAllRequest(BaseModel):
    for_date: Optional[str] = None


class ApplyLateFeesRequest(BaseModel):
    grace_period_days: int = 3