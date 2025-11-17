"""
Report generation service for weekly/daily summaries.
"""
from datetime import datetime, timedelta
from typing import Dict
from services.reprint_analyzer import (
    calculate_reprint_metrics,
    get_product_metrics,
    get_facility_metrics,
    get_reason_metrics,
    get_trend_data
)
from services.review_analyzer import analyze_reviews
from services.freshdesk_client import fetch_tickets, filter_quality_tickets
from utils.ticket_matcher import get_ticket_reprint_stats
import json

def generate_weekly_summary() -> Dict:
    """Generate weekly summary report."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Get reprint metrics
    metrics = calculate_reprint_metrics(start_date=start_date, end_date=end_date)
    products = get_product_metrics(start_date=start_date, end_date=end_date, top_n=10)
    facilities = get_facility_metrics(start_date=start_date, end_date=end_date, top_n=10)
    reasons = get_reason_metrics(start_date=start_date, end_date=end_date, top_n=10)
    trend = get_trend_data(start_date=start_date, end_date=end_date, group_by="day")
    
    # Get review analysis
    review_analysis = analyze_reviews(start_date=start_date, end_date=end_date)
    
    # Get Freshdesk stats
    tickets = fetch_tickets(updated_since=start_date)
    quality_tickets = filter_quality_tickets(tickets)
    freshdesk_stats = get_ticket_reprint_stats(quality_tickets)
    
    report = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "reprints": {
            "total": metrics.total_reprints,
            "change_percentage": metrics.change_percentage,
            "top_products": [
                {
                    "product": p.product_type,
                    "count": p.count,
                    "percentage": p.percentage
                }
                for p in products[:5]
            ],
            "top_facilities": [
                {
                    "facility": f.facility,
                    "count": f.count,
                    "percentage": f.percentage
                }
                for f in facilities[:5]
            ],
            "top_reasons": [
                {
                    "reason": r.reason,
                    "count": r.count,
                    "percentage": r.percentage
                }
                for r in reasons[:5]
            ]
        },
        "reviews": {
            "total": review_analysis["total_reviews"],
            "with_issues": review_analysis["reviews_with_issues"],
            "top_products": review_analysis["top_products_with_issues"][:5],
            "trending_concerns": review_analysis["trending_concerns"][:5]
        },
        "freshdesk": {
            "total_tickets": freshdesk_stats["total_tickets"],
            "matched_tickets": freshdesk_stats["matched_tickets"],
            "match_rate": freshdesk_stats["match_rate"]
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return report

def generate_daily_summary() -> Dict:
    """Generate daily summary report."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    metrics = calculate_reprint_metrics(start_date=start_date, end_date=end_date)
    products = get_product_metrics(start_date=start_date, end_date=end_date, top_n=5)
    reasons = get_reason_metrics(start_date=start_date, end_date=end_date, top_n=5)
    
    report = {
        "date": end_date.date().isoformat(),
        "reprints": {
            "total": metrics.total_reprints,
            "top_products": [
                {
                    "product": p.product_type,
                    "count": p.count
                }
                for p in products
            ],
            "top_reasons": [
                {
                    "reason": r.reason,
                    "count": r.count
                }
                for r in reasons
            ]
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return report

def save_report(report: Dict, filename: str):
    """Save report to JSON file."""
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

def generate_and_save_weekly_report():
    """Generate and save weekly report."""
    report = generate_weekly_summary()
    filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
    save_report(report, filename)
    return report

def generate_and_save_daily_report():
    """Generate and save daily report."""
    report = generate_daily_summary()
    filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    save_report(report, filename)
    return report

