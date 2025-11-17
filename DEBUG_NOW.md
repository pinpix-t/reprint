# Debug "Failed to load overview data" - Do This Now

## Step 1: Check Browser Console (Most Important!)

1. Open your Vercel site: https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
2. Press **F12** (or right-click → Inspect)
3. Go to **Console** tab
4. Look for error messages

**What to look for:**

### If you see: `Trying to connect to: http://localhost:8000`
→ **Problem**: NEXT_PUBLIC_API_URL not set in Vercel
→ **Fix**: Set it and redeploy (see Step 2)

### If you see: `CORS policy` or `Access-Control-Allow-Origin`
→ **Problem**: CORS issue
→ **Fix**: Check Railway CORS_ORIGINS matches Vercel URL exactly

### If you see: `Network Error` or `ECONNREFUSED`
→ **Problem**: Railway backend not running or wrong URL
→ **Fix**: Check Railway is running and URL is correct

### If you see: `404` or `500` error
→ **Problem**: Backend running but endpoint not found
→ **Fix**: Test Railway URL directly

---

## Step 2: Verify Vercel Environment Variable

1. Go to Vercel → Your Project → **Settings** → **Environment Variables**
2. Check if `NEXT_PUBLIC_API_URL` exists
3. If it exists, what value does it show?
4. If it doesn't exist, you need to add it (see SET_VERCEL_ENV_VAR.md)

**After adding/changing, you MUST redeploy:**
- Go to **Deployments** tab
- Click **3 dots** (⋯) → **Redeploy**

---

## Step 3: Test Railway Backend Directly

1. Get your Railway public URL (Settings → Networking → Public Domain)
2. Test these URLs in your browser:

**Health check:**
```
https://your-railway-url.railway.app/health
```
Should return: `{"status":"healthy"}`

**API endpoint:**
```
https://your-railway-url.railway.app/api/reprints/overview?days=7
```
Should return JSON data

**If these don't work:**
- Railway backend might not be running
- Check Railway → Your Service → Status
- Check Railway → Logs for errors

---

## Step 4: Quick Checklist

- [ ] Browser console checked - what error did you see?
- [ ] NEXT_PUBLIC_API_URL set in Vercel?
- [ ] Vercel redeployed after setting variable?
- [ ] Railway backend is "Running" (green status)?
- [ ] Railway /health endpoint works?
- [ ] Railway CORS_ORIGINS = Vercel URL?

---

## Tell Me What You See

After checking the browser console, tell me:
1. What error message appears in the console?
2. What URL does it say it's trying to connect to?
3. Is Railway backend running?
4. Does Railway /health work when you visit it directly?

This will help me pinpoint the exact issue!

