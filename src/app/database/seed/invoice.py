from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import random
from .base import BaseSeeder
from src.app.model.invoice import Invoice, InvoiceStatus
from src.app.model.room import Room
from src.app.model.tenant import Tenant

class InvoiceSeeder(BaseSeeder):
    def __init__(self, db: Session):
        super().__init__(db, Invoice)

    def seed(self, tenants: list[Tenant], months_back: int = 4) -> list[Invoice]:
        """Generate monthly invoices for tenants"""
        invoices = []
        today = date.today()
        current_month = today.replace(day=1)
        
        for tenant in tenants:
            room = self.db.query(Room).filter(Room.id == tenant.room_id).first()
            if not room:
                continue
            
            for m in range(months_back):
                invoice_date = current_month - timedelta(days=30 * m)
                month, year = invoice_date.month, invoice_date.year
                
                # Skip duplicates
                if self.exists(tenant_id=tenant.id, month=month, year=year):
                    continue
                
                # Determine status based on recency
                status, amount_paid, paid_at = self._determine_status(m, room.price, invoice_date)
                
                invoice = self.create_one(
                    lambda: {
                        "room_id": room.id,
                        "tenant_id": tenant.id,
                        "month": month,
                        "year": year,
                        "amount": room.price,
                        "amount_paid": amount_paid,
                        "due_date": invoice_date.replace(day=5),
                        "status": status,
                        "created_at": invoice_date,
                        "paid_at": paid_at
                    },
                    skip_if_exists=False
                )
                if invoice:
                    invoices.append(invoice)
        
        self.log_created("invoices")
        return invoices

    def _determine_status(self, months_back: int, price: float, invoice_date: date):
        """Determine invoice status based on scenario"""
        if months_back == 0:  # Current month
            roll = random.randint(1, 10)
            if roll <= 5:
                return InvoiceStatus.paid, price, datetime.utcnow() - timedelta(days=random.randint(1, 4))
            elif roll <= 8:
                return InvoiceStatus.pending, 0, None
            else:
                return InvoiceStatus.late, 0, None
        elif months_back == 1:  # Last month
            if random.randint(1, 10) <= 8:
                return InvoiceStatus.paid, price, invoice_date.replace(day=random.randint(1, 28))
            else:
                return InvoiceStatus.late, 0, None
        else:  # Older months
            return InvoiceStatus.paid, price, invoice_date.replace(day=random.randint(1, 28))   