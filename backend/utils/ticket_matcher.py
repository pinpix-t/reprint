from typing import List, Dict, Optional
from services.freshdesk_client import extract_order_number
from utils.db_access import get_reprints
import pandas as pd

def match_tickets_to_reprints(tickets: List[Dict]) -> List[Dict]:
    """Match Freshdesk tickets to reprint records."""
    matched = []
    
    for ticket in tickets:
        order_number = extract_order_number(ticket)
        
        if not order_number:
            continue
        
        # Search for reprint with matching order number
        # Note: Adjust column name based on your schema
        try:
            df = get_reprints()
            if not df.empty and 'Order Number' in df.columns:
                matching_reprints = df[df['Order Number'] == order_number]
                
                if not matching_reprints.empty:
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
            print(f"Error matching ticket {ticket.get('id')}: {e}")
            continue
    
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

