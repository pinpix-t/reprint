# Cron Job Setup Guide

## Overview

The application now includes a scheduled job that runs daily at **9 AM GMT** to refresh data from the past 24 hours and make it available in your dashboard.

## What It Does

- **Runs daily at 9 AM GMT**
- **Fetches all new data from past 24 hours** from:
  - Supabase (reprints)
  - Reviews
  - Freshdesk tickets
- **Refreshes the data cache** so your dashboard shows the latest information
- **Prevents duplicate runs** using job locking

## Setup on Railway

### Option 1: Separate Scheduler Service (Recommended)

1. **Create a new Railway service:**
   - Go to Railway dashboard
   - Click "New" → "Empty Service"
   - Connect to your GitHub repo: `pinpix-t/reprint`

2. **Configure the service:**
   - **Root Directory**: Leave empty (uses root `/`)
   - **Start Command**: 
     ```bash
     cd backend && source venv/bin/activate && python -m jobs.scheduler
     ```
   - Or Railway should auto-detect `Procfile.scheduler`

3. **Set Environment Variables:**
   - Copy all environment variables from your main API service:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `FRESHDESK_API_KEY` (optional)
     - `FRESHDESK_DOMAIN` (optional)
     - `CRON_SECRET` (optional, for HTTP endpoint security)

4. **Deploy:**
   - Railway will automatically build and deploy
   - Check logs to see: "Scheduler started" and "Scheduler configured: Daily refresh at 9 AM GMT"

### Option 2: HTTP Endpoint (Alternative)

If you prefer to use an external cron service (like GitHub Actions or cron-job.org):

1. **Set `CRON_SECRET` environment variable** in Railway:
   ```
   CRON_SECRET=your-secret-key-here
   ```

2. **Call the endpoint at 9 AM GMT:**
   ```bash
   curl -X POST https://your-railway-url.railway.app/api/jobs/refresh-24h \
     -H "X-Cron-Secret: your-secret-key-here"
   ```

3. **Schedule it:**
   - **GitHub Actions**: Create `.github/workflows/daily-refresh.yml`
   - **cron-job.org**: Set up a daily cron job
   - **Railway Cron**: If Railway supports cron jobs, use that

## Testing Locally

### Test the scheduler:
```bash
cd backend
python -m jobs.scheduler
```

You should see:
```
Scheduler configured: Daily refresh at 9 AM GMT, Weekly report on Mondays at 9 AM GMT
Scheduler started. Press Ctrl+C to stop.
Current time: 2025-01-30 12:00:00+00:00
```

### Test the refresh manually:
```bash
cd backend
python -m jobs.daily_refresh
```

### Test the HTTP endpoint (if API is running):
```bash
curl -X POST http://localhost:8000/api/jobs/refresh-24h \
  -H "X-Cron-Secret: your-secret"
```

## Monitoring

### Check scheduler logs in Railway:
- Look for: "Starting daily refresh for past 24 hours (9 AM GMT)..."
- Should see: "Daily refresh completed at 9 AM GMT"
- Check for any errors

### Check job status:
```bash
curl https://your-railway-url.railway.app/api/jobs/status
```

Returns:
```json
{
  "status": "active",
  "message": "Scheduler is running",
  "next_refresh": "9 AM GMT daily"
}
```

## How It Works

1. **Scheduler runs continuously** (separate Railway service)
2. **At 9 AM GMT**, it triggers `run_daily_refresh()`
3. **Job locking prevents duplicates** if the job is already running
4. **Data is refreshed** from all sources (Supabase, Reviews, Freshdesk)
5. **Cache is updated** so your dashboard shows the latest data
6. **Users can query past 24 hours** using:
   - `GET /api/reprints/overview?days=1`
   - Or date range: `?start_date=2025-01-30&end_date=2025-01-31`

## Troubleshooting

### Scheduler not running:
- Check Railway logs for errors
- Verify environment variables are set
- Ensure the start command is correct

### Data not refreshing:
- Check scheduler logs for "Daily refresh completed"
- Verify Supabase connection
- Check if job locking is preventing runs (look for "already running")

### Wrong timezone:
- The scheduler uses GMT/UTC
- 9 AM GMT = 9:00 UTC
- Adjust if needed in `backend/jobs/scheduler.py`:
  ```python
  schedule.every().day.at("09:00").do(run_daily_refresh)
  ```

## Files Modified

- `backend/jobs/scheduler.py` - Updated to run at 9 AM GMT
- `backend/jobs/daily_refresh.py` - Focuses on past 24 hours
- `backend/api/jobs.py` - New HTTP endpoint for manual triggers
- `backend/main.py` - Added jobs router
- `Procfile.scheduler` - Railway start command for scheduler

