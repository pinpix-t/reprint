import os
import sys
from dotenv import load_dotenv
from typing import List

load_dotenv()

# SECURITY: Never hardcode secrets - require environment variables
# Note: Supabase is now optional - CSV is the primary data source
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "")

# Supabase is optional now (CSV is primary data source)
# Only warn if Supabase is configured but incomplete
if (SUPABASE_URL or SUPABASE_KEY) and not (SUPABASE_URL and SUPABASE_KEY):
    print(
        "WARNING: Supabase credentials are incomplete. "
        "Using CSV file as data source.",
        file=sys.stderr
    )

# Optional: Warn if Freshdesk is configured but API key is missing
if FRESHDESK_DOMAIN and not FRESHDESK_API_KEY:
    print(
        "WARNING: FRESHDESK_DOMAIN is set but FRESHDESK_API_KEY is missing. "
        "Freshdesk integration will not work.",
        file=sys.stderr
    )

# CORS configuration - restrict to specific origins
_cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_origins_str.split(",") if origin.strip()]

# API configuration
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "1000"))

