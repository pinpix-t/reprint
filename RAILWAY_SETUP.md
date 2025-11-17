# Railway Deployment Setup Checklist

## ✅ Pre-Deployment Checklist

### 1. Code Status
- [x] All code pushed to GitHub
- [x] Dockerfile configured correctly
- [x] Railway configuration files in place

### 2. Railway Dashboard Setup

#### Step 1: Create/Configure Service
1. Go to [railway.app](https://railway.app)
2. Create new project or select existing
3. Add service → "Deploy from GitHub repo"
4. Select `pinpix-t/reprint` repository

#### Step 2: Configure Service Settings
- **Root Directory**: Leave empty (uses root `/`)
- **Builder**: Should auto-detect as "Dockerfile" (or set manually)
- **Start Command**: Leave empty (uses Dockerfile CMD)

#### Step 3: Set Environment Variables
Go to Service → Variables and add:

**Required:**
```
SUPABASE_URL=https://jqzpyztivqshzzsfdecp.supabase.co
SUPABASE_KEY=your-supabase-key-here
CORS_ORIGINS=https://your-frontend.vercel.app
```

**Optional:**
```
FRESHDESK_API_KEY=your-freshdesk-key
FRESHDESK_DOMAIN=your-domain.freshdesk.com
API_TIMEOUT_SECONDS=30
MAX_PAGE_SIZE=1000
```

#### Step 4: Deploy
- Railway will automatically detect the Dockerfile
- Build will start automatically
- Monitor build logs for progress

### 3. After Deployment

#### Get Your Backend URL
- Railway will provide a URL like: `https://your-app.railway.app`
- Test health endpoint: `https://your-app.railway.app/health`

#### Update Frontend
1. Go to Vercel dashboard
2. Add/Update environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```
3. Redeploy frontend

#### Update CORS
1. Go back to Railway
2. Update `CORS_ORIGINS` variable with your Vercel URL:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
3. Restart service

## 🔍 Troubleshooting

### Build Fails
- Check build logs in Railway dashboard
- Verify Dockerfile syntax
- Ensure all files are committed to GitHub

### App Won't Start
- Check service logs in Railway
- Verify environment variables are set
- Test health endpoint: `/health`

### CORS Errors
- Verify `CORS_ORIGINS` includes your frontend URL
- Check for trailing slashes
- Restart service after updating CORS

## 📝 Quick Commands

### Test Backend Locally (Optional)
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```

### Test Docker Build Locally (Optional)
```bash
docker build -t reprint-api .
docker run -p 8000:8000 \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_KEY=your-key \
  -e CORS_ORIGINS=http://localhost:3000 \
  reprint-api
```

## ✅ Deployment Complete When:
- [ ] Railway build succeeds
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Frontend can connect to backend
- [ ] No CORS errors in browser console
- [ ] Dashboard loads and displays data

