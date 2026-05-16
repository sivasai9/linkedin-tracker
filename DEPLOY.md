# LinkedIn Job Tracker - Deployment Guide

## Deploy to Render (Free Tier)

### Step 1: Setup MongoDB Atlas (Free Cloud DB)
1. Go to https://www.mongodb.com/atlas and create a free account
2. Create a free cluster (M0 tier)
3. Under "Database Access", create a user with password
4. Under "Network Access", add `0.0.0.0/0` to allow access from Render
5. Click "Connect" → "Drivers" → Copy the connection string
   - It looks like: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/`

### Step 2: Push to GitHub
```bash
cd linkedin-tracker
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/linkedin-tracker.git
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to https://render.com and sign up (free with GitHub)
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: linkedin-job-tracker
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variable:
   - `MONGODB_URL` = your MongoDB Atlas connection string from Step 1
6. Click "Create Web Service"

### Done!
Your app will be live at `https://linkedin-job-tracker.onrender.com` (or similar URL).

> **Note**: Render free tier spins down after 15 min of inactivity. First request after sleep takes ~30s to wake up.
