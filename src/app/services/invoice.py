from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import Dict, Any
import calendar
from ..model.invoice import Invoice, InvoiceStatus
from ..model.room import Room
from ..model.tenant import Tenant
from ..model.payment import Payment, PaymentStatus

class InvoiceService:
    
    @staticmethod
    def _calculate_prorated_amount(room_price: float, check_in_date: date, invoice_date: date) -> float:
        """Calculate prorated rent for partial month"""
        days_in_month = calendar.monthrange(invoice_date.year, invoice_date.month)[1]
        remaining_days = days_in_month - check_in_date.day + 1
        return (room_price / days_in_month) * remaining_days
    
    @staticmethod
    def generate_invoice(db: Session, tenant_id: int, room_id: int, for_date: date, is_first_invoice: bool = False, check_in_date: date = None) -> Invoice:
        """
        Generate monthly invoice for a tenant
        """
        # Idempotency check
        existing = db.query(Invoice).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.year == for_date.year,
            Invoice.month == for_date.month
        ).first()
        
        if existing:
            return existing
        
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        # Calculate amount (apply proration if needed)
        amount = room.price
        
        if is_first_invoice and check_in_date:
            amount = InvoiceService._calculate_prorated_amount(
                room.price, check_in_date, for_date
            )
        
        invoice = Invoice(
            room_id=room_id,
            tenant_id=tenant_id,
            month=for_date.month,
            year=for_date.year,
            amount=amount,
            due_date=for_date.replace(day=5),
            status=InvoiceStatus.pending,
            amount_paid=0
        )
        
        db.add(invoice)
        return invoice
    
    @staticmethod
    def generate_all_monthly_invoices(db: Session, for_date: date = None) -> Dict[str, Any]:
        """
        Generate invoices for ALL active tenants
        """
        if for_date is None:
            for_date = date.today()
        
        active_tenants = db.query(Tenant).filter(Tenant.is_active.is_(True)).all()
        
        created = 0
        skipped = 0
        failed = 0
        
        for tenant in active_tenants:
            try:
                invoice = InvoiceService.generate_invoice(
                    db, 
                    tenant.id, 
                    tenant.room_id, 
                    for_date,
                    is_first_invoice=False
                )
                if invoice.id is None:
                    created += 1
                else:
                    skipped += 1
            except Exception:
                failed += 1
                continue

        return {
            "invoices_created": created, 
            "invoices_skipped": skipped,
            "invoices_failed": failed,
            "month": for_date.isoformat()
        }
    
    @staticmethod
    def update_late_invoices(db: Session, grace_period_days: int = 3) -> Dict[str, int]:
        """
        Mark invoices as late and apply late fee
        """
        today = date.today()
        late_threshold = today - relativedelta(days=grace_period_days)
        
        overdue = db.query(Invoice).filter(
            Invoice.status == InvoiceStatus.pending,
            Invoice.due_date < late_threshold
        ).all()
        
        marked_late = 0
        for invoice in overdue:
            invoice.status = InvoiceStatus.late
            late_fee = invoice.amount * 0.05 
            invoice.amount += late_fee
            marked_late += 1
        return {"marked_late": marked_late}
    
    @staticmethod
    def record_payment(
        db: Session, 
        invoice_id: int, 
        amount: float, 
        image: str = None
    ) -> Payment:
        """
        Record payment and update invoice status
        """
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0")
        
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            image=image,
            status=PaymentStatus.completed,
            paid_at=datetime.now(timezone.utc)
        )
        
        invoice.amount_paid += amount
        
        if invoice.amount_paid >= invoice.amount:
            invoice.status = InvoiceStatus.paid
            invoice.paid_at = datetime.now(timezone.utc)
        elif invoice.due_date < date.today():
            invoice.status = InvoiceStatus.late
        
        db.add(payment)
        return payment
    
    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice:
        """Get single invoice with details"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        return invoice
    
    @staticmethod
    def get_payment_report(db: Session, month: int, year: int) -> Dict[str, Any]:
        """Generate payment report for a specific month"""
        invoices = db.query(Invoice).filter(
            Invoice.month == month,
            Invoice.year == year
        ).all()
        
        if not invoices:
            return {
                "month": month,
                "year": year,
                "summary": {
                    "total_invoices": 0,
                    "total_expected": 0,
                    "total_received": 0,
                    "collection_rate": 0,
                    "paid_count": 0,
                    "pending_count": 0,
                    "late_count": 0
                },
                "data": []
            }
        
        total_expected = sum(inv.amount for inv in invoices)
        total_received = sum(inv.amount_paid for inv in invoices)
        paid_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.paid)
        pending_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.pending)
        late_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.late)
        
        report_data = []
        for inv in invoices:
            report_data.append({
                "invoice_id": inv.id,
                "room_name": inv.room.name if inv.room else "N/A",
                "tenant_name": inv.tenant.name if inv.tenant else "N/A",
                "amount": float(inv.amount),
                "amount_paid": float(inv.amount_paid),
                "status": inv.status.value,
                "due_date": inv.due_date.isoformat(),
                "paid_at": inv.paid_at.isoformat() if inv.paid_at else None
            })
        
        return {
            "month": month,
            "year": year,
            "summary": {
                "total_invoices": len(invoices),
                "total_expected": float(total_expected),
                "total_received": float(total_received),
                "collection_rate": round((total_received / total_expected * 100), 2) if total_expected > 0 else 0,
                "paid_count": paid_count,
                "pending_count": pending_count,
                "late_count": late_count
            },
            "data": report_data
        }