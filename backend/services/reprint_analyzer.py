from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
from utils.db_access import get_reprints, get_all_reprints
from models.reprint_metrics import (
    ReprintMetrics, ProductMetrics, FacilityMetrics, 
    ReasonMetrics, TrendDataPoint, ComparisonMetrics, FacilityProductMatrix,
    ShippingCountryMetrics, ShippingServiceMetrics, ReasonCategoryMetrics
)

def calculate_reprint_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    facility: Optional[str] = None,
    product_type: Optional[str] = None
) -> ReprintMetrics:
    """Calculate overall reprint metrics for a period."""
    df = get_reprints(
        start_date=start_date,
        end_date=end_date,
        facility=facility,
        product_type=product_type
    )
    
    if df.empty:
        return ReprintMetrics(
            total_reprints=0,
            period_start=start_date or datetime.now(),
            period_end=end_date or datetime.now()
        )
    
    total = len(df)
    
    # Calculate previous period for comparison
    if start_date and end_date:
        period_duration = end_date - start_date
        prev_start = start_date - period_duration
        prev_end = start_date
        
        prev_df = get_reprints(
            start_date=prev_start,
            end_date=prev_end,
            facility=facility,
            product_type=product_type
        )
        prev_total = len(prev_df)
        
        change = total - prev_total
        change_pct = (change / prev_total * 100) if prev_total > 0 else 0
        
        return ReprintMetrics(
            total_reprints=total,
            period_start=start_date,
            period_end=end_date,
            previous_period_total=prev_total,
            change_percentage=change_pct
        )
    
    return ReprintMetrics(
        total_reprints=total,
        period_start=start_date or datetime.now(),
        period_end=end_date or datetime.now()
    )

def get_product_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    top_n: int = 10
) -> List[ProductMetrics]:
    """Get metrics by product type."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'product_type' not in df.columns:
        return []
    
    product_counts = df['product_type'].value_counts()
    total = len(df)
    
    metrics = []
    for product, count in product_counts.head(top_n).items():
        # Get top reasons for this product
        product_df = df[df['product_type'] == product]
        if 'reprint_reason' in product_df.columns:
            reasons = product_df['reprint_reason'].value_counts().head(5)
            # Format as Dict[str, int] where key is reason name, value is count
            top_reasons = [{str(r): int(c)} for r, c in reasons.items()]
        else:
            top_reasons = []
        
        metrics.append(ProductMetrics(
            product_type=product,
            count=int(count),
            percentage=(count / total * 100) if total > 0 else 0,
            top_reasons=top_reasons
        ))
    
    return metrics

def get_facility_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    top_n: int = 10
) -> List[FacilityMetrics]:
    """Get metrics by facility."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'facility' not in df.columns:
        return []
    
    facility_counts = df['facility'].value_counts()
    total = len(df)
    
    metrics = []
    for facility, count in facility_counts.head(top_n).items():
        facility_df = df[df['facility'] == facility]
        
        # Top products for this facility
        if 'product_type' in facility_df.columns:
            products = facility_df['product_type'].value_counts().head(5)
            # Format as Dict[str, int] where key is product name, value is count
            top_products = [{str(p): int(c)} for p, c in products.items()]
        else:
            top_products = []
        
        # Top reasons for this facility
        if 'reprint_reason' in facility_df.columns:
            reasons = facility_df['reprint_reason'].value_counts().head(5)
            # Format as Dict[str, int] where key is reason name, value is count
            top_reasons = [{str(r): int(c)} for r, c in reasons.items()]
        else:
            top_reasons = []
        
        metrics.append(FacilityMetrics(
            facility=facility,
            count=int(count),
            percentage=(count / total * 100) if total > 0 else 0,
            top_products=top_products,
            top_reasons=top_reasons
        ))
    
    return metrics

