from datetime import date
import logging

from ..config.session import local_session
from .invoice import InvoiceService

logger = logging.getLogger(__name__)
SessionLocal = local_session

def run_monthly_billing():
    """
    Generate invoices for all active tenants (Monthly)
    Called by APScheduler on 1st of every month
    """
    db = SessionLocal()
    
    try:
        logger.info("Starting monthly billing task")
        
        for_date = date.today()
        
        stats = InvoiceService.generate_all_monthly_invoices(db, for_date)
        
        db.commit()
        
        logger.info("Monthly billing complete: %s", stats)
        
        return stats
        
    except Exception as e:
        db.rollback()
        logger.exception("Monthly billing failed: %s", str(e))
        raise  # Re-raise so scheduler can log it
        
    finally:
        db.close()


def run_daily_late_fees():
    """
    Mark overdue invoices as late and apply fees (Daily)
    Called by APScheduler every day
    """
    db = SessionLocal()
    
    try:
        logger.info("Starting late fee processing task")
        
        stats = InvoiceService.update_late_invoices(db)
        
        db.commit()
        
        logger.info("Late fee processing complete: %s", stats)
        
        return stats
        
    except Exception as e:
        db.rollback()
        logger.exception("Late fee processing failed: %s", str(e))
        raise  # Re-raise so scheduler can log it
        
    finally:
        db.close()


def generate_tenant_invoice_sync(tenant_id: int, room_id: int, year: int, month: int, check_in_date: date = None):
    """
    Generate invoice for a specific tenant (synchronous)
    Called when tenant is assigned mid-month
    
    Note: This runs synchronously in the API request
    For small projects, this is acceptable
    """
    db = SessionLocal()
    
    try:
        logger.info("Generating invoice for tenant %s", tenant_id)
        
        for_date = date(year, month, 1)
        
        # Determine if this is first invoice (for proration)
        is_first = check_in_date is not None and check_in_date.year == year and check_in_date.month == month
        
        invoice = InvoiceService.generate_invoice(
            db,
            tenant_id=tenant_id,
            room_id=room_id,
            for_date=for_date,
            is_first_invoice=is_first,
            check_in_date=check_in_date
        )
        
        db.commit()
        
        logger.info("Generated invoice %s for tenant %s", invoice.id, tenant_id)
        
        return {"invoice_id": invoice.id, "status": "success"}
        
    except Exception as e:
        db.rollback()
        logger.exception("Tenant invoice generation failed: %s", str(e))
        raise
        
    finally:
        db.close()