# Update Railway CORS for Netlify

## What You Need to Change

Since you're now using **Netlify** instead of Vercel, you need to update Railway's `CORS_ORIGINS` to include your Netlify URL.

---

## Step 1: Get Your Netlify URL

1. Go to [app.netlify.com](https://app.netlify.com)
2. Click on your site
3. Your site URL is at the top, like:
   - `https://reprint-xyz.netlify.app`
   - Or `https://reprint-xyz-12345.netlify.app`

**Copy this URL!**

---

## Step 2: Update Railway CORS

1. Go to [railway.app](https://railway.app)
2. Click on your **backend service** (the one running FastAPI)
3. Go to **Variables** tab
4. Find `CORS_ORIGINS` (or add it if it doesn't exist)
5. Update the value to include your Netlify URL:

### Option A: Only Netlify (Recommended)
```
https://your-netlify-url.netlify.app
```

### Option B: Both Netlify and Localhost (For Development)
```
https://your-netlify-url.netlify.app,http://localhost:3000
```

### Option C: Keep Vercel Too (If You Want Both)
```
https://your-netlify-url.netlify.app,https://reprint-p917cyfiu-tejas-projects-8bee9919.vercel.app
```

6. Railway will **automatically restart** the service after you save

---

## Step 3: Verify

1. Wait 30 seconds for Railway to restart
2. Test your Netlify site
3. Open browser console (F12) - should not see CORS errors
4. Dashboard should load data!

---

## Important Notes

- **No trailing slash**: Make sure URL doesn't end with `/`
- **Exact match**: CORS is strict - URL must match exactly
- **HTTPS required**: Use `https://` not `http://`
- **Auto-restart**: Railway restarts automatically, no manual restart needed

---

## Quick Checklist

- [ ] Got Netlify URL: `https://________.netlify.app`
- [ ] Updated Railway `CORS_ORIGINS` with Netlify URL
- [ ] Saved the variable (Railway auto-restarts)
- [ ] Waited 30 seconds
- [ ] Tested Netlify site - it works! ✅

---

## Troubleshooting

**Still getting CORS errors?**
- Check the exact URL in browser console
- Make sure `CORS_ORIGINS` matches exactly (no trailing slash)
- Verify Railway service restarted (check logs)

**Multiple URLs?**
- Separate with commas: `url1,url2,url3`
- No spaces around commas

