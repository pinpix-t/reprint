# Quick Setup for Your Vercel Deployment

## Your Vercel URL
✅ **https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app**

---

## Step 1: Get Your Railway Backend URL

1. Go to [railway.app](https://railway.app)
2. Click on your backend project
3. Go to **Settings** → **Networking** (or **Variables** tab)
4. Find your **Public Domain** - it looks like:
   - `https://your-app.railway.app`
   - Or `https://your-app-production.up.railway.app`

**Copy that URL!**

---

## Step 2: Set Environment Variable in Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click on your **reprint** project
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-railway-url.railway.app` (paste your Railway URL)
   - **Environment**: ✅ Production ✅ Preview ✅ Development (select all)
6. Click **Save**

**IMPORTANT**: After saving, you MUST redeploy:
- Go to **Deployments** tab
- Click the **3 dots** (⋯) on the latest deployment
- Click **Redeploy**

---

## Step 3: Update Railway CORS

1. Go to Railway → Your backend project
2. Click **Variables** tab
3. Find or add `CORS_ORIGINS`
4. Set value to:
   ```
   https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
   ```
5. Railway will auto-restart

---

## Step 4: Test!

Open: **https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app**

If it works, you're done! 🎉

If you see errors, check the browser console (F12) for details.

