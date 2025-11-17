# Troubleshooting "Failed to load overview data" on Vercel

## Quick Diagnosis

### Step 1: Check Browser Console
1. Open your Vercel site: https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
2. Press **F12** (or right-click → Inspect)
3. Go to **Console** tab
4. Look for error messages

**What to look for:**
- `Trying to connect to: http://localhost:8000` → API URL not set in Vercel
- `CORS error` → Railway CORS not configured
- `Network error` or `ECONNREFUSED` → Railway backend not running/accessible
- `404` or `500` → Backend running but endpoint not found

---

## Common Issues & Fixes

### Issue 1: API URL Not Set (Most Common)

**Symptom:** Console shows `Trying to connect to: http://localhost:8000`

**Fix:**
1. Go to Vercel → Your Project → **Settings** → **Environment Variables**
2. Check if `NEXT_PUBLIC_API_URL` exists
3. If missing or wrong:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-railway-url.railway.app` (your Railway public URL)
   - **Environment**: Select all (Production, Preview, Development)
   - Click **Save**
4. **IMPORTANT**: Go to **Deployments** → Click **3 dots** (⋯) → **Redeploy**

---

### Issue 2: CORS Error

**Symptom:** Console shows `CORS policy` or `Access-Control-Allow-Origin` error

**Fix:**
1. Go to Railway → Your Backend → **Variables**
2. Find or add `CORS_ORIGINS`
3. Set value to:
   ```
   https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
   ```
4. Railway will auto-restart
5. Wait 30 seconds, then refresh Vercel site

---

### Issue 3: Railway Backend Not Running

**Symptom:** `Network error`, `ECONNREFUSED`, or timeout

**Fix:**
1. Go to Railway → Your Backend
2. Check if service is **Running** (green status)
3. If not running, check **Logs** for errors
4. Verify environment variables are set:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
5. Try accessing Railway URL directly: `https://your-railway-url.railway.app/health`
   - Should return: `{"status":"healthy"}`

---

### Issue 4: Wrong Railway URL

**Symptom:** 404 errors or "Cannot GET /api/..."

**Fix:**
1. Make sure you're using the **public Railway URL** (ends in `.railway.app`)
2. NOT the internal URL (`*.railway.internal`)
3. Test the URL directly:
   ```
   https://your-railway-url.railway.app/health
   https://your-railway-url.railway.app/api/reprints/overview?days=7
   ```

---

## Step-by-Step Checklist

- [ ] **Vercel Environment Variable Set**
  - `NEXT_PUBLIC_API_URL` = your Railway public URL
  - Redeployed after setting variable

- [ ] **Railway CORS Configured**
  - `CORS_ORIGINS` = `https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app`
  - Service restarted

- [ ] **Railway Backend Running**
  - Service status is "Running"
  - `/health` endpoint works
  - Environment variables set (SUPABASE_URL, SUPABASE_KEY)

- [ ] **URLs Are Correct**
  - Railway URL is public (`.railway.app`)
  - Vercel URL matches CORS_ORIGINS exactly
  - No trailing slashes

---

## Test Commands

### Test Railway Backend Directly
```bash
# Replace with your Railway URL
curl https://your-railway-url.railway.app/health
curl https://your-railway-url.railway.app/api/reprints/overview?days=7
```

### Check Vercel Environment Variable
1. In Vercel, go to **Deployments**
2. Click on latest deployment
3. Check **Build Logs** - should show the API URL being used

---

## Still Not Working?

1. **Check Railway Logs:**
   - Railway → Your Service → **Logs** tab
   - Look for errors when Vercel tries to connect

2. **Check Vercel Logs:**
   - Vercel → Your Project → **Deployments** → Click deployment → **Logs**

3. **Verify URLs Match Exactly:**
   - Vercel URL in `CORS_ORIGINS` must match exactly (including `https://`)
   - No extra spaces or characters

4. **Try Hard Refresh:**
   - Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Clears browser cache

---

## Quick Fix Script

If you have both URLs ready:

**In Vercel:**
```
NEXT_PUBLIC_API_URL = https://your-railway-url.railway.app
```

**In Railway:**
```
CORS_ORIGINS = https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
```

Then redeploy Vercel and restart Railway.

