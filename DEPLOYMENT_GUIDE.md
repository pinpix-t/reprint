# Complete Deployment Guide

This guide covers deploying both the backend API and frontend dashboard.

## Prerequisites

- GitHub repository: `https://github.com/pinpix-t/reprint.git`
- Supabase credentials (URL and API key)
- Freshdesk API key (optional)
- Vercel account (for frontend - free tier available)
- Backend hosting (Railway, Render, Fly.io, or similar)

## Step 1: Deploy Backend API

### Option A: Railway (Recommended - Easiest)

1. **Sign up/Login**: Go to [railway.app](https://railway.app) and sign in with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `pinpix-t/reprint` repository

3. **Configure Service**:
   - Railway will auto-detect Python
   - Set root directory to `/backend`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**:
   ```
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   FRESHDESK_API_KEY=your-freshdesk-key (optional)
   FRESHDESK_DOMAIN=your-domain.freshdesk.com (optional)
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   API_TIMEOUT_SECONDS=30
   MAX_PAGE_SIZE=1000
   ```

5. **Deploy**:
   - Railway will automatically build and deploy
   - Note the generated URL (e.g., `https://your-app.railway.app`)

### Option B: Render

1. **Create Web Service**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo

2. **Configure**:
   - **Name**: `reprint-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** (same as Railway above)

4. **Deploy**: Render will build and deploy automatically

### Option C: Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Create App**:
   ```bash
   cd backend
   fly launch
   ```

4. **Set Secrets**:
   ```bash
   fly secrets set SUPABASE_URL=your-url
   fly secrets set SUPABASE_KEY=your-key
   fly secrets set CORS_ORIGINS=https://your-frontend.vercel.app
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

### Option D: Docker (Any Platform)

1. **Build Image**:
   ```bash
   cd backend
   docker build -t reprint-api .
   ```

2. **Run Container**:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e SUPABASE_URL=your-url \
     -e SUPABASE_KEY=your-key \
     -e CORS_ORIGINS=https://your-frontend.vercel.app \
     --name reprint-api \
     reprint-api
   ```

3. **Push to Registry** (for cloud deployment):
   ```bash
   docker tag reprint-api your-registry/reprint-api
   docker push your-registry/reprint-api
   ```

## Step 2: Deploy Frontend (Vercel)

1. **Sign up/Login**: Go to [vercel.com](https://vercel.com) and sign in with GitHub

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import `pinpix-t/reprint` repository

3. **Configure Project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

4. **Set Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
   (Use the URL from your backend deployment)

5. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - You'll get a URL like `https://reprint-xyz.vercel.app`

## Step 3: Update CORS Configuration

After deploying frontend, update backend CORS:

1. Go to your backend hosting platform
2. Update `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app,https://your-custom-domain.com
   ```
3. Restart the backend service

## Step 4: Set Up Scheduled Jobs

### Option A: GitHub Actions (Recommended)

1. **Go to Repository Settings**:
   - Navigate to `Settings` → `Secrets and variables` → `Actions`

2. **Add Secrets**:
   ```
   SUPABASE_URL
   SUPABASE_KEY
   FRESHDESK_API_KEY (optional)
   FRESHDESK_DOMAIN (optional)
   ```

3. **Workflow Already Configured**:
   - The workflow at `.github/workflows/daily-refresh.yml` is ready
   - It runs daily at 2 AM UTC
   - No additional setup needed!

### Option B: Cron Job (If self-hosting)

Add to your server's crontab:
```bash
0 2 * * * cd /path/to/reprint/backend && python jobs/daily_refresh.py
```

### Option C: External Cron Service

Use services like:
- [cron-job.org](https://cron-job.org)
- [EasyCron](https://www.easycron.com)

Set up HTTP request to your backend's refresh endpoint (if you add one).

## Step 5: Verify Deployment

### Backend Health Check

```bash
curl https://your-backend-url.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

### Frontend Check

1. Visit your Vercel URL
2. Check browser console for errors
3. Test API connectivity

### Test API Endpoints

```bash
# Overview endpoint
curl https://your-backend-url.railway.app/api/reprints/overview?days=7

# Health check
curl https://your-backend-url.railway.app/health
```

## Step 6: Custom Domain (Optional)

### Frontend (Vercel)

1. Go to your project in Vercel dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

### Backend

Depends on your hosting platform:
- **Railway**: Add custom domain in project settings
- **Render**: Add custom domain in service settings
- **Fly.io**: `fly domains add yourdomain.com`

## Troubleshooting

### Backend Issues

**Problem**: Environment variables not loading
- **Solution**: Ensure all required vars are set in hosting platform
- Check logs for "CRITICAL: Required environment variables are missing"

**Problem**: CORS errors
- **Solution**: Verify `CORS_ORIGINS` includes your frontend URL
- Check for trailing slashes

**Problem**: Health check failing
- **Solution**: Ensure port is correctly set (usually `$PORT` or `8000`)
- Check if health endpoint is accessible

### Frontend Issues

**Problem**: API calls failing
- **Solution**: Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check browser console for CORS errors
- Ensure backend is running

**Problem**: Build errors
- **Solution**: Check Node.js version (should be 18+)
- Verify all dependencies are in `package.json`

## Environment Variables Summary

### Backend (Required)
```
SUPABASE_URL=https://jqzpyztivqshzzsfdecp.supabase.co
SUPABASE_KEY=your-key
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Backend (Optional)
```
FRESHDESK_API_KEY=your-key
FRESHDESK_DOMAIN=your-domain.freshdesk.com
API_TIMEOUT_SECONDS=30
MAX_PAGE_SIZE=1000
```

### Frontend (Required)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

## Quick Start Commands

### Local Development

**Backend**:
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

### Production Deployment

**Backend** (Railway/Render):
- Connect GitHub repo
- Set environment variables
- Deploy automatically

**Frontend** (Vercel):
- Connect GitHub repo
- Set `NEXT_PUBLIC_API_URL`
- Deploy automatically

## Cost Estimates

- **Vercel**: Free tier (100GB bandwidth/month)
- **Railway**: $5/month (500 hours free, then $0.000463/hour)
- **Render**: Free tier available (spins down after inactivity)
- **Fly.io**: Free tier (3 shared VMs)

## Next Steps

1. ✅ Deploy backend to Railway/Render/Fly.io
2. ✅ Deploy frontend to Vercel
3. ✅ Update CORS_ORIGINS with frontend URL
4. ✅ Set up GitHub Actions for scheduled jobs
5. ✅ Test all endpoints
6. ✅ Monitor logs for errors
7. ✅ Set up custom domains (optional)

## Support

If you encounter issues:
1. Check application logs in your hosting platform
2. Verify all environment variables are set
3. Test endpoints with `curl` or Postman
4. Check browser console for frontend errors

