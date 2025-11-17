# Final Setup - Connect Vercel to Railway

## Your Railway URL
✅ `https://reprint-production.up.railway.app`
✅ Health check works!

---

## Step 1: Set Environment Variable in Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click on your **reprint** project
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://reprint-production.up.railway.app`
   - **Environment**: ✅ Production ✅ Preview ✅ Development (select all)
6. Click **Save**

---

## Step 2: Redeploy Vercel (CRITICAL!)

**You MUST redeploy after adding the environment variable!**

1. Go to **Deployments** tab
2. Find your latest deployment
3. Click the **3 dots** (⋯) on the right
4. Click **Redeploy**
5. Wait for deployment to finish (1-2 minutes)

---

## Step 3: Verify Railway CORS

Make sure Railway has your Vercel URL in CORS_ORIGINS:

1. Go to Railway → Your Service → **Variables**
2. Check `CORS_ORIGINS` is set to:
   ```
   https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
   ```

---

## Step 4: Test

1. **Test Railway directly:**
   - `https://reprint-production.up.railway.app/health` ✅ (you confirmed this works)
   - `https://reprint-production.up.railway.app/api/reprints/overview?days=7`
   - Should return JSON data (not 404 anymore, since we fixed the table name)

2. **Test Vercel site:**
   - Open: https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
   - Dashboard should now load data!

---

## Quick Checklist

- [x] Railway URL: `https://reprint-production.up.railway.app`
- [x] Railway health check works
- [x] Table name fixed: `BO_reprints`
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel = `https://reprint-production.up.railway.app`
- [ ] Vercel redeployed after setting variable
- [ ] Railway CORS_ORIGINS = Vercel URL
- [ ] Test Vercel site - it works!

---

## After Setting NEXT_PUBLIC_API_URL

Once you've set it and redeployed, the dashboard should work!

If you still see errors, check the browser console (F12) for the exact error message.

