from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd
from dateutil import parser
import logging

logger = logging.getLogger(__name__)

def parse_date(date_str: Optional[str], timezone_aware: bool = False) -> Optional[datetime]:
    """
    Parse date string to datetime object with proper timezone handling.
    FIXED: Consistent date parsing with timezone awareness and DD/MM/YYYY support.
    """
    if not date_str:
        return None
    
    try:
        # Handle DD/MM/YYYY format (common in CSV and Supabase text fields)
        # Check if it looks like DD/MM/YYYY (has / and first part is 1-31)
        if '/' in date_str:
            parts = date_str.split(' ')
            date_part = parts[0]
            date_components = date_part.split('/')
            if len(date_components) == 3:
                try:
                    first_part = int(date_components[0])
                    # If first part is 1-31, it's likely DD/MM/YYYY
                    if 1 <= first_part <= 31:
                        time_part = parts[1] if len(parts) > 1 else None
                        
                        try:
                            day, month, year = date_part.split('/')
                            year_int = int(year)
                            month_int = int(month)
                            day_int = int(day)
                            
                            # Handle 2-digit years
                            if year_int < 100:
                                year_int += 2000 if year_int < 50 else 1900
                            
                            if time_part:
                                time_parts = time_part.split(':')
                                hour = int(time_parts[0])
                                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                                dt = datetime(year_int, month_int, day_int, hour, minute)
                            else:
                                dt = datetime(year_int, month_int, day_int)
                            
                            # Make timezone-aware if requested (default to UTC)
                            if timezone_aware and dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            
                            return dt
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Failed to parse date format DD/MM/YYYY: {date_str}, error: {e}")
                            # Fall through to parser.parse
                except ValueError:
                    # Not a number, fall through to parser.parse
                    pass
        
        # Use dateutil parser for ISO and other formats
        # Note: dateutil might misinterpret DD/MM/YYYY as MM/DD/YYYY
        # So we try to parse with dayfirst=True for ambiguous dates
        try:
            dt = parser.parse(date_str, dayfirst=True)
        except:
            dt = parser.parse(date_str)
        
        # Ensure timezone awareness
        if timezone_aware and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        elif not timezone_aware and dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        
        return dt
    except Exception as e:
        logger.warning(f"Failed to parse date: {date_str}, error: {e}")
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

