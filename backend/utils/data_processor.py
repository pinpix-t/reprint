from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd
from dateutil import parser
import logging

logger = logging.getLogger(__name__)

def parse_date(date_str: Optional[str], timezone_aware: bool = False, date_format: str = "DD/MM/YYYY") -> Optional[datetime]:
    """
    Parse date string to datetime object with proper timezone handling.
    Supports both DD/MM/YYYY and MM/DD/YYYY formats.
    
    Args:
        date_str: Date string to parse
        timezone_aware: Whether to make the datetime timezone-aware
        date_format: Expected format - "DD/MM/YYYY" or "MM/DD/YYYY"
    """
    if not date_str:
        return None
    
    try:
        # Handle DD/MM/YYYY or MM/DD/YYYY format
        if '/' in date_str:
            parts = date_str.split(' ')
            date_part = parts[0]
            date_components = date_part.split('/')
            if len(date_components) == 3:
                try:
                    time_part = parts[1] if len(parts) > 1 else None
                    
                    if date_format == "DD/MM/YYYY":
                        # Parse as DD/MM/YYYY
                        day, month, year = date_part.split('/')
                    elif date_format == "MM/DD/YYYY":
                        # Parse as MM/DD/YYYY
                        month, day, year = date_part.split('/')
                    else:
                        # Try to auto-detect: if first part > 12, it's likely DD/MM/YYYY
                        first_part = int(date_components[0])
                        second_part = int(date_components[1])
                        
                        if first_part > 12:
                            # First part is day (DD/MM/YYYY)
                            day, month, year = date_part.split('/')
                        elif second_part > 12:
                            # Second part is day (MM/DD/YYYY)
                            month, day, year = date_part.split('/')
                        else:
                            # Ambiguous - default to DD/MM/YYYY (most common in this dataset)
                            day, month, year = date_part.split('/')
                    
                    year_int = int(year)
                    month_int = int(month)
                    day_int = int(day)
                    
                    # Handle 2-digit years
                    if year_int < 100:
                        year_int += 2000 if year_int < 50 else 1900
                    
                    # Validate date
                    if not (1 <= month_int <= 12 and 1 <= day_int <= 31):
                        raise ValueError(f"Invalid date: month={month_int}, day={day_int}")
                    
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
                    logger.warning(f"Failed to parse date format {date_format}: {date_str}, error: {e}")
                    # Fall through to parser.parse
            except ValueError:
                # Not a number, fall through to parser.parse
                pass
        
        # Use dateutil parser for ISO and other formats
        # Use dayfirst=True for DD/MM/YYYY, dayfirst=False for MM/DD/YYYY
        try:
            if date_format == "DD/MM/YYYY":
                dt = parser.parse(date_str, dayfirst=True)
            elif date_format == "MM/DD/YYYY":
                dt = parser.parse(date_str, dayfirst=False)
            else:
                # Try both
                try:
                    dt = parser.parse(date_str, dayfirst=True)
                except:
                    dt = parser.parse(date_str, dayfirst=False)
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
    
    # Parse dates with correct format for each column
    # 'Requested date' is DD/MM/YYYY format
    if 'Requested date' in df.columns:
        df['requested_date'] = df['Requested date'].apply(lambda x: parse_date(x, date_format="DD/MM/YYYY"))
    # 'Order Date' is MM/DD/YYYY format
    if 'Order Date' in df.columns:
        df['order_date'] = df['Order Date'].apply(lambda x: parse_date(x, date_format="MM/DD/YYYY"))
    # Other dates - try to auto-detect format
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

