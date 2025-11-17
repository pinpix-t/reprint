from fastapi import APIRouter, Query, Request
from typing import Optional
from datetime import datetime, timedelta
from utils.rate_limiter import limiter, DEFAULT_RATE_LIMIT
from services.review_analyzer import analyze_reviews, get_review_summary, get_product_quality_summary

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

@router.get("/analyze")
async def analyze_reviews_endpoint(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Analyze reviews for quality/damage issues."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    return analyze_reviews(start_date=start, end_date=end)

@router.get("/summary")
@limiter.limit(DEFAULT_RATE_LIMIT)
async def get_review_summary_endpoint(
    request: Request,
    days: int = Query(7, description="Number of days to analyze")
):
    """Get review summary for the last N days."""
    return get_review_summary(days=days)

@router.get("/product/{product}")
async def get_product_quality(
    product: str,
    days: int = Query(30, description="Number of days to analyze")
):
    """Get quality summary for a specific product."""
    return get_product_quality_summary(product, days=days)

