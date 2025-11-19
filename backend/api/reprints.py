from fastapi import APIRouter, Query, Request
from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd
import logging
from utils.rate_limiter import limiter, DEFAULT_RATE_LIMIT

logger = logging.getLogger(__name__)
from services.reprint_analyzer import (
    calculate_reprint_metrics,
    get_product_metrics,
    get_facility_metrics,
    get_reason_metrics,
    get_trend_data,
    get_comparison_metrics,
    get_facility_product_matrix,
    get_facility_drilldown,
    get_product_drilldown,
    get_quality_metrics,
    get_shipping_country_metrics,
    get_shipping_service_metrics,
    get_reason_category_metrics,
    get_trend_by_category
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
    end_date: Optional[str] = Query(None),
    region: Optional[str] = Query(None)
):
    """Get facility × product issue matrix."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    matrix = get_facility_product_matrix(start_date=start, end_date=end, region=region)
    
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
    
    # Debug: Log what we're getting - use logger instead of print
    logger.info(f"DEBUG: all_data.empty={all_data.empty}, has requested_date={'requested_date' in all_data.columns if not all_data.empty else False}")
    if not all_data.empty:
        logger.info(f"DEBUG: all_data columns: {all_data.columns.tolist()}")
        logger.info(f"DEBUG: all_data shape: {all_data.shape}")
    
    if not all_data.empty and 'requested_date' in all_data.columns:
        # Get the most recent date in the data
        # Filter out NaN dates first to ensure we get a valid max
        valid_dates = all_data['requested_date'].dropna()
        if len(valid_dates) > 0:
            max_date = valid_dates.max()
            logger.info(f"DEBUG: Max date from data: {max_date} (type: {type(max_date)})")
        else:
            max_date = None
            logger.warning("DEBUG: No valid dates found in data")
        
        if max_date is None or pd.isna(max_date):
            # If no valid dates, fall back to today
            logger.warning("DEBUG: Max date is None or NaN, falling back to datetime.now()")
            end_date = datetime.now(timezone.utc)
        else:
            # Use the most recent data date as the end date
            # Convert pandas Timestamp to datetime and make timezone-aware
            try:
                if isinstance(max_date, pd.Timestamp):
                    # Convert to Python datetime
                    max_date_dt = max_date.to_pydatetime()
                    # Set to end of day to include all records from that date
                    max_date_dt = max_date_dt.replace(hour=23, minute=59, second=59, microsecond=0)
                    end_date = max_date_dt.replace(tzinfo=timezone.utc)
                    logger.info(f"DEBUG: Converted pandas Timestamp to end_date: {end_date}")
                elif isinstance(max_date, datetime):
                    if max_date.tzinfo is None:
                        max_date_dt = max_date.replace(hour=23, minute=59, second=59, microsecond=0)
                        end_date = max_date_dt.replace(tzinfo=timezone.utc)
                    else:
                        end_date = max_date.replace(hour=23, minute=59, second=59, microsecond=0)
                    logger.info(f"Converted datetime to end_date: {end_date}")
                else:
                    # Try to convert to datetime
                    max_date_dt = pd.to_datetime(max_date).to_pydatetime()
                    max_date_dt = max_date_dt.replace(hour=23, minute=59, second=59, microsecond=0)
                    end_date = max_date_dt.replace(tzinfo=timezone.utc)
                    logger.info(f"Converted unknown type to end_date: {end_date}")
            except Exception as e:
                logger.error(f"Error converting max_date to end_date: {e}, falling back to datetime.now()")
                end_date = datetime.now(timezone.utc)
    else:
        # Fallback to current date if we can't determine data range
        logger.warning("DEBUG: Data is empty or missing requested_date column, falling back to datetime.now()")
        end_date = datetime.now(timezone.utc)
    
    # Calculate start date based on requested days, relative to most recent data
    # For days=1 (past 24 hours), we want the last day of data available
    # So if latest data is 2025-11-14 and days=1, we get 2025-11-14 only
    # If days=7, we get 2025-11-08 to 2025-11-14
    if days == 1:
        # For single day, start_date should be the start of the latest day
        # end_date is already set to end of latest day (23:59:59), so we need start of same day
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = (end_date - timedelta(days=days-1)) if days > 0 else end_date
    
    logger.info(f"DEBUG: Calculated date range for days={days}: start_date={start_date}, end_date={end_date}")
    
    # Note: get_reprints() will add 1 day internally to make end_date inclusive
    # So we pass end_date directly (not end_date + 1 day)
    
    # Get all key metrics with the calculated date range
    metrics = calculate_reprint_metrics(start_date=start_date, end_date=end_date)
    products = get_product_metrics(start_date=start_date, end_date=end_date, top_n=5)
    facilities = get_facility_metrics(start_date=start_date, end_date=end_date, top_n=5)
    reasons = get_reason_metrics(start_date=start_date, end_date=end_date, top_n=5)
    trend = get_trend_data(start_date=start_date, end_date=end_date, group_by="day")
    
    # Get quality metrics
    quality_metrics = get_quality_metrics(start_date=start_date, end_date=end_date)
    
    # Get shipping metrics
    shipping_countries = get_shipping_country_metrics(start_date=start_date, end_date=end_date, top_n=1)
    shipping_services = get_shipping_service_metrics(start_date=start_date, end_date=end_date, top_n=1)
    
    # Get reason categories
    reason_categories = get_reason_category_metrics(start_date=start_date, end_date=end_date)
    
    # Get trend by category
    trend_by_category = {}
    for category in ["Damage/Print Quality", "Packaging/Transit Damage", "Address/Undelivered", "Customer Error"]:
        category_trend = get_trend_by_category(start_date=start_date, end_date=end_date, category=category, group_by="day")
        trend_by_category[category] = [
            {
                "date": t.date.isoformat(),
                "count": t.count
            }
            for t in category_trend
        ]
    
    # Previous period comparison (same duration, shifted back)
    # For days=1, previous period is the day before the latest day
    # For days=7, previous period is the 7 days before the current period
    if days == 1:
        # For single day, previous period is the day before
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end
    else:
        # For multiple days, previous period is the same duration before current period
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date
    prev_metrics = calculate_reprint_metrics(start_date=prev_start, end_date=prev_end)
    prev_quality_metrics = get_quality_metrics(start_date=prev_start, end_date=prev_end)
    
    return {
        "total_reprints": metrics.total_reprints,
        "previous_period_total": prev_metrics.total_reprints,
        "change_percentage": metrics.change_percentage or 0,
        "quality_reprints": quality_metrics["quality_reprints"],
        "quality_percentage": quality_metrics["quality_percentage"],
        "top_shipping_country": {
            "country": shipping_countries[0].country if shipping_countries else None,
            "count": shipping_countries[0].count if shipping_countries else 0
        },
        "top_shipping_service": {
            "service": shipping_services[0].service if shipping_services else None,
            "count": shipping_services[0].count if shipping_services else 0
        },
        "reason_categories": [
            {
                "category": c.category,
                "count": c.count,
                "percentage": c.percentage
            }
            for c in reason_categories
        ],
        "trend_by_category": trend_by_category,
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

@router.get("/shipping/countries")
async def get_shipping_countries(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    top_n: int = Query(10, description="Number of top countries to return")
):
    """Get reprints by shipping country."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = get_shipping_country_metrics(start_date=start, end_date=end, top_n=top_n)
    
    return [
        {
            "country": m.country,
            "count": m.count,
            "percentage": m.percentage
        }
        for m in metrics
    ]

