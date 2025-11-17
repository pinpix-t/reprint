"""
Job management endpoints for cron jobs and manual triggers.
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from jobs.daily_refresh import run_daily_refresh
import os
import logging

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)

@router.post("/refresh-24h")
async def refresh_24h_data(
    x_cron_secret: Optional[str] = Header(None, alias="X-Cron-Secret")
):
    """
    Refresh data for past 24 hours. 
    Can be called by cron jobs or manually.
    """
    # Optional: Verify secret for security
    expected_secret = os.getenv("CRON_SECRET")
    if expected_secret:
        if not x_cron_secret or x_cron_secret != expected_secret:
            logger.warning("Unauthorized refresh attempt")
            raise HTTPException(401, "Unauthorized: Invalid or missing X-Cron-Secret header")
    
    try:
        results = run_daily_refresh()
        return {
            "status": "success",
            "message": "Data refreshed for past 24 hours",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in refresh-24h: {e}", exc_info=True)
        raise HTTPException(500, f"Error refreshing data: {str(e)}")

@router.get("/status")
async def get_job_status():
    """Get status of scheduled jobs."""
    return {
        "status": "active",
        "message": "Scheduler is running",
        "next_refresh": "9 AM GMT daily"
    }

