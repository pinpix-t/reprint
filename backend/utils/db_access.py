from typing import List, Dict, Optional
from datetime import datetime
import os
import sys
import logging
import threading
import fcntl
from functools import lru_cache

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.supabase_client import supabase
SUPABASE_AVAILABLE = True

from utils.data_processor import process_reprint_data
from config import MAX_PAGE_SIZE
import pandas as pd

logger = logging.getLogger(__name__)

# Constants for table and column names
REPRINT_TABLE = "BO_reprints"
REVIEW_TABLE = "reviews"
COLUMN_REQUESTED_DATE = "Requested date"
COLUMN_FACILITY_NAME = "ActualFacilityName"
COLUMN_PRODUCT_TYPE = "Product Type"
COLUMN_ORDER_NUMBER = "Order Number"

# Thread-safe CSV cache with file locking
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
    Falls back to CSV if Supabase fails.
    """
    try:
        # Validate and sanitize inputs
        facility = _validate_input_string(facility, "facility")
        product_type = _validate_input_string(product_type, "product_type")
        
        if limit > MAX_PAGE_SIZE:
            limit = MAX_PAGE_SIZE
            logger.warning(f"Limit exceeded MAX_PAGE_SIZE, capped at {MAX_PAGE_SIZE}")
        
        # Try Supabase first
        if SUPABASE_AVAILABLE and supabase:
            try:
                query = supabase.table(REPRINT_TABLE).select("*")
                
                # SECURITY: Supabase client uses parameterized queries
                # Note: Dates in Supabase may be stored as text in DD/MM/YYYY format
                # We'll fetch data and filter in Python to handle any date format
                # This ensures compatibility regardless of how Supabase stores the dates
                
                # Apply non-date filters directly in query (more efficient)
                if facility:
                    query = query.eq(COLUMN_FACILITY_NAME, facility)
                if product_type:
                    query = query.eq(COLUMN_PRODUCT_TYPE, product_type)
                
                # Fetch data (we'll filter by date in Python if needed)
                # Increase limit if date filtering is needed (we'll filter after)
                fetch_limit = limit * 10 if (start_date or end_date) else limit
                query = query.range(offset, offset + fetch_limit - 1)
                
                response = query.execute()
                data = response.data if hasattr(response, 'data') else []
                
                logger.info(f"Fetched {len(data)} raw records from Supabase table {REPRINT_TABLE}")
                
                if data:
                    # Process data to DataFrame
                    df = process_reprint_data(data)
                    logger.info(f"Processed {len(df)} records into DataFrame. Columns: {df.columns.tolist()}")
                    
                    # Apply date filters in Python (handles any date format)
                    if start_date or end_date:
                        if 'requested_date' in df.columns:
                            initial_count = len(df)
                            # Debug: Show sample dates before filtering
                            if initial_count > 0:
                                sample_dates = df['requested_date'].dropna().head(5).tolist()
                                logger.info(f"Sample requested_date values before filtering: {sample_dates}")
                                logger.info(f"Date range in data: min={df['requested_date'].min()}, max={df['requested_date'].max()}")
                            
                            if start_date:
                                # Check how many dates are None/NaN
                                null_dates = df['requested_date'].isna().sum()
                                if null_dates > 0:
                                    logger.warning(f"{null_dates} records have null requested_date")
                                
                                # Convert timezone-aware datetime to naive if needed (DataFrame dates are naive)
                                if start_date.tzinfo is not None:
                                    start_date = start_date.replace(tzinfo=None)
                                
                                df = df[df['requested_date'] >= start_date]
                                logger.info(f"After start_date filter ({start_date}): {len(df)} records (from {initial_count})")
                            if end_date:
                                # Include full end date
                                from datetime import timedelta
                                end_date_inclusive = end_date + timedelta(days=1)
                                
                                # Convert timezone-aware datetime to naive if needed (DataFrame dates are naive)
                                if end_date_inclusive.tzinfo is not None:
                                    end_date_inclusive = end_date_inclusive.replace(tzinfo=None)
                                
                                before_end_filter = len(df)
                                df = df[df['requested_date'] < end_date_inclusive]
                                logger.info(f"After end_date filter (<{end_date_inclusive}): {len(df)} records (from {before_end_filter})")
                        else:
                            logger.warning(f"Column 'requested_date' not found in processed data. Available columns: {df.columns.tolist()}")
                            logger.warning("Date filtering skipped - will return all data")
                    
                    # Apply limit after filtering
                    if len(df) > limit:
                        df = df.head(limit)
                        logger.info(f"Limited results to {limit} records")
                    
                    logger.info(f"Returning {len(df)} records after filtering")
                    return df
                else:
                    logger.warning(f"No data returned from Supabase table {REPRINT_TABLE}, falling back to CSV")
            except Exception as e:
                logger.error(f"Error fetching reprints from Supabase: {e}", exc_info=True)
                logger.info("Falling back to CSV file")
        
        # Fallback to CSV
        df = _load_csv_fallback()
        
        if df.empty:
            logger.warning("No data available from CSV file")
            return pd.DataFrame()
        
        logger.info(f"Loaded {len(df)} records from CSV file")
        
        # Apply filters in Python
        initial_count = len(df)
        
        # Filter by facility
        if facility:
            if 'facility' in df.columns:
                df = df[df['facility'] == facility]
                logger.info(f"After facility filter ({facility}): {len(df)} records (from {initial_count})")
            else:
                logger.warning(f"Column 'facility' not found for filtering")
        
        # Filter by product type
        if product_type:
            if 'product_type' in df.columns:
                df = df[df['product_type'] == product_type]
                logger.info(f"After product_type filter ({product_type}): {len(df)} records")
            else:
                logger.warning(f"Column 'product_type' not found for filtering")
        
        # Apply date filters
        if start_date or end_date:
            if 'requested_date' in df.columns:
                before_date_filter = len(df)
                # Debug: Show sample dates before filtering
                if before_date_filter > 0:
                    sample_dates = df['requested_date'].dropna().head(5).tolist()
                    logger.info(f"Sample requested_date values before filtering: {sample_dates}")
                    logger.info(f"Date range in data: min={df['requested_date'].min()}, max={df['requested_date'].max()}")
                
                if start_date:
                    # Check how many dates are None/NaN
                    null_dates = df['requested_date'].isna().sum()
                    if null_dates > 0:
                        logger.warning(f"{null_dates} records have null requested_date")
                    
                    # Convert timezone-aware datetime to naive if needed (DataFrame dates are naive)
                    if start_date.tzinfo is not None:
                        start_date = start_date.replace(tzinfo=None)
                    
                    df = df[df['requested_date'] >= start_date]
                    logger.info(f"After start_date filter ({start_date}): {len(df)} records (from {before_date_filter})")
                if end_date:
                    # Include full end date
                    from datetime import timedelta
                    end_date_inclusive = end_date + timedelta(days=1)
                    
                    # Convert timezone-aware datetime to naive if needed (DataFrame dates are naive)
                    if end_date_inclusive.tzinfo is not None:
                        end_date_inclusive = end_date_inclusive.replace(tzinfo=None)
                    
                    before_end_filter = len(df)
                    df = df[df['requested_date'] < end_date_inclusive]
                    logger.info(f"After end_date filter (<{end_date_inclusive}): {len(df)} records (from {before_end_filter})")
            else:
                logger.warning(f"Column 'requested_date' not found in processed data. Available columns: {df.columns.tolist()}")
                logger.warning("Date filtering skipped - will return all data")
        
        # Apply pagination (offset and limit)
        if offset > 0:
            df = df.iloc[offset:]
        if len(df) > limit:
            df = df.head(limit)
            logger.info(f"Limited results to {limit} records (offset: {offset})")
        
        logger.info(f"Returning {len(df)} records after filtering")
        return df
    except Exception as e:
        logger.error(f"Error fetching reprints: {e}", exc_info=True)
        raise

@lru_cache(maxsize=1)
def _load_csv_fallback() -> pd.DataFrame:
    """
    Load CSV data with caching, thread safety, and file locking.
    Uses fcntl for cross-process file locking on Unix systems.
    """
    global _csv_cache
    
    with _csv_lock:
        if _csv_cache is not None:
            return _csv_cache
        
        try:
            import csv
            # Try multiple possible paths for CSV file
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'BO_reprints_rows.csv'),  # Root directory
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'BO_reprints_rows.csv'),  # Backend directory
                'BO_reprints_rows.csv',  # Current directory
                os.path.join('..', 'BO_reprints_rows.csv'),  # Parent directory
                '/app/BO_reprints_rows.csv',  # Docker container root
                '/app/backend/BO_reprints_rows.csv',  # Docker backend directory
            ]
            csv_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    csv_path = path
                    break
            
            if csv_path:
                data = []
                # SECURITY: Use file locking to prevent concurrent access issues
                # fcntl provides advisory file locking (works across processes)
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        # Acquire exclusive lock (non-blocking)
                        try:
                            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            logger.debug(f"Acquired file lock for {csv_path}")
                        except BlockingIOError:
                            # Another process has the lock, wait briefly
                            logger.warning(f"File {csv_path} is locked, waiting...")
                            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Blocking lock
                        
                        try:
                            reader = csv.DictReader(f)
                            data = list(reader)
                        finally:
                            # Release lock
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                            logger.debug(f"Released file lock for {csv_path}")
                except (OSError, IOError) as e:
                    # Fallback for systems without fcntl (e.g., Windows)
                    # Use thread lock only (already held by _csv_lock)
                    logger.warning(f"File locking not available ({e}), using thread lock only")
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
    Fetch all reprint data from Supabase with pagination.
    Falls back to CSV if Supabase fails.
    """
    try:
        # Try Supabase first
        if SUPABASE_AVAILABLE and supabase:
            try:
                # Supabase has a default limit, so we need to paginate to get ALL records
                all_data = []
                page_size = 1000  # Supabase max per request
                offset = 0
                
                while True:
                    response = supabase.table(REPRINT_TABLE).select("*").range(offset, offset + page_size - 1).execute()
                    page_data = response.data if hasattr(response, 'data') else []
                    
                    if not page_data:
                        break
                    
                    all_data.extend(page_data)
                    logger.info(f"Fetched {len(page_data)} records from Supabase (offset {offset}, total so far: {len(all_data)})")
                    
                    # If we got fewer than page_size, we've reached the end
                    if len(page_data) < page_size:
                        break
                    
                    offset += page_size
                
                if all_data:
                    logger.info(f"Fetched {len(all_data)} total records from Supabase")
                    return process_reprint_data(all_data)
                else:
                    logger.warning("No data from Supabase, falling back to CSV")
            except Exception as e:
                logger.error(f"Error fetching reprints from Supabase: {e}", exc_info=True)
                logger.info("Falling back to CSV file")
        
        # Fallback: try to read from CSV if Supabase fails
        if use_cache:
            return _load_csv_fallback()
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching reprints: {e}", exc_info=True)
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

