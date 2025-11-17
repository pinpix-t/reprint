from fastapi import APIRouter, Query, Request
from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd
from utils.rate_limiter import limiter, DEFAULT_RATE_LIMIT
from services.reprint_analyzer import (
    calculate_reprint_metrics,
    get_product_metrics,
    get_facility_metrics,
    get_reason_metrics,
    get_trend_data,
    get_comparison_metrics,
    get_facility_product_matrix,
    get_facility_drilldown,
    get_product_drilldown
)

router = APIRouter(prefix="/api/reprints", tags=["reprints"])

@router.get("/metrics")
async def get_reprint_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    facility: Optional[str] = Query(None),
    product_type: Optional[str] = Query(None)
):
    """Get overall reprint metrics."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = calculate_reprint_metrics(
        start_date=start,
        end_date=end,
        facility=facility,
        product_type=product_type
    )
    
    return {
        "total_reprints": metrics.total_reprints,
        "period_start": metrics.period_start.isoformat() if metrics.period_start else None,
        "period_end": metrics.period_end.isoformat() if metrics.period_end else None,
        "previous_period_total": metrics.previous_period_total,
        "change_percentage": metrics.change_percentage
    }

@router.get("/products")
async def get_products_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    top_n: int = Query(10)
):
    """Get metrics by product type."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = get_product_metrics(start_date=start, end_date=end, top_n=top_n)
    
    return [
        {
            "product_type": m.product_type,
            "count": m.count,
            "percentage": m.percentage,
            "top_reasons": m.top_reasons
        }
        for m in metrics
    ]

@router.get("/facilities")
async def get_facilities_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    top_n: int = Query(10)
):
    """Get metrics by facility."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = get_facility_metrics(start_date=start, end_date=end, top_n=top_n)
    
    return [
        {
            "facility": m.facility,
            "count": m.count,
            "percentage": m.percentage,
            "top_products": m.top_products,
            "top_reasons": m.top_reasons
        }
        for m in metrics
    ]

@router.get("/reasons")
async def get_reasons_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    top_n: int = Query(10)
):
    """Get metrics by reprint reason."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = get_reason_metrics(start_date=start, end_date=end, top_n=top_n)
    
    return [
        {
            "reason": m.reason,
            "count": m.count,
            "percentage": m.percentage,
            "affected_products": m.affected_products
        }
        for m in metrics
    ]

@router.get("/trend")
async def get_trend(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    group_by: str = Query("day", description="Group by: day, week, or month")
):
    """Get time-series trend data."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    trend = get_trend_data(start_date=start, end_date=end, group_by=group_by)
    
    return [
        {
            "date": t.date.isoformat(),
            "count": t.count,
            "by_product": t.by_product,
            "by_facility": t.by_facility,
            "by_reason": t.by_reason
        }
        for t in trend
    ]

@router.get("/compare")
async def get_comparison(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    comparison_type: str = Query("week", description="Compare with: week, month, or year")
):
    """Compare current period with previous period."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    comparison = get_comparison_metrics(start, end, comparison_type=comparison_type)
    
    return {
        "current": comparison.current,
        "previous": comparison.previous,
        "change": comparison.change,
        "change_percentage": comparison.change_percentage,
        "period": comparison.period
    }

@router.get("/matrix")
async def get_matrix(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get facility × product issue matrix."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    matrix = get_facility_product_matrix(start_date=start, end_date=end)
    
    return [
        {
            "facility": m.facility,
            "product": m.product,
            "count": m.count,
            "reasons": m.reasons
        }
        for m in matrix
    ]

@router.get("/facility/{facility}")
async def get_facility_details(
    facility: str,
    days: int = Query(30, description="Number of days to analyze")
):
    """Get detailed analysis for a specific facility."""
    return get_facility_drilldown(facility, days=days)

@router.get("/product/{product}")
async def get_product_details(
    product: str,
    days: int = Query(30, description="Number of days to analyze")
):
    """Get detailed analysis for a specific product."""
    return get_product_drilldown(product, days=days)

@router.get("/overview")
@limiter.limit(DEFAULT_RATE_LIMIT)
async def get_overview(
    request: Request,
    days: int = Query(30, description="Number of days for overview")
):
    """Get overview metrics for dashboard."""
    from datetime import timezone
    from utils.db_access import get_all_reprints
    
    # First, get the actual date range of data in the database
    # This allows us to calculate "last N days" relative to the most recent data
    all_data = get_all_reprints(use_cache=False)
    
    if not all_data.empty and 'requested_date' in all_data.columns:
        # Get the most recent date in the data
        max_date = all_data['requested_date'].max()
        if pd.isna(max_date):
            # If no valid dates, fall back to today
            end_date = datetime.now(timezone.utc)
        else:
            # Use the most recent data date as the end date
            # Convert to timezone-aware if needed
            if max_date.tzinfo is None:
                end_date = max_date.replace(tzinfo=timezone.utc)
            else:
                end_date = max_date
    else:
        # Fallback to current date if we can't determine data range
        end_date = datetime.now(timezone.utc)
    
    # Calculate start date based on requested days, relative to most recent data
    start_date = end_date - timedelta(days=days)
    
    # Get all key metrics with the calculated date range
    metrics = calculate_reprint_metrics(start_date=start_date, end_date=end_date)
    products = get_product_metrics(start_date=start_date, end_date=end_date, top_n=5)
    facilities = get_facility_metrics(start_date=start_date, end_date=end_date, top_n=5)
    reasons = get_reason_metrics(start_date=start_date, end_date=end_date, top_n=5)
    trend = get_trend_data(start_date=start_date, end_date=end_date, group_by="day")
    
    # Previous period comparison (same duration, shifted back)
    prev_start = start_date - timedelta(days=days)
    prev_metrics = calculate_reprint_metrics(start_date=prev_start, end_date=start_date)
    
    return {
        "total_reprints": metrics.total_reprints,
        "previous_period_total": prev_metrics.total_reprints,
        "change_percentage": metrics.change_percentage or 0,
        "top_products": [
            {
                "product_type": p.product_type,
                "count": p.count,
                "percentage": p.percentage
            }
            for p in products
        ],
        "top_facilities": [
            {
                "facility": f.facility,
                "count": f.count,
                "percentage": f.percentage
            }
            for f in facilities
        ],
        "top_reasons": [
            {
                "reason": r.reason,
                "count": r.count,
                "percentage": r.percentage
            }
            for r in reasons
        ],
        "trend": [
            {
                "date": t.date.isoformat(),
                "count": t.count
            }
            for t in trend
        ]
    }