def get_reason_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    top_n: int = 10,
    region: Optional[str] = None
) -> List[ReasonMetrics]:
    """Get metrics by reprint reason."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    # Filter by region if provided
    if region and 'shipping_country' in df.columns:
        df = df[df['shipping_country'] == region]
    
    if df.empty or 'reprint_reason' not in df.columns:
        return []
    
    reason_counts = df['reprint_reason'].value_counts()
    total = len(df)
    
    metrics = []
    for reason, count in reason_counts.head(top_n).items():
        reason_df = df[df['reprint_reason'] == reason]
        
        # Affected products
        if 'product_type' in reason_df.columns:
            products = reason_df['product_type'].unique().tolist()
        else:
            products = []
        
        metrics.append(ReasonMetrics(
            reason=reason,
            count=int(count),
            percentage=(count / total * 100) if total > 0 else 0,
            affected_products=products[:10]  # Top 10
        ))
    
    return metrics

def get_trend_data(
    start_date: datetime,
    end_date: datetime,
    group_by: str = "day",  # "day", "week", "month"
    reason_category: Optional[str] = None,  # Filter by reason category
    region: Optional[str] = None  # Filter by region (shipping_country)
) -> List[TrendDataPoint]:
    """Get time-series trend data."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'requested_date' not in df.columns:
        return []
    
    # Filter by region if provided
    if region and 'shipping_country' in df.columns:
        df = df[df['shipping_country'] == region]
    
    # Filter by category if specified
    if reason_category and 'reason_category' in df.columns:
        df = df[df['reason_category'] == reason_category]
    
    # Remove rows without dates
    df = df[df['requested_date'].notna()].copy()
    
    if df.empty:
        return []
    
    # Group by time period
    if group_by == "day":
        df['period'] = df['requested_date'].dt.date
    elif group_by == "week":
        df['period'] = df['requested_date'].dt.to_period('W').dt.start_time
    elif group_by == "month":
        df['period'] = df['requested_date'].dt.to_period('M').dt.start_time
    else:
        df['period'] = df['requested_date'].dt.date
    
    trend_points = []
    for period, group_df in df.groupby('period'):
        by_product = {}
        by_facility = {}
        by_reason = {}
        
        if 'product_type' in group_df.columns:
            by_product = group_df['product_type'].value_counts().to_dict()
        
        if 'facility' in group_df.columns:
            by_facility = group_df['facility'].value_counts().to_dict()
        
        if 'reprint_reason' in group_df.columns:
            by_reason = group_df['reprint_reason'].value_counts().to_dict()
        
        trend_points.append(TrendDataPoint(
            date=period if isinstance(period, datetime) else datetime.combine(period, datetime.min.time()),
            count=len(group_df),
            by_product=by_product,
            by_facility=by_facility,
            by_reason=by_reason
        ))
    
    return sorted(trend_points, key=lambda x: x.date)

def get_comparison_metrics(
    current_start: datetime,
    current_end: datetime,
    comparison_type: str = "week"  # "week", "month", "year"
) -> ComparisonMetrics:
    """Compare current period with previous period."""
    current_df = get_reprints(start_date=current_start, end_date=current_end)
    current_count = len(current_df)
    
    # Calculate previous period
    period_duration = current_end - current_start
    
    if comparison_type == "week":
        prev_start = current_start - timedelta(weeks=1)
    elif comparison_type == "month":
        prev_start = current_start - timedelta(days=30)
    elif comparison_type == "year":
        prev_start = current_start - timedelta(days=365)
    else:
        prev_start = current_start - period_duration
    
    prev_end = current_start
    prev_df = get_reprints(start_date=prev_start, end_date=prev_end)
    prev_count = len(prev_df)
    
    change = current_count - prev_count
    change_pct = (change / prev_count * 100) if prev_count > 0 else 0
    
    return ComparisonMetrics(
        current=current_count,
        previous=prev_count,
        change=change,
        change_percentage=change_pct,
        period=comparison_type
    )

