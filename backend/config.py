import os
import sys
from dotenv import load_dotenv
from typing import List

load_dotenv()

# SECURITY: Never hardcode secrets - require environment variables
# Fail fast if required secrets are missing
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "")

# Validate required secrets - fail immediately if missing
missing_secrets = []

if not SUPABASE_URL:
    missing_secrets.append("SUPABASE_URL")
if not SUPABASE_KEY:
    missing_secrets.append("SUPABASE_KEY")

if missing_secrets:
    error_msg = (
        f"CRITICAL: Required environment variables are missing: {', '.join(missing_secrets)}\n"
        f"Please set these variables before starting the application.\n"
        f"Example: export SUPABASE_URL='your-url' && export SUPABASE_KEY='your-key'"
    )
    print(error_msg, file=sys.stderr)
    sys.exit(1)

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

