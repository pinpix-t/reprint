import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jqzpyztivqshzzsfdecp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpxenB5enRpdnFzaHp6c2ZkZWNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MTE0NzUsImV4cCI6MjA2MDM4NzQ3NX0.RPUTHIa2KEfBry8_uGHQEhTOjwIE7Nns174TNqJnEPs")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY", "FfKH4xCLLoQSDKLfaXzu")
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