def get_facility_product_matrix(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    region: Optional[str] = None
) -> List[FacilityProductMatrix]:
    """Get facility × product issue matrix."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'facility' not in df.columns or 'product_type' not in df.columns:
        return []
    
    # Filter by region if provided
    if region and 'shipping_country' in df.columns:
        before_region = len(df)
        df = df[df['shipping_country'] == region]
        logger.info(f"After region filter ({region}): {len(df)} records (from {before_region})")
    elif region:
        logger.warning(f"Region filter provided ({region}) but 'shipping_country' column not found")
    
    if df.empty:
        return []
    
    matrix = []
    for (facility, product), group_df in df.groupby(['facility', 'product_type']):
        reasons = {}
        if 'reprint_reason' in group_df.columns:
            reason_counts = group_df['reprint_reason'].value_counts()
            reasons = {r: int(c) for r, c in reason_counts.items()}
        
        matrix.append(FacilityProductMatrix(
            facility=facility,
            product=product,
            count=len(group_df),
            reasons=reasons
        ))
    
    return sorted(matrix, key=lambda x: x.count, reverse=True)

def get_facility_drilldown(facility: str, days: int = 30, region: Optional[str] = None) -> Dict:
    """Get detailed analysis for a specific facility."""
    # Use timezone-aware datetime to match overview endpoint behavior
    from datetime import timezone
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    df = get_reprints(start_date=start_date, end_date=end_date, facility=facility)
    
    # Filter by region if provided
    if region and 'shipping_country' in df.columns:
        df = df[df['shipping_country'] == region]
    
    if df.empty:
        return {
            "facility": facility,
            "total_reprints": 0,
            "products": {},
            "reasons": {},
            "trend": []
        }
    
    products = {}
    if 'product_type' in df.columns:
        products = df['product_type'].value_counts().to_dict()
    
    reasons = {}
    if 'reprint_reason' in df.columns:
        reasons = df['reprint_reason'].value_counts().to_dict()
    
    # Get trend - end_date will be made inclusive by get_trend_data -> get_reprints
    trend = get_trend_data(start_date, end_date, group_by="day", region=region)
    
    return {
        "facility": facility,
        "total_reprints": len(df),
        "products": {k: int(v) for k, v in products.items()},
        "reasons": {k: int(v) for k, v in reasons.items()},
        "trend": [{"date": t.date.isoformat(), "count": t.count} for t in trend]
    }

def get_product_drilldown(product: str, days: int = 30, region: Optional[str] = None) -> Dict:
    """Get detailed analysis for a specific product."""
    # Use timezone-aware datetime to match overview endpoint behavior
    from datetime import timezone
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    df = get_reprints(start_date=start_date, end_date=end_date, product_type=product)
    
    # Filter by region if provided
    if region and 'shipping_country' in df.columns:
        df = df[df['shipping_country'] == region]
    
    if df.empty:
        return {
            "product": product,
            "total_reprints": 0,
            "facilities": {},
            "reasons": {},
            "trend": []
        }
    
    facilities = {}
    if 'facility' in df.columns:
        facilities = df['facility'].value_counts().to_dict()
    
    reasons = {}
    if 'reprint_reason' in df.columns:
        reasons = df['reprint_reason'].value_counts().to_dict()
    
    # Get trend - end_date will be made inclusive by get_trend_data -> get_reprints
    trend = get_trend_data(start_date, end_date, group_by="day", region=region)
    
    return {
        "product": product,
        "total_reprints": len(df),
        "facilities": {k: int(v) for k, v in facilities.items()},
        "reasons": {k: int(v) for k, v in reasons.items()},
        "trend": [{"date": t.date.isoformat(), "count": t.count} for t in trend]
    }

def get_quality_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    facility: Optional[str] = None,
    product_type: Optional[str] = None
) -> Dict:
    """Calculate quality/damage-related reprints count and percentage."""
    df = get_reprints(
        start_date=start_date,
        end_date=end_date,
        facility=facility,
        product_type=product_type
    )
    
    if df.empty:
        return {
            "quality_reprints": 0,
            "quality_percentage": 0.0,
            "total_reprints": 0
        }
    
    total = len(df)
    
    # Filter for quality/damage reasons
    if 'reason_category' in df.columns:
        quality_df = df[df['reason_category'] == "Damage/Print Quality"]
        quality_count = len(quality_df)
    else:
        # Fallback: check reason text for quality keywords
        if 'reprint_reason' in df.columns:
            quality_keywords = ['fingerprint', 'scuff', 'colour quality', 'color quality', 'poor quality',
                              'ink', 'oil marks', 'pages not bound', 'pages missing', 'mixed up',
                              'incorrectly cut', 'incorrectly cropped', 'wiro-binding']
            quality_df = df[df['reprint_reason'].str.lower().str.contains('|'.join(quality_keywords), na=False)]
            quality_count = len(quality_df)
        else:
            quality_count = 0
    
    quality_percentage = (quality_count / total * 100) if total > 0 else 0.0
    
    return {
        "quality_reprints": quality_count,
        "quality_percentage": quality_percentage,
        "total_reprints": total
    }

def get_shipping_country_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    top_n: int = 10
) -> List[ShippingCountryMetrics]:
    """Get metrics by shipping country."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'shipping_country' not in df.columns:
        return []
    
    country_counts = df['shipping_country'].value_counts()
    total = len(df)
    
    metrics = []
    for country, count in country_counts.head(top_n).items():
        metrics.append(ShippingCountryMetrics(
            country=str(country),
            count=int(count),
            percentage=(count / total * 100) if total > 0 else 0
        ))
    
    return metrics

