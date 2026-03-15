from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from src.app.database.seed.base import BaseSeeder
from src.app.model.payment import Payment, PaymentStatus
from src.app.model.invoice import Invoice, InvoiceStatus

class PaymentSeeder(BaseSeeder):
    def __init__(self, db: Session):
        super().__init__(db, Payment)

    def seed(self, invoices: list[Invoice]) -> list[Payment]:
        """Create payment records for paid/partial invoices"""
        payments = []
        
        for invoice in invoices:
            if invoice.status == InvoiceStatus.paid and invoice.amount_paid > 0:
                payment = self.create_one(
                    lambda: {
                        "invoice_id": invoice.id,
                        "amount": invoice.amount_paid,
                        "image": f"uploads/receipts/payment_{invoice.id}_{invoice.month}{invoice.year}.jpg",
                        "status": PaymentStatus.completed,
                        "paid_at": invoice.paid_at or datetime.utcnow()
                    },
                    skip_if_exists=False
                )
                if payment:
                    payments.append(payment)
                    
            elif invoice.status == InvoiceStatus.pending and random.randint(1, 10) <= 3:
                # Partial payment scenario
                partial = round(invoice.amount * random.uniform(0.3, 0.8), 2)
                payment = self.create_one(
                    lambda: {
                        "invoice_id": invoice.id,
                        "amount": partial,
                        "image": f"uploads/receipts/partial_{invoice.id}.jpg",
                        "status": PaymentStatus.completed,
                        "paid_at": datetime.utcnow() - timedelta(days=random.randint(1, 10))
                    },
                    skip_if_exists=False
                )
                if payment:
                    # Update invoice amount_paid
                    invoice.amount_paid = partial
                    payments.append(payment)
        
        self.log_created("payments")
        return payments