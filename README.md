# Quality/Damage Analysis Dashboard

Automated quality and damage analysis system with review analysis, reprint report analytics, and Freshdesk integration.

## Setup

### Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

3. Set up environment variables (see `backend/.env.example`)

4. Run the FastAPI server:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
cd frontend
npm run dev
```

## Deployment

Frontend deploys to Vercel. Backend can be deployed as Vercel serverless functions or separate API host.