def get_shipping_service_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    top_n: int = 10
) -> List[ShippingServiceMetrics]:
    """Get metrics by shipping service."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'shipping_service' not in df.columns:
        return []
    
    service_counts = df['shipping_service'].value_counts()
    total = len(df)
    
    metrics = []
    for service, count in service_counts.head(top_n).items():
        metrics.append(ShippingServiceMetrics(
            service=str(service),
            count=int(count),
            percentage=(count / total * 100) if total > 0 else 0
        ))
    
    return metrics

def get_reason_category_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[ReasonCategoryMetrics]:
    """Get metrics grouped by reason category."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'reason_category' not in df.columns:
        return []
    
    category_counts = df['reason_category'].value_counts()
    total = len(df)
    
    metrics = []
    for category, count in category_counts.items():
        metrics.append(ReasonCategoryMetrics(
            category=str(category),
            count=int(count),
            percentage=(count / total * 100) if total > 0 else 0
        ))
    
    return sorted(metrics, key=lambda x: x.count, reverse=True)

def get_trend_by_category(
    start_date: datetime,
    end_date: datetime,
    category: Optional[str] = None,
    group_by: str = "day"
) -> List[TrendDataPoint]:
    """Get trend data filtered by reason category."""
    df = get_reprints(start_date=start_date, end_date=end_date)
    
    if df.empty or 'requested_date' not in df.columns:
        return []
    
    # Filter by category if specified
    if category and 'reason_category' in df.columns:
        df = df[df['reason_category'] == category]
    
    # Remove rows without dates
    df = df[df['requested_date'].notna()].copy()
    
    if df.empty:
        return []
    
    # Group by time period
    if group_by == "day":
        df['period'] = df['requested_date'].dt.date
    elif group_by == "week":
        df['period'] = df['requested_date'].dt.to_period('W').dt.start_time
    elif group_by == "month":
        df['period'] = df['requested_date'].dt.to_period('M').dt.start_time
    else:
        df['period'] = df['requested_date'].dt.date
    
    trend_points = []
    for period, group_df in df.groupby('period'):
        by_product = {}
        by_facility = {}
        by_reason = {}
        
        if 'product_type' in group_df.columns:
            by_product = group_df['product_type'].value_counts().to_dict()
        
        if 'facility' in group_df.columns:
            by_facility = group_df['facility'].value_counts().to_dict()
        
        if 'reprint_reason' in group_df.columns:
            by_reason = group_df['reprint_reason'].value_counts().to_dict()
        
        trend_points.append(TrendDataPoint(
            date=period if isinstance(period, datetime) else datetime.combine(period, datetime.min.time()),
            count=len(group_df),
            by_product=by_product,
            by_facility=by_facility,
            by_reason=by_reason
        ))
    
    return sorted(trend_points, key=lambda x: x.date)

