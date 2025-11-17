# Vercel Frontend Setup - Connect to Railway Backend

## ✅ Step 1: Get Your Vercel URL

1. Go to [vercel.com](https://vercel.com)
2. Click on your project
3. You'll see your deployment URL at the top, like:
   - `https://reprint-xyz.vercel.app`
   - Or `https://reprint-git-main-yourname.vercel.app`

**Copy this URL** - you'll need it for Step 3!

---

## ✅ Step 2: Get Your Railway Backend URL

1. Go to [railway.app](https://railway.app)
2. Click on your backend project
3. Go to **Settings** → **Networking**
4. Find your **Public Domain** URL, like:
   - `https://your-app.railway.app`
   - Or `https://your-app-production.up.railway.app`

**Copy this URL** - you'll need it now!

---

## ✅ Step 3: Set Vercel Environment Variable

1. In Vercel, go to your project
2. Click **Settings** → **Environment Variables**
3. Click **Add New**
4. Add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-railway-url.railway.app` (paste your Railway URL from Step 2)
   - **Environment**: Select all (Production, Preview, Development)
5. Click **Save**

**Important**: After adding the variable, you need to **redeploy**:
- Go to **Deployments** tab
- Click the **3 dots** (⋯) on the latest deployment
- Click **Redeploy**

---

## ✅ Step 4: Update Railway CORS

1. Go to Railway → Your backend project
2. Click **Variables** tab
3. Find or add `CORS_ORIGINS`
4. Set the value to:
   ```
   https://your-vercel-url.vercel.app
   ```
   (Use the Vercel URL from Step 1)

5. Railway will automatically restart the service

---

## ✅ Step 5: Test It!

1. Open your Vercel URL in a browser
2. Open browser **Developer Tools** (F12) → **Console** tab
3. Check for any errors
4. Try navigating the dashboard

**If you see CORS errors:**
- Make sure Railway CORS_ORIGINS includes your exact Vercel URL
- Make sure Railway service restarted after adding the variable

---

## Quick Checklist

- [ ] Got Vercel URL: `https://________.vercel.app`
- [ ] Got Railway URL: `https://________.railway.app`
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel = Railway URL
- [ ] Redeployed Vercel after adding environment variable
- [ ] Set `CORS_ORIGINS` in Railway = Vercel URL
- [ ] Tested the dashboard - it works! ✅

---

## Troubleshooting

**Frontend shows "Cannot connect to API"**
- Check Vercel environment variable is set correctly
- Make sure you redeployed after adding the variable
- Check Railway backend is running (visit Railway URL/health)

**CORS errors in browser console**
- Verify Railway `CORS_ORIGINS` includes your exact Vercel URL
- Make sure there are no trailing slashes
- Restart Railway service

**Build fails on Vercel**
- Check that Root Directory is set to `frontend`
- Check Node.js version (should be 18+)
- Check build logs in Vercel dashboard

