from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from dateutil import parser

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        # Handle DD/MM/YYYY format
        if '/' in date_str:
            parts = date_str.split(' ')
            date_part = parts[0]
            time_part = parts[1] if len(parts) > 1 else None
            day, month, year = date_part.split('/')
            if time_part:
                hour, minute = time_part.split(':')
                return datetime(int(year), int(month), int(day), int(hour), int(minute))
            return datetime(int(year), int(month), int(day))
        return parser.parse(date_str)
    except:
        return None

def normalize_facility_name(facility: Optional[str]) -> str:
    """Normalize facility names."""
    if not facility:
        return "Unknown"
    return facility.strip()

def normalize_product_type(product: Optional[str]) -> str:
    """Normalize product type names."""
    if not product:
        return "Unknown"
    return product.strip()

def normalize_reprint_reason(reason: Optional[str]) -> str:
    """Normalize reprint reason names."""
    if not reason:
        return "Unknown"
    return reason.strip()

def process_reprint_data(data: List[Dict]) -> pd.DataFrame:
    """Process raw reprint data into normalized DataFrame."""
    df = pd.DataFrame(data)
    
    # Parse dates
    if 'Requested date' in df.columns:
        df['requested_date'] = df['Requested date'].apply(parse_date)
    if 'Order Date' in df.columns:
        df['order_date'] = df['Order Date'].apply(parse_date)
    if 'Authorized Date' in df.columns:
        df['authorized_date'] = df['Authorized Date'].apply(parse_date)
    if 'ActualCONumberDispatchedDate' in df.columns:
        df['dispatched_date'] = df['ActualCONumberDispatchedDate'].apply(parse_date)
    if 'RMACONumberDispatchedDate' in df.columns:
        df['rma_dispatched_date'] = df['RMACONumberDispatchedDate'].apply(parse_date)
    
    # Normalize text fields
    if 'Product Type' in df.columns:
        df['product_type'] = df['Product Type'].apply(normalize_product_type)
    if 'Sub Type' in df.columns:
        df['sub_type'] = df['Sub Type'].apply(lambda x: x.strip() if x else "Unknown")
    if 'Reprint Reason' in df.columns:
        df['reprint_reason'] = df['Reprint Reason'].apply(normalize_reprint_reason)
    if 'ActualFacilityName' in df.columns:
        df['facility'] = df['ActualFacilityName'].apply(normalize_facility_name)
    elif 'Reprinted Facility Name' in df.columns:
        df['facility'] = df['Reprinted Facility Name'].apply(normalize_facility_name)
    if 'Shipping Country' in df.columns:
        df['shipping_country'] = df['Shipping Country'].apply(lambda x: x.strip() if x else "Unknown")
    if 'Order Value' in df.columns:
        df['order_value'] = pd.to_numeric(df['Order Value'], errors='coerce').fillna(0)
    
    return df

