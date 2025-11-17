# Deployment Guide

## Backend Deployment

The FastAPI backend can be deployed in several ways:

### Option 1: Vercel Serverless Functions

1. Create `api/` directory in project root
2. Create `api/index.py` that imports and exports the FastAPI app
3. Configure `vercel.json` to route `/api/*` to serverless functions

### Option 2: Separate API Hosting

Deploy to services like:
- Railway
- Render
- Fly.io
- AWS Lambda
- Google Cloud Run

Example for Railway/Render:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Option 3: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Deployment (Vercel)

1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to frontend directory: `cd frontend`
3. Deploy: `vercel`
4. Set environment variable: `NEXT_PUBLIC_API_URL` to your backend URL

Or connect your GitHub repo to Vercel for automatic deployments.

## Environment Variables

### Backend
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FRESHDESK_API_KEY`
- `FRESHDESK_DOMAIN`
- `CORS_ORIGINS`

### Frontend
- `NEXT_PUBLIC_API_URL`

## Scheduled Jobs

For daily/weekly refresh jobs, use:
- GitHub Actions (cron)
- Vercel Cron Jobs
- External cron service (cron-job.org)
- Cloud scheduler (AWS EventBridge, Google Cloud Scheduler)

Example GitHub Actions workflow:
```yaml
name: Daily Refresh
on:
  schedule:
    - cron: '0 2 * * *'
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python backend/jobs/daily_refresh.py
```

