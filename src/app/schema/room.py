# schemas/room.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

# ==================== Enums ====================

class RoomStatus(str, Enum):
    available = "available"
    occupied = "occupied"

class PaymentStatus(str, Enum):
    paid = "paid"
    late = "late"
    pending = "pending"
    no_invoice = "no_invoice"

# ==================== Request Schemas ====================

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    price: float = Field(..., gt=0)  # Must be greater than 0
    is_available: Optional[bool] = True  # Default: available for rent

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Room 101",
                "description": "Single room with AC",
                "price": 500.00,
                "is_available": True
            }
        }

class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Room 101 Updated",
                "price": 550.00
            }
        }

class TenantAssign(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, email=True)
    phone: Optional[str] = Field(None, max_length=50)
    id_card: Optional[str] = Field(None, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "012-345-6789",
                "id_card": "ABC123456"
            }
        }

class PaymentRecord(BaseModel):
    amount: float = Field(..., gt=0)
    image: Optional[str] = None  # Receipt image path/URL

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 500.00,
                "image": "receipts/payment_123.jpg"
            }
        }

# ==================== Response Schemas ====================

class TenantInfo(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    check_in_date: datetime
    is_active: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "012-345-6789",
                "id_card": "ABC123456",
                "check_in_date": "2024-01-01T00:00:00",
                "is_active": True
            }
        }

class PaymentInfo(BaseModel):
    id: int
    amount: float
    paid_at: datetime
    image: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "amount": 500.00,
                "paid_at": "2024-01-03T10:30:00",
                "image": "receipts/payment_123.jpg"
            }
        }

class InvoiceInfo(BaseModel):
    id: int
    month: int
    year: int
    amount: float
    amount_paid: float
    status: str
    due_date: date
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "month": 1,
                "year": 2024,
                "amount": 500.00,
                "amount_paid": 500.00,
                "status": "paid",
                "due_date": "2024-01-05",
                "paid_at": "2024-01-03T10:30:00"
            }
        }

class RoomDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool
    status: RoomStatus  # "available" or "occupied"
    tenant: Optional[TenantInfo] = None
    payment_status: Optional[PaymentStatus] = None  # "paid", "late", "pending", "no_invoice"
    amount_due: float = 0.0
    due_date: Optional[date] = None
    latest_payment: Optional[PaymentInfo] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Room 101",
                "description": "Single room with AC",
                "price": 500.00,
                "is_available": False,
                "status": "occupied",
                "tenant": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "payment_status": "paid",
                "amount_due": 0.0,
                "due_date": "2024-01-05",
                "latest_payment": {
                    "id": 1,
                    "amount": 500.00,
                    "paid_at": "2024-01-03T10:30:00"
                },
                "updated_at": "2024-01-03T10:30:00"
            }
        }

class RoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== Pagination & Meta ====================

class SummaryStats(BaseModel):
    available: int = 0
    occupied: int = 0
    late_payments: int = 0
    paid: int = 0

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    summary: Optional[SummaryStats] = None

class RoomListResponse(BaseModel):
    data: List[RoomDetailResponse]
    meta: PaginationMeta

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "meta": {
                    "page": 1,
                    "limit": 10,
                    "total": 50,
                    "summary": {
                        "available": 20,
                        "occupied": 30,
                        "late_payments": 5,
                        "paid": 25
                    }
                }
            }
        }

# ==================== Tenant & Payment Responses ====================

class TenantResponse(BaseModel):
    id: int
    room_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    is_active: bool
    check_in_date: datetime
    check_out_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: float
    image: Optional[str] = None
    status: str
    paid_at: datetime

    class Config:
        from_attributes = True

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

# ==================== API Response Wrappers ====================

class MessageResponse(BaseModel):
    message: str
    data: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation successful",
                "data": {}
            }
        }

class ErrorResponse(BaseModel):
    detail: str
    status_code: int = 400

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Room is already occupied",
                "status_code": 400
            }
        }