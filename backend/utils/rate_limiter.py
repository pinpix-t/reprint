"""
Rate limiting utilities for API endpoints.
Prevents abuse and ensures fair resource usage.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Default rate limits
DEFAULT_RATE_LIMIT = "100/hour"  # 100 requests per hour per IP
STRICT_RATE_LIMIT = "10/minute"  # 10 requests per minute for sensitive endpoints
RELAXED_RATE_LIMIT = "1000/hour"  # 1000 requests per hour for public endpoints

def get_rate_limit_handler():
    """Get rate limit exceeded handler."""
    return _rate_limit_exceeded_handler

