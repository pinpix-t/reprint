# Set NEXT_PUBLIC_API_URL in Vercel - Step by Step

## Step 1: Get Your Railway Public URL

1. Go to [railway.app](https://railway.app)
2. Click on your **reprint** project
3. Click on your **backend service** (the one running FastAPI)
4. Go to **Settings** tab
5. Click **Networking** (or look for "Public Domain" section)
6. You should see a **Public Domain** section
7. If you see a URL like:
   - `https://reprint-production-xxxx.up.railway.app`
   - Or `https://reprint.railway.app`
   - **Copy this URL!**

**If you don't see a public domain:**
- Click **Generate Domain** button
- Railway will create a public URL
- Copy that URL

---

## Step 2: Set Environment Variable in Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click on your **reprint** project
3. Click **Settings** (left sidebar)
4. Click **Environment Variables** (under Configuration)
5. Click **Add New** button
6. Fill in:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: Paste your Railway URL from Step 1 (e.g., `https://reprint-production-xxxx.up.railway.app`)
   - **Environment**: 
     - ✅ Check **Production**
     - ✅ Check **Preview** 
     - ✅ Check **Development**
7. Click **Save**

---

## Step 3: Redeploy Vercel (IMPORTANT!)

**You MUST redeploy after adding the environment variable!**

1. Still in Vercel, go to **Deployments** tab (left sidebar)
2. Find your latest deployment
3. Click the **3 dots** (⋯) on the right side of that deployment
4. Click **Redeploy**
5. Wait for the deployment to finish (usually 1-2 minutes)

---

## Step 4: Test

1. Open your Vercel site: https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
2. The dashboard should now load data!

---

## Troubleshooting

**Still not working?**
- Check Railway is running (green status)
- Test Railway URL directly: `https://your-railway-url.railway.app/health`
- Check browser console (F12) for errors
- Make sure Railway URL in Vercel matches exactly (no trailing slash)

