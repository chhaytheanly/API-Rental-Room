# services/invoice_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ..model.invoice import Invoice, InvoiceStatus
from ..model.room import Room
from ..model.tenant import Tenant
from ..model.payment import Payment, PaymentStatus

class InvoiceService:
    
    @staticmethod
    def generate_invoice(db: Session, tenant_id: int, room_id: int, for_date: date):
        """
        Generate monthly invoice for a tenant
        """
        # Check if invoice already exists
        existing = db.query(Invoice).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.year == for_date.year,
            Invoice.month == for_date.month
        ).first()
        
        if existing:
            return existing
        
        # Create new invoice
        invoice = Invoice(
            room_id=room_id,
            tenant_id=tenant_id,
            month=for_date.month,
            year=for_date.year,
            amount=db.query(Room).filter(Room.id == room_id).first().price,
            due_date=for_date.replace(day=5),  # Due on 5th
            status=InvoiceStatus.pending
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    def generate_all_monthly_invoices(db: Session, for_date: date = None):
        """
        Generate invoices for ALL active tenants (run monthly via cron)
        """
        if for_date is None:
            for_date = date.today()
        
        # Get all active tenants
        active_tenants = db.query(Tenant).filter(
            Tenant.is_active == True
        ).all()
        
        created = 0
        for tenant in active_tenants:
            try:
                InvoiceService.generate_invoice(db, tenant.id, tenant.room_id, for_date)
                created += 1
            except:
                continue
        
        db.commit()
        return {"invoices_created": created, "month": for_date.isoformat()}
    
    @staticmethod
    def update_late_invoices(db: Session, grace_period_days: int = 3):
        """
        Mark invoices as late (run daily via cron)
        """
        today = date.today()
        late_threshold = today - relativedelta(days=grace_period_days)
        
        overdue = db.query(Invoice).filter(
            Invoice.status == InvoiceStatus.pending,
            Invoice.due_date < late_threshold
        ).all()
        
        for invoice in overdue:
            invoice.status = InvoiceStatus.late
        
        db.commit()
        return {"marked_late": len(overdue)}
    
    @staticmethod
    def record_payment(db: Session, invoice_id: int, amount: float, image: str = None):
        """
        Record payment and update invoice status
        """
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        
        # Create payment record
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            image=image,
            status=PaymentStatus.completed,
            paid_at=datetime.utcnow()
        )
        
        # Update invoice
        invoice.amount_paid += amount
        invoice.paid_at = datetime.utcnow()
        
        if invoice.amount_paid >= invoice.amount:
            invoice.status = InvoiceStatus.paid
        elif invoice.due_date < date.today():
            invoice.status = InvoiceStatus.late
        
        db.add(payment)
        db.commit()
        db.refresh(invoice)
        
        return payment