# Fix 404 NOT_FOUND Error

## The Problem
You're getting a 404 error, which means:
- ✅ The request is reaching a server
- ❌ But the endpoint doesn't exist on that server

## Most Likely Causes

### 1. Wrong URL in NEXT_PUBLIC_API_URL (Most Common)

**Check this first:**
1. Go to Vercel → Settings → Environment Variables
2. What is the value of `NEXT_PUBLIC_API_URL`?
3. Is it pointing to your Railway backend?

**Common mistakes:**
- ❌ `NEXT_PUBLIC_API_URL = https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app` (pointing to Vercel itself!)
- ✅ `NEXT_PUBLIC_API_URL = https://your-railway-url.railway.app` (pointing to Railway)

**If it's pointing to Vercel, that's the problem!** The frontend is trying to call Vercel's API, but Vercel doesn't have your backend.

---

### 2. Railway Backend Not Running

1. Go to Railway → Your Service
2. Check if status is **"Running"** (green)
3. If not running, check **Logs** for errors
4. Make sure environment variables are set:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

---

### 3. Test Railway Endpoints Directly

Test these URLs in your browser (replace with your Railway URL):

**Health check:**
```
https://your-railway-url.railway.app/health
```
Should return: `{"status":"healthy"}`

**Root endpoint:**
```
https://your-railway-url.railway.app/
```
Should return: `{"message":"Quality/Damage Analysis API","version":"1.0.0"}`

**API endpoint:**
```
https://your-railway-url.railway.app/api/reprints/overview?days=7
```
Should return JSON data with reprint overview

**If these don't work:**
- Railway backend isn't running correctly
- Check Railway logs for errors

---

## Quick Fix Steps

### Step 1: Verify Railway URL
1. Get your Railway public URL (Settings → Networking)
2. Test it: `https://your-railway-url.railway.app/health`
3. Should work!

### Step 2: Set Vercel Environment Variable
1. Vercel → Settings → Environment Variables
2. Set `NEXT_PUBLIC_API_URL` = your Railway URL
3. **Redeploy** (Deployments → 3 dots → Redeploy)

### Step 3: Check Browser Console
1. Open Vercel site
2. F12 → Console
3. Look for the actual request URL
4. Should show: `https://your-railway-url.railway.app/api/reprints/overview?days=7`

---

## What to Check

**In Vercel:**
- [ ] `NEXT_PUBLIC_API_URL` is set
- [ ] Value is your **Railway URL** (not Vercel URL!)
- [ ] Redeployed after setting

**In Railway:**
- [ ] Service is "Running"
- [ ] `/health` endpoint works
- [ ] `/api/reprints/overview?days=7` works when tested directly

**In Browser:**
- [ ] Console shows the correct Railway URL in requests
- [ ] Not trying to connect to `localhost:8000` or Vercel URL

---

## Tell Me

1. What is the value of `NEXT_PUBLIC_API_URL` in Vercel?
2. Does `https://your-railway-url.railway.app/health` work?
3. What URL does the browser console show when making the request?

This will help me pinpoint the exact issue!

