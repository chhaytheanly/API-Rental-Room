from enum import Enum

class PaymentStatus(str, Enum):
    paid = "paid"
    late = "late"
    pending = "pending"
    no_invoice = "no_invoice"