from fastapi import APIRouter
from utils.db_access import get_all_reprints
import pandas as pd

router = APIRouter(prefix="/api", tags=["debug"])

@router.get("/dates/check")
async def check_dates():
    """Check the latest dates for both Requested date and Order Date."""
    all_data = get_all_reprints(use_cache=False)
    
    if all_data.empty:
        return {
            "error": "No data available",
            "requested_date": None,
            "order_date": None
        }
    
    result = {}
    
    # Check requested_date
    if 'requested_date' in all_data.columns:
        valid_requested = all_data['requested_date'].dropna()
        if len(valid_requested) > 0:
            result['requested_date'] = {
                "latest": valid_requested.max().isoformat() if pd.notna(valid_requested.max()) else None,
                "earliest": valid_requested.min().isoformat() if pd.notna(valid_requested.min()) else None,
                "total_records": len(valid_requested),
                "null_count": all_data['requested_date'].isna().sum()
            }
        else:
            result['requested_date'] = {
                "latest": None,
                "earliest": None,
                "total_records": 0,
                "null_count": len(all_data)
            }
    else:
        result['requested_date'] = {"error": "Column not found"}
    
    # Check order_date
    if 'order_date' in all_data.columns:
        valid_order = all_data['order_date'].dropna()
        if len(valid_order) > 0:
            result['order_date'] = {
                "latest": valid_order.max().isoformat() if pd.notna(valid_order.max()) else None,
                "earliest": valid_order.min().isoformat() if pd.notna(valid_order.min()) else None,
                "total_records": len(valid_order),
                "null_count": all_data['order_date'].isna().sum()
            }
        else:
            result['order_date'] = {
                "latest": None,
                "earliest": None,
                "total_records": 0,
                "null_count": len(all_data)
            }
    else:
        result['order_date'] = {"error": "Column not found"}
    
    return result

