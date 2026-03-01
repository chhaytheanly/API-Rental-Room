from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import Optional
from datetime import date

from ..config.session import get_db
from ..services.invoice import InvoiceService
from ..schema.invoice import (
    InvoiceCreate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    PaginatedInvoiceResponse,
    GenerateAllRequest,
    ApplyLateFeesRequest,
)
from ..model.invoice import Invoice

invoice_router = APIRouter(prefix="/invoices", tags=["Invoices"])

@invoice_router.get("/", response_model=PaginatedInvoiceResponse)
def get_invoices(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    tenant_id: Optional[int] = Query(None),
    room_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Invoice).options(
        selectinload(Invoice.room),
        selectinload(Invoice.tenant),
        selectinload(Invoice.payments),
    )

    if status:
        query = query.filter(Invoice.status == status)
    if month:
        query = query.filter(Invoice.month == month)
    if year:
        query = query.filter(Invoice.year == year)
    if tenant_id:
        query = query.filter(Invoice.tenant_id == tenant_id)
    if room_id:
        query = query.filter(Invoice.room_id == room_id)

    total = query.count()
    invoices = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "data": invoices,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
        },
    }


@invoice_router.post("/generate", response_model=InvoiceResponse)
def generate_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
):
    try:
        for_date_obj = date.fromisoformat(data.for_date)
        check_in_obj = (
            date.fromisoformat(data.check_in_date)
            if data.check_in_date
            else None
        )

        invoice = InvoiceService.generate_invoice(
            db,
            tenant_id=data.tenant_id,
            room_id=data.room_id,
            for_date=for_date_obj,
            is_first_invoice=data.is_first_invoice or False,
            check_in_date=check_in_obj,
        )

        db.commit()
        db.refresh(invoice)
        return invoice

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# GENERATE ALL INVOICES (BODY FIXED)
# ===============================
@invoice_router.post("/generate-all")
def generate_all_invoices(
    data: GenerateAllRequest,
    db: Session = Depends(get_db),
):
    try:
        date_obj = date.fromisoformat(data.for_date) if data.for_date else None
        result = InvoiceService.generate_all_monthly_invoices(db, date_obj)

        db.commit()
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@invoice_router.post("/{invoice_id}/payments", response_model=PaymentResponse)
def record_payment(
    invoice_id: int,
    payment: PaymentCreate,
    db: Session = Depends(get_db),
):
    try:
        result = InvoiceService.record_payment(
            db,
            invoice_id=invoice_id,
            amount=payment.amount,
            image=payment.image,
        )

        db.commit()
        db.refresh(result)
        return result

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.post("/apply-late-fees")
def apply_late_fees(
    data: ApplyLateFeesRequest,
    db: Session = Depends(get_db),
):
    try:
        result = InvoiceService.update_late_invoices(
            db,
            data.grace_period_days,
        )
        db.commit()
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.get("/reports/monthly")
def get_monthly_payment_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
):
    return InvoiceService.get_payment_report(db, month, year)


@invoice_router.get("/tenants/payment-status")
def get_tenants_payment_status(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return InvoiceService.get_all_tenants_payment_status(db, month, year)


@invoice_router.get("/tenants/{tenant_id}/payment-status")
def get_tenant_payment_status(
    tenant_id: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return InvoiceService.get_tenant_payment_status(db, tenant_id, month, year)


@invoice_router.get("/late-payers")
def get_late_payers(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return InvoiceService.get_late_payers(db, month, year)


# ===============================
# GET SINGLE INVOICE (MOVED TO BOTTOM)
# ===============================
@invoice_router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    try:
        return InvoiceService.get_invoice_by_id(db, invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))