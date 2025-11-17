"""
Scheduler for automated jobs.
Can be run as a background service or deployed as a scheduled task.
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import schedule
import time
from jobs.daily_refresh import run_daily_refresh
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_schedule():
    """Set up scheduled jobs."""
    # Daily refresh at 2 AM
    schedule.every().day.at("02:00").do(run_daily_refresh)
    
    # Weekly summary (Monday at 9 AM)
    schedule.every().monday.at("09:00").do(generate_weekly_report)
    
    logger.info("Scheduler configured")

def generate_weekly_report():
    """Generate weekly summary report with job locking."""
    from services.report_generator import generate_weekly_summary
    from utils.job_locker import job_lock
    
    with job_lock('weekly_report') as acquired:
        if not acquired:
            logger.warning("Weekly report generation already running, skipping")
            return
        
        try:
            logger.info("Generating weekly report...")
            generate_weekly_summary()
            logger.info("Weekly report generated")
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}", exc_info=True)

def run_scheduler():
    """Run the scheduler (blocking)."""
    setup_schedule()
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    run_scheduler()

