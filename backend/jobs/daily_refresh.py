"""
Daily data refresh job.
This can be run as a scheduled task (cron, GitHub Actions, etc.)
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from datetime import datetime, timedelta
from services.reprint_analyzer import get_all_reprints
from services.review_analyzer import analyze_reviews
from services.freshdesk_client import fetch_tickets, filter_quality_tickets
from utils.ticket_matcher import get_ticket_reprint_stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_reprint_data():
    """Refresh reprint data from Supabase."""
    try:
        logger.info("Refreshing reprint data...")
        # This will fetch and cache data
        df = get_all_reprints()
        logger.info(f"Refreshed {len(df)} reprint records")
        return True
    except Exception as e:
        logger.error(f"Error refreshing reprint data: {e}")
        return False

def refresh_review_analysis():
    """Refresh review analysis."""
    try:
        logger.info("Refreshing review analysis...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        analysis = analyze_reviews(start_date=start_date, end_date=end_date)
        logger.info(f"Analyzed {analysis['total_reviews']} reviews")
        return True
    except Exception as e:
        logger.error(f"Error refreshing review analysis: {e}")
        return False

def refresh_freshdesk_data():
    """Refresh Freshdesk ticket data."""
    try:
        logger.info("Refreshing Freshdesk data...")
        updated_since = datetime.now() - timedelta(days=1)
        tickets = fetch_tickets(updated_since=updated_since)
        quality_tickets = filter_quality_tickets(tickets)
        stats = get_ticket_reprint_stats(quality_tickets)
        logger.info(f"Processed {stats['total_tickets']} tickets, matched {stats['matched_tickets']}")
        return True
    except Exception as e:
        logger.error(f"Error refreshing Freshdesk data: {e}")
        return False

def run_daily_refresh():
    """Run all daily refresh tasks."""
    logger.info("Starting daily refresh...")
    results = {
        "reprints": refresh_reprint_data(),
        "reviews": refresh_review_analysis(),
        "freshdesk": refresh_freshdesk_data()
    }
    
    logger.info(f"Daily refresh completed: {results}")
    return results

if __name__ == "__main__":
    run_daily_refresh()

