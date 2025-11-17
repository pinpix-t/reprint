import requests
from typing import List, Dict, Optional
from datetime import datetime
from config import FRESHDESK_API_KEY, FRESHDESK_DOMAIN
import base64

def get_freshdesk_auth() -> str:
    """Get Freshdesk API authentication header."""
    api_key = FRESHDESK_API_KEY
    auth_string = f"{api_key}:X"
    return base64.b64encode(auth_string.encode()).decode()

def fetch_tickets(
    domain: Optional[str] = None,
    status: Optional[int] = None,
    priority: Optional[int] = None,
    updated_since: Optional[datetime] = None,
    limit: int = 100
) -> List[Dict]:
    """Fetch tickets from Freshdesk API."""
    if not domain:
        domain = FRESHDESK_DOMAIN
    
    if not domain:
        print("Warning: Freshdesk domain not configured")
        return []
    
    url = f"https://{domain}.freshdesk.com/api/v2/tickets"
    
    headers = {
        "Authorization": f"Basic {get_freshdesk_auth()}",
        "Content-Type": "application/json"
    }
    
    params = {
        "per_page": limit
    }
    
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if updated_since:
        params["updated_since"] = updated_since.isoformat()
    
    try:
        response = requests.get(url, headers=headers, params=params, auth=(FRESHDESK_API_KEY, "X"))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Freshdesk tickets: {e}")
        return []

def fetch_ticket(ticket_id: int, domain: Optional[str] = None) -> Optional[Dict]:
    """Fetch a specific ticket by ID."""
    if not domain:
        domain = FRESHDESK_DOMAIN
    
    if not domain:
        return None
    
    url = f"https://{domain}.freshdesk.com/api/v2/tickets/{ticket_id}"
    
    headers = {
        "Authorization": f"Basic {get_freshdesk_auth()}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, auth=(FRESHDESK_API_KEY, "X"))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Freshdesk ticket {ticket_id}: {e}")
        return None

def filter_quality_tickets(tickets: List[Dict]) -> List[Dict]:
    """Filter tickets related to quality/damage issues."""
    quality_keywords = [
        "damage", "damaged", "broken", "defect", "defective",
        "quality", "poor quality", "wrong", "missing", "incomplete",
        "reprint", "replacement", "refund"
    ]
    
    quality_tickets = []
    for ticket in tickets:
        subject = ticket.get("subject", "").lower()
        description = ticket.get("description", "").lower()
        tags = [tag.lower() for tag in ticket.get("tags", [])]
        
        text = f"{subject} {description} {' '.join(tags)}"
        
        if any(keyword in text for keyword in quality_keywords):
            quality_tickets.append(ticket)
    
    return quality_tickets

def extract_order_number(ticket: Dict) -> Optional[str]:
    """Extract order number from ticket."""
    # Check various fields for order number
    subject = ticket.get("subject", "")
    description = ticket.get("description", "")
    custom_fields = ticket.get("custom_fields", {})
    
    # Look for order number patterns
    import re
    order_patterns = [
        r'REZ\d+',
        r'RED\d+',
        r'REQ\d+',
        r'REP\d+',
        r'Order[:\s]+(\d+)',
        r'Order\s*#\s*(\d+)'
    ]
    
    text = f"{subject} {description} {str(custom_fields)}"
    for pattern in order_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0) if match.groups() == () else match.group(1)
    
    return None

