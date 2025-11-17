# Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account with reprint and review tables
- Freshdesk API access (optional)

## Setup

1. **Install backend dependencies:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

3. **Configure environment variables:**
   - Backend: Create `.env` file in `backend/` directory (see `backend/.env.example`)
   - Frontend: Create `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Running Locally

1. **Start backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. **Start frontend (in new terminal):**
```bash
cd frontend
npm run dev
```

3. **Access dashboard:**
   - Open http://localhost:3000 in your browser

## Key Features

### Overview Tab
- Top-level metrics (total reprints, top products, facilities, reasons)
- Trend charts
- Distribution visualizations

### Query & Explore Tab
- Filter by date range, facility, product type
- Compare with previous periods
- Drill down into specific facilities or products
- Export data

### Review Insights Tab
- Review analysis with NLP
- Product mentions and quality concerns
- Sentiment breakdown
- Trending issues

## API Endpoints

### Reprints
- `GET /api/reprints/overview?days=7` - Overview metrics
- `GET /api/reprints/products` - Product metrics
- `GET /api/reprints/facilities` - Facility metrics
- `GET /api/reprints/trend?start_date=...&end_date=...` - Trend data
- `GET /api/reprints/facility/{facility}?days=30` - Facility drilldown
- `GET /api/reprints/product/{product}?days=30` - Product drilldown

### Reviews
- `GET /api/reviews/summary?days=7` - Review summary
- `GET /api/reviews/analyze?start_date=...&end_date=...` - Review analysis

### Freshdesk
- `GET /api/freshdesk/stats?days=30` - Freshdesk statistics
- `GET /api/freshdesk/tickets/match?days=30` - Match tickets to reprints

## Scheduled Jobs

Run daily refresh:
```bash
cd backend
python jobs/daily_refresh.py
```

Or use GitHub Actions (see `.github/workflows/daily-refresh.yml`)

## Deployment

See `DEPLOYMENT.md` for detailed deployment instructions.

## Notes

- The system will fallback to reading `BO_reprints_rows.csv` if Supabase connection fails
- Adjust table names in `backend/utils/db_access.py` if your Supabase tables have different names
- Configure Freshdesk domain in environment variables

