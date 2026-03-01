from sqlalchemy.orm import Session, selectinload
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List, Optional
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
        
        if remaining_days <= 0:
            return room_price  # Full month if check-in was before month start
        
        return round((room_price / days_in_month) * remaining_days, 2)
    
    @staticmethod
    def generate_invoice(
        db: Session, 
        tenant_id: int, 
        room_id: int, 
        for_date: date, 
        is_first_invoice: bool = False, 
        check_in_date: date = None
    ) -> Invoice:
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
        
        active_tenants = db.query(Tenant).filter(
            Tenant.is_active.is_(True),
            Tenant.room_id.isnot(None)
        ).all()
        
        created = 0
        skipped = 0
        failed = 0
        
        for tenant in active_tenants:
            try:
                existing = db.query(Invoice).filter(
                    Invoice.tenant_id == tenant.id,
                    Invoice.year == for_date.year,
                    Invoice.month == for_date.month
                ).first()
                
                if existing:
                    skipped += 1
                else:
                    invoice = InvoiceService.generate_invoice(
                        db, 
                        tenant.id, 
                        tenant.room_id, 
                        for_date,
                        is_first_invoice=False
                    )
                    created += 1
            except Exception as e:
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
            if invoice.status != InvoiceStatus.late:
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

        remaining_balance = invoice.amount - invoice.amount_paid
        if amount > remaining_balance:
            amount = remaining_balance
        
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
        elif invoice.due_date < date.today() and invoice.status != InvoiceStatus.late:
            invoice.status = InvoiceStatus.late
        
        db.add(payment)
        return payment
    
    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice:
        """Get single invoice with details"""

        invoice = db.query(Invoice).options(
            selectinload(Invoice.room),
            selectinload(Invoice.tenant),
            selectinload(Invoice.payments)
        ).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise ValueError("Invoice not found")
        return invoice
    
    @staticmethod
    def get_payment_report(db: Session, month: int, year: int) -> Dict[str, Any]:
        """Generate payment report for a specific month"""

        invoices = db.query(Invoice).options(
            selectinload(Invoice.room),
            selectinload(Invoice.tenant)
        ).filter(
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
    
    @staticmethod
    def get_tenant_payment_status(
        db: Session, 
        tenant_id: int, 
        month: int = None, 
        year: int = None
    ) -> Dict[str, Any]:
        """
        Get payment status for a specific tenant
        Returns current month status by default
        """
        # Default to current month
        if month is None or year is None:
            today = date.today()
            month = today.month
            year = today.year
        
        # Get tenant's invoice for the month
        invoice = db.query(Invoice).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.month == month,
            Invoice.year == year
        ).first()
        
        if not invoice:
            return {
                "tenant_id": tenant_id,
                "month": month,
                "year": year,
                "status": "no_invoice",
                "amount_due": 0,
                "amount_paid": 0,
                "total_amount": 0,
                "due_date": None,
                "paid_at": None,
                "invoice_id": None
            }
        
        return {
            "tenant_id": tenant_id,
            "month": month,
            "year": year,
            "status": invoice.status.value,
            "amount_due": round(invoice.amount - invoice.amount_paid, 2),
            "amount_paid": float(invoice.amount_paid),
            "total_amount": float(invoice.amount),
            "due_date": invoice.due_date.isoformat(),
            "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
            "invoice_id": invoice.id
        }
    
    @staticmethod
    def get_all_tenants_payment_status(
        db: Session, 
        month: int = None, 
        year: int = None
    ) -> Dict[str, Any]:
        """
        Get payment status for ALL active tenants
        """
        # Default to current month
        if month is None or year is None:
            today = date.today()
            month = today.month
            year = today.year
        
        # Get all active tenants with their invoices
        tenants = db.query(Tenant).filter(
            Tenant.is_active.is_(True)
        ).options(
            selectinload(Tenant.invoices)
        ).all()
        
        results = []
        for tenant in tenants:
            status = InvoiceService.get_tenant_payment_status(db, tenant.id, month, year)
            status["tenant_name"] = tenant.name
            status["tenant_email"] = tenant.email
            status["tenant_phone"] = tenant.phone
            status["room_id"] = tenant.room_id
            results.append(status)
        
        # Summary stats
        summary = {
            "total_tenants": len(results),
            "paid": sum(1 for r in results if r["status"] == "paid"),
            "pending": sum(1 for r in results if r["status"] == "pending"),
            "late": sum(1 for r in results if r["status"] == "late"),
            "no_invoice": sum(1 for r in results if r["status"] == "no_invoice"),
            "collection_rate": round(
                (sum(1 for r in results if r["status"] == "paid") / len(results) * 100) 
                if results else 0, 2
            )
        }
        
        return {
            "month": month,
            "year": year,
            "summary": summary,
            "data": results
        }
    
    @staticmethod
    def get_late_payers(db: Session, month: int = None, year: int = None) -> List[Dict[str, Any]]:
        """
        Get list of tenants with late payments
        """
        if month is None or year is None:
            today = date.today()
            month = today.month
            year = today.year
        
        late_invoices = db.query(Invoice).options(
            selectinload(Invoice.tenant),
            selectinload(Invoice.room)
        ).filter(
            Invoice.status == InvoiceStatus.late,
            Invoice.month == month,
            Invoice.year == year
        ).all()
        
        return [
            {
                "invoice_id": inv.id,
                "tenant_id": inv.tenant_id,
                "tenant_name": inv.tenant.name if inv.tenant else "Unknown",
                "tenant_email": inv.tenant.email if inv.tenant else None,
                "room_name": inv.room.name if inv.room else "Unknown",
                "amount_due": float(inv.amount - inv.amount_paid),
                "due_date": inv.due_date.isoformat(),
                "days_overdue": (date.today() - inv.due_date).days
            }
            for inv in late_invoices
        ]