@router.get("/shipping/services")
async def get_shipping_services(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    top_n: int = Query(10, description="Number of top services to return")
):
    """Get reprints by shipping service."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = get_shipping_service_metrics(start_date=start, end_date=end, top_n=top_n)
    
    return [
        {
            "service": m.service,
            "count": m.count,
            "percentage": m.percentage
        }
        for m in metrics
    ]

@router.get("/categories")
async def get_categories(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get reprints grouped by reason category."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = get_reason_category_metrics(start_date=start, end_date=end)
    
    return [
        {
            "category": m.category,
            "count": m.count,
            "percentage": m.percentage
        }
        for m in metrics
    ]

@router.get("/records")
async def get_records(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    facility: Optional[str] = Query(None),
    product_type: Optional[str] = Query(None),
    reason_category: Optional[str] = Query(None),
    reprint_reason: Optional[str] = Query(None),
    shipping_country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    shipping_service: Optional[str] = Query(None),
    limit: int = Query(1000, description="Maximum number of records to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get detailed reprint records with filters."""
    from utils.db_access import get_reprints
    
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    df = get_reprints(
        start_date=start,
        end_date=end,
        facility=facility,
        product_type=product_type,
        limit=limit,
        offset=offset
    )
    
    # Apply additional filters
    if reason_category and 'reason_category' in df.columns:
        df = df[df['reason_category'] == reason_category]
    if reprint_reason and 'reprint_reason' in df.columns:
        df = df[df['reprint_reason'] == reprint_reason]
    # Region maps to shipping_country - use region if provided, otherwise use shipping_country
    region_filter = region or shipping_country
    if region_filter and 'shipping_country' in df.columns:
        df = df[df['shipping_country'] == region_filter]
    if shipping_service and 'shipping_service' in df.columns:
        df = df[df['shipping_service'] == shipping_service]
    
    # Convert to records
    records = []
    for _, row in df.iterrows():
        records.append({
            "requested_date": row['requested_date'].isoformat() if pd.notna(row.get('requested_date')) else None,
            "order_number": str(row.get('Order Number', '')) if pd.notna(row.get('Order Number')) else None,
            "product_type": str(row.get('product_type', '')) if pd.notna(row.get('product_type')) else None,
            "sub_type": str(row.get('sub_type', '')) if pd.notna(row.get('sub_type')) else None,
            "facility": str(row.get('facility', '')) if pd.notna(row.get('facility')) else None,
            "reprint_reason": str(row.get('reprint_reason', '')) if pd.notna(row.get('reprint_reason')) else None,
            "shipping_country": str(row.get('shipping_country', '')) if pd.notna(row.get('shipping_country')) else None,
            "shipping_service": str(row.get('shipping_service', '')) if pd.notna(row.get('shipping_service')) else None,
            "monumber": str(row.get('MONumber', '')) if pd.notna(row.get('MONumber')) else None,
            "conumber": str(row.get('CONumber', '')) if pd.notna(row.get('CONumber')) else None,
            "order_value": float(row.get('order_value', 0)) if pd.notna(row.get('order_value')) else None
        })
    
    return {
        "records": records,
        "total": len(records),
        "limit": limit,
        "offset": offset
    }

