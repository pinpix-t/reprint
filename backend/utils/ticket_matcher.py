from typing import List, Dict, Optional
import logging
from services.freshdesk_client import extract_order_number
from utils.db_access import get_all_reprints, COLUMN_ORDER_NUMBER
import pandas as pd

logger = logging.getLogger(__name__)

def match_tickets_to_reprints(tickets: List[Dict]) -> List[Dict]:
    """
    Match Freshdesk tickets to reprint records.
    FIXED: N+1 query problem - loads all reprints once and uses O(1) lookup.
    """
    matched = []
    
    if not tickets:
        return matched
    
    try:
        # PERFORMANCE FIX: Load all reprints once instead of per-ticket (N+1 problem)
        df = get_all_reprints()
        
        if df.empty or COLUMN_ORDER_NUMBER not in df.columns:
            logger.warning("No reprint data available for matching")
            return matched
        
        # Create O(1) lookup dictionary by order number
        # Handle multiple reprints per order number
        order_lookup: Dict[str, pd.DataFrame] = {}
        for order_num in df[COLUMN_ORDER_NUMBER].dropna().unique():
            order_lookup[str(order_num)] = df[df[COLUMN_ORDER_NUMBER] == order_num]
        
        logger.info(f"Created lookup for {len(order_lookup)} unique order numbers")
        
        # Match tickets using O(1) lookup
        for ticket in tickets:
            order_number = extract_order_number(ticket)
            
            if not order_number:
                continue
            
            try:
                # O(1) lookup instead of O(n) search
                matching_reprints = order_lookup.get(str(order_number))
                
                if matching_reprints is not None and not matching_reprints.empty:
                    # Use first match if multiple exist
                    reprint = matching_reprints.iloc[0].to_dict()
                    matched.append({
                        "ticket_id": ticket.get("id"),
                        "ticket_subject": ticket.get("subject"),
                        "ticket_status": ticket.get("status"),
                        "ticket_created": ticket.get("created_at"),
                        "order_number": order_number,
                        "reprint_id": reprint.get("id"),
                        "reprint_reason": reprint.get("Reprint Reason"),
                        "product_type": reprint.get("Product Type"),
                        "facility": reprint.get("ActualFacilityName") or reprint.get("Reprinted Facility Name")
                    })
            except Exception as e:
                logger.error(f"Error matching ticket {ticket.get('id')}: {e}", exc_info=True)
                continue
        
        logger.info(f"Matched {len(matched)} out of {len(tickets)} tickets")
        return matched
        
    except Exception as e:
        logger.error(f"Error in match_tickets_to_reprints: {e}", exc_info=True)
        return matched

def get_ticket_reprint_stats(tickets: List[Dict]) -> Dict:
    """Get statistics about tickets and their relationship to reprints."""
    matched = match_tickets_to_reprints(tickets)
    
    total_tickets = len(tickets)
    matched_count = len(matched)
    unmatched_count = total_tickets - matched_count
    
    # Group by product type
    product_counts = {}
    for match in matched:
        product = match.get("product_type", "Unknown")
        product_counts[product] = product_counts.get(product, 0) + 1
    
    # Group by facility
    facility_counts = {}
    for match in matched:
        facility = match.get("facility", "Unknown")
        facility_counts[facility] = facility_counts.get(facility, 0) + 1
    
    return {
        "total_tickets": total_tickets,
        "matched_tickets": matched_count,
        "unmatched_tickets": unmatched_count,
        "match_rate": (matched_count / total_tickets * 100) if total_tickets > 0 else 0,
        "by_product": product_counts,
        "by_facility": facility_counts,
        "matches": matched
    }

