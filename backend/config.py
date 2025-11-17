import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

# SECURITY: Never hardcode secrets - require environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "")

# Validate required secrets
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is required")

# CORS configuration - restrict to specific origins
_cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_origins_str.split(",") if origin.strip()]

# API configuration
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "1000"))

