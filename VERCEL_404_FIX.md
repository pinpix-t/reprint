# Fix Vercel 404 Error - Frontend Calling Wrong Server

## The Problem

You're getting a **Vercel 404 error** (notice the error ID format: `dxb1::vvrnp-...`), which means:
- ❌ Frontend is trying to call **Vercel's API** (which doesn't exist)
- ✅ Railway backend **does work** (I tested it - returns data!)

**Root cause:** `NEXT_PUBLIC_API_URL` is either:
1. Not set in Vercel
2. Set incorrectly (maybe to Vercel URL instead of Railway)
3. Set but Vercel wasn't redeployed

---

## Solution: Set NEXT_PUBLIC_API_URL in Vercel

### Step 1: Check Current Value

1. Go to Vercel → Your Project → **Settings** → **Environment Variables**
2. Look for `NEXT_PUBLIC_API_URL`
3. What does it say?

**If it doesn't exist or is wrong:**
- Continue to Step 2

**If it exists and is correct:**
- You need to **redeploy** (see Step 3)

---

### Step 2: Set the Environment Variable

1. In Vercel → **Settings** → **Environment Variables**
2. Click **Add New**
3. Enter:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://reprint-production.up.railway.app`
   - **Environment**: ✅ Production ✅ Preview ✅ Development
4. Click **Save**

---

### Step 3: Redeploy (CRITICAL!)

**You MUST redeploy after setting/changing the variable!**

1. Go to **Deployments** tab
2. Click the **3 dots** (⋯) on the latest deployment
3. Click **Redeploy**
4. Wait for it to finish (1-2 minutes)

**Why?** Environment variables are only available at build time. Changing them requires a new build.

---

### Step 4: Verify It's Set

After redeploying, check the build logs:

1. Go to **Deployments** → Click on the new deployment
2. Check **Build Logs**
3. Look for the API URL being used

Or test in browser console:
1. Open your Vercel site
2. F12 → Console
3. Type: `console.log(process.env.NEXT_PUBLIC_API_URL)`
4. Should show: `https://reprint-production.up.railway.app`

---

## Quick Test

**Before fix:**
- Frontend tries: `https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app/api/reprints/overview`
- Result: 404 (Vercel doesn't have this endpoint)

**After fix:**
- Frontend tries: `https://reprint-production.up.railway.app/api/reprints/overview`
- Result: ✅ Data loads!

---

## Verification Checklist

- [ ] `NEXT_PUBLIC_API_URL` exists in Vercel
- [ ] Value = `https://reprint-production.up.railway.app`
- [ ] Vercel redeployed after setting variable
- [ ] Browser console shows correct Railway URL
- [ ] Dashboard loads data ✅

---

## Still Getting 404?

1. **Check browser console (F12):**
   - What URL is it trying to connect to?
   - Should be: `https://reprint-production.up.railway.app/api/...`
   - If it shows Vercel URL, the variable isn't set correctly

2. **Check Vercel build logs:**
   - Did the build complete successfully?
   - Any errors about environment variables?

3. **Hard refresh:**
   - Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Clears browser cache

---

## Confirmed Working

I tested your Railway endpoint directly:
```
https://reprint-production.up.railway.app/api/reprints/overview?days=7
```
✅ **It works!** Returns data (currently empty, but endpoint exists).

The issue is 100% that Vercel frontend isn't pointing to Railway. Fix the environment variable and redeploy!

