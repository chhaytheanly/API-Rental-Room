from fastapi import APIRouter, HTTPException

from ..config.scheduler import get_scheduler
from ..services.task import run_daily_late_fees, run_monthly_billing

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.post("/trigger-monthly")
def trigger_monthly_billing():
    """
    Manually trigger monthly billing (for testing/admin)
    """
    try:
        stats = run_monthly_billing()
        return {
            "message": "Monthly billing completed",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-late-fees")
def trigger_late_fees():
    """
    Manually trigger late fee processing (for testing/admin)
    """
    try:
        stats = run_daily_late_fees()
        return {
            "message": "Late fee processing completed",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduler-status")
def get_scheduler_status():
    """
    Get APScheduler status and scheduled jobs
    """
    scheduler = get_scheduler()
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "trigger": str(job.trigger),
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return {
        "scheduler_running": scheduler.running,
        "total_jobs": len(jobs),
        "jobs": jobs
    }