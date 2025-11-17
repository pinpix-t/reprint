from typing import List, Dict, Optional
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.supabase_client import supabase
from utils.data_processor import process_reprint_data
import pandas as pd

# Table names - adjust if different in your Supabase
REPRINT_TABLE = "reprints"  # or "reprint_data" or whatever your table is named
REVIEW_TABLE = "reviews"  # adjust as needed

def get_reprints(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    facility: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = 10000
) -> pd.DataFrame:
    """Fetch reprint data from Supabase with optional filters."""
    query = supabase.table(REPRINT_TABLE).select("*")
    
    if start_date:
        query = query.gte("Requested date", start_date.isoformat())
    if end_date:
        query = query.lte("Requested date", end_date.isoformat())
    if facility:
        query = query.eq("ActualFacilityName", facility)
    if product_type:
        query = query.eq("Product Type", product_type)
    
    query = query.limit(limit)
    
    response = query.execute()
    data = response.data if hasattr(response, 'data') else []
    
    if not data:
        # If table doesn't exist or is empty, return empty DataFrame with expected columns
        return pd.DataFrame()
    
    return process_reprint_data(data)

def get_all_reprints() -> pd.DataFrame:
    """Fetch all reprint data from Supabase."""
    try:
        response = supabase.table(REPRINT_TABLE).select("*").execute()
        data = response.data if hasattr(response, 'data') else []
        
        if not data:
            return pd.DataFrame()
        
        return process_reprint_data(data)
    except Exception as e:
        print(f"Error fetching reprints: {e}")
        # Fallback: try to read from CSV if Supabase fails
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
                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                return process_reprint_data(data)
        except Exception as e:
            print(f"Error reading CSV fallback: {e}")
            return pd.DataFrame()

def get_reviews(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 10000
) -> List[Dict]:
    """Fetch reviews from Supabase with optional date filters."""
    try:
        query = supabase.table(REVIEW_TABLE).select("*")
        
        if start_date:
            # Adjust column name based on your schema
            query = query.gte("created_at", start_date.isoformat())
        if end_date:
            query = query.lte("created_at", end_date.isoformat())
        
        query = query.limit(limit)
        response = query.execute()
        
        return response.data if hasattr(response, 'data') else []
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return []

def get_review_text_fields() -> List[str]:
    """Get potential text field names from reviews table."""
    # Common field names for review text
    return ["review_text", "comment", "text", "content", "description", "body", "message"]

