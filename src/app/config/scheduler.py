from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()

def init_scheduler():
    """
    Initialize and start the APScheduler
    Call this in FastAPI startup event
    """
    from src.app.services.task import run_daily_late_fees, run_monthly_billing

    if scheduler.running:
        return
    
    # Add monthly billing job (1st of every month at 2 AM)
    scheduler.add_job(
        func=run_monthly_billing,
        trigger=CronTrigger(day=1, hour=2, minute=0),
        id="monthly_billing",
        name="Generate monthly invoices",
        replace_existing=True,
        misfire_grace_time=3600  # 1 hour grace period
    )
    
    # Add daily late fee job (every day at 3 AM)
    scheduler.add_job(
        func=run_daily_late_fees,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_late_fees",
        name="Process late fees",
        replace_existing=True,
        misfire_grace_time=1800  # 30 minutes grace period
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("APScheduler started successfully")
    
    # Log all scheduled jobs
    for job in scheduler.get_jobs():
        logger.info("Scheduled job: %s - %s", job.name, job.trigger)

def shutdown_scheduler():
    """
    Shutdown the scheduler gracefully
    Call this in FastAPI shutdown event
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shutdown complete")

def get_scheduler():
    """Get the scheduler instance"""
    return scheduler