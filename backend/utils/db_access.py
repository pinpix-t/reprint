from typing import List, Dict, Optional
from datetime import datetime
import os
import sys
import logging
import threading
from functools import lru_cache

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.supabase_client import supabase
from utils.data_processor import process_reprint_data
from config import MAX_PAGE_SIZE
import pandas as pd

logger = logging.getLogger(__name__)

# Constants for table and column names
REPRINT_TABLE = "reprints"
REVIEW_TABLE = "reviews"
COLUMN_REQUESTED_DATE = "Requested date"
COLUMN_FACILITY_NAME = "ActualFacilityName"
COLUMN_PRODUCT_TYPE = "Product Type"
COLUMN_ORDER_NUMBER = "Order Number"

# Thread-safe CSV cache
_csv_lock = threading.Lock()
_csv_cache: Optional[pd.DataFrame] = None

def _validate_input_string(value: Optional[str], field_name: str) -> Optional[str]:
    """Validate and sanitize input strings to prevent injection."""
    if not value:
        return None
    # Remove any potential SQL injection characters
    # Supabase client handles this, but we validate anyway
    if any(char in value for char in [';', '--', '/*', '*/', 'xp_', 'sp_']):
        logger.warning(f"Potentially unsafe input detected in {field_name}")
        raise ValueError(f"Invalid characters in {field_name}")
    return value.strip()

def get_reprints(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    facility: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = MAX_PAGE_SIZE,
    offset: int = 0
) -> pd.DataFrame:
    """
    Fetch reprint data from Supabase with optional filters.
    Uses parameterized queries via Supabase client (safe from SQL injection).
    """
    try:
        # Validate and sanitize inputs
        facility = _validate_input_string(facility, "facility")
        product_type = _validate_input_string(product_type, "product_type")
        
        if limit > MAX_PAGE_SIZE:
            limit = MAX_PAGE_SIZE
            logger.warning(f"Limit exceeded MAX_PAGE_SIZE, capped at {MAX_PAGE_SIZE}")
        
        query = supabase.table(REPRINT_TABLE).select("*")
        
        # SECURITY: Supabase client uses parameterized queries
        if start_date:
            query = query.gte(COLUMN_REQUESTED_DATE, start_date.isoformat())
        if end_date:
            query = query.lte(COLUMN_REQUESTED_DATE, end_date.isoformat())
        if facility:
            query = query.eq(COLUMN_FACILITY_NAME, facility)
        if product_type:
            query = query.eq(COLUMN_PRODUCT_TYPE, product_type)
        
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        data = response.data if hasattr(response, 'data') else []
        
        if not data:
            return pd.DataFrame()
        
        return process_reprint_data(data)
    except Exception as e:
        logger.error(f"Error fetching reprints from Supabase: {e}", exc_info=True)
        raise

@lru_cache(maxsize=1)
def _load_csv_fallback() -> pd.DataFrame:
    """Load CSV data with caching and thread safety."""
    global _csv_cache
    
    with _csv_lock:
        if _csv_cache is not None:
            return _csv_cache
        
        try:
            import csv
            # Try multiple possible paths
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'BO_reprints_rows.csv'),
                'BO_reprints_rows.csv',
                os.path.join('..', 'BO_reprints_rows.csv')
            ]
            csv_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    csv_path = path
                    break
            
            if csv_path:
                data = []
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                _csv_cache = process_reprint_data(data)
                logger.info(f"Loaded {len(_csv_cache)} records from CSV fallback")
                return _csv_cache
        except Exception as e:
            logger.error(f"Error reading CSV fallback: {e}", exc_info=True)
        
        _csv_cache = pd.DataFrame()
        return _csv_cache

def get_all_reprints(use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch all reprint data from Supabase.
    Falls back to CSV if Supabase fails.
    """
    try:
        response = supabase.table(REPRINT_TABLE).select("*").execute()
        data = response.data if hasattr(response, 'data') else []
        
        if not data:
            logger.warning("No data from Supabase, falling back to CSV")
            return _load_csv_fallback() if use_cache else pd.DataFrame()
        
        return process_reprint_data(data)
    except Exception as e:
        logger.error(f"Error fetching reprints from Supabase: {e}", exc_info=True)
        # Fallback: try to read from CSV if Supabase fails
        if use_cache:
            return _load_csv_fallback()
        return pd.DataFrame()

def get_reviews(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = MAX_PAGE_SIZE,
    offset: int = 0
) -> List[Dict]:
    """
    Fetch reviews from Supabase with optional date filters.
    Uses pagination to prevent memory issues.
    """
    try:
        if limit > MAX_PAGE_SIZE:
            limit = MAX_PAGE_SIZE
            logger.warning(f"Limit exceeded MAX_PAGE_SIZE, capped at {MAX_PAGE_SIZE}")
        
        query = supabase.table(REVIEW_TABLE).select("*")
        
        # SECURITY: Supabase client uses parameterized queries
        if start_date:
            query = query.gte("created_at", start_date.isoformat())
        if end_date:
            query = query.lte("created_at", end_date.isoformat())
        
        query = query.range(offset, offset + limit - 1)
        response = query.execute()
        
        return response.data if hasattr(response, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}", exc_info=True)
        return []

def get_review_text_fields() -> List[str]:
    """Get potential text field names from reviews table."""
    # Common field names for review text
    return ["review_text", "comment", "text", "content", "description", "body", "message"]

