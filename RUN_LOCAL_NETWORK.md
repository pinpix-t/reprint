# Running on Local Network (Share with Others)

## Quick Start

### Step 1: Find Your Local IP Address
```bash
# On Mac/Linux:
ifconfig | grep "inet " | grep -v 127.0.0.1

# On Windows:
ipconfig
```

Your IP is: **192.168.70.253** (update if different)

### Step 2: Start Backend (Terminal 1)
```bash
cd backend

# Make sure .env has your Supabase credentials
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be at: `http://192.168.70.253:8000`

### Step 3: Start Frontend (Terminal 2)
```bash
cd frontend

# Create .env.local with your local IP
echo "NEXT_PUBLIC_API_URL=http://192.168.70.253:8000" > .env.local

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

Frontend will be at: `http://192.168.70.253:3000`

### Step 4: Update Backend CORS
In `backend/.env`, add:
```
CORS_ORIGINS=http://192.168.70.253:3000,http://localhost:3000
```

Then restart the backend.

### Step 5: Share the URL
Give your friend this URL: **http://192.168.70.253:3000**

## Requirements
- Both laptops must be on the **same WiFi network**
- Firewall may need to allow ports 3000 and 8000
- Backend must be running before frontend

## Troubleshooting

**Can't connect?**
- Check both devices are on same WiFi
- Try disabling firewall temporarily
- Verify backend is running: `curl http://192.168.70.253:8000/health`

**CORS errors?**
- Make sure `CORS_ORIGINS` in backend includes your IP
- Restart backend after changing .env

