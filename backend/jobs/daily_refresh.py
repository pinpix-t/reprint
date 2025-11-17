"""
Daily data refresh job.
This can be run as a scheduled task (cron, GitHub Actions, etc.)
Refreshes data from past 24 hours for 9 AM GMT presentation.
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from datetime import datetime, timedelta, timezone
from utils.db_access import get_all_reprints, get_reprints
from services.review_analyzer import analyze_reviews
from services.freshdesk_client import fetch_tickets, filter_quality_tickets
from utils.ticket_matcher import get_ticket_reprint_stats
from utils.job_locker import job_lock
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_reprint_data():
    """Refresh reprint data from Supabase (past 24 hours)."""
    try:
        logger.info("Refreshing reprint data for past 24 hours...")
        # Get data from past 24 hours
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        # Fetch and cache all data (for full dataset)
        df_all = get_all_reprints(use_cache=False)
        logger.info(f"Refreshed {len(df_all)} total reprint records")
        
        # Also fetch past 24 hours specifically
        df_24h = get_reprints(start_date=start_date, end_date=end_date)
        logger.info(f"Found {len(df_24h)} reprints in past 24 hours")
        
        return True
    except Exception as e:
        logger.error(f"Error refreshing reprint data: {e}", exc_info=True)
        return False

def refresh_review_analysis():
    """Refresh review analysis for past 24 hours."""
    try:
        logger.info("Refreshing review analysis for past 24 hours...")
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        analysis = analyze_reviews(start_date=start_date, end_date=end_date)
        logger.info(f"Analyzed {analysis['total_reviews']} reviews in past 24 hours")
        return True
    except Exception as e:
        logger.error(f"Error refreshing review analysis: {e}", exc_info=True)
        return False

def refresh_freshdesk_data():
    """Refresh Freshdesk ticket data for past 24 hours."""
    try:
        logger.info("Refreshing Freshdesk data for past 24 hours...")
        updated_since = datetime.now(timezone.utc) - timedelta(days=1)
        tickets = fetch_tickets(updated_since=updated_since)
        quality_tickets = filter_quality_tickets(tickets)
        stats = get_ticket_reprint_stats(quality_tickets)
        logger.info(f"Processed {stats['total_tickets']} tickets in past 24 hours, matched {stats['matched_tickets']}")
        return True
    except Exception as e:
        logger.error(f"Error refreshing Freshdesk data: {e}", exc_info=True)
        return False

def run_daily_refresh():
    """Run all daily refresh tasks with job locking to prevent concurrent execution."""
    with job_lock('daily_refresh') as acquired:
        if not acquired:
            logger.warning("Daily refresh already running, skipping this execution")
            return {"status": "skipped", "reason": "already_running"}
        
        logger.info("Starting daily refresh for past 24 hours (9 AM GMT)...")
        results = {
            "reprints": refresh_reprint_data(),
            "reviews": refresh_review_analysis(),
            "freshdesk": refresh_freshdesk_data(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Daily refresh completed at 9 AM GMT: {results}")
        return results

if __name__ == "__main__":
    run_daily_refresh()

