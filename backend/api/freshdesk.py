from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
from services.freshdesk_client import fetch_tickets, filter_quality_tickets, fetch_ticket
from utils.ticket_matcher import match_tickets_to_reprints, get_ticket_reprint_stats

router = APIRouter(prefix="/api/freshdesk", tags=["freshdesk"])

@router.get("/tickets")
async def get_tickets(
    status: Optional[int] = Query(None, description="Ticket status"),
    priority: Optional[int] = Query(None, description="Ticket priority"),
    days: int = Query(30, description="Fetch tickets updated in last N days"),
    quality_only: bool = Query(True, description="Filter for quality-related tickets only")
):
    """Fetch tickets from Freshdesk."""
    updated_since = datetime.now() - timedelta(days=days)
    
    tickets = fetch_tickets(
        status=status,
        priority=priority,
        updated_since=updated_since
    )
    
    if quality_only:
        tickets = filter_quality_tickets(tickets)
    
    return {
        "count": len(tickets),
        "tickets": tickets
    }

@router.get("/tickets/{ticket_id}")
async def get_ticket_details(ticket_id: int):
    """Get details of a specific ticket."""
    ticket = fetch_ticket(ticket_id)
    
    if not ticket:
        return {"error": "Ticket not found"}
    
    return ticket

@router.get("/tickets/match")
async def match_tickets(
    days: int = Query(30, description="Match tickets from last N days")
):
    """Match Freshdesk tickets to reprint records."""
    updated_since = datetime.now() - timedelta(days=days)
    tickets = fetch_tickets(updated_since=updated_since)
    quality_tickets = filter_quality_tickets(tickets)
    
    matches = match_tickets_to_reprints(quality_tickets)
    
    return {
        "total_tickets": len(quality_tickets),
        "matched": len(matches),
        "matches": matches
    }

@router.get("/stats")
async def get_freshdesk_stats(
    days: int = Query(30, description="Analyze tickets from last N days")
):
    """Get statistics about Freshdesk tickets and their relationship to reprints."""
    updated_since = datetime.now() - timedelta(days=days)
    tickets = fetch_tickets(updated_since=updated_since)
    quality_tickets = filter_quality_tickets(tickets)
    
    stats = get_ticket_reprint_stats(quality_tickets)
    
    return stats

