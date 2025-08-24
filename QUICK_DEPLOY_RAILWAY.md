# 🚂 Quick Deploy to Railway

## One-Command Deployment

```bash
# Make the script executable (if not already)
chmod +x deploy_railway.sh

# Run the deployment script
./deploy_railway.sh
```

## Manual Deployment (Step by Step)

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
# or
brew install railway
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Project
```bash
railway init
```

### 4. Set Environment Variables
```bash
railway variables set FLASK_ENV=production
railway variables set FLASK_DEBUG=false
```

### 5. Deploy
```bash
railway up
```

### 6. Open Your App
```bash
railway open
```

## What's Been Created

✅ **`railway.json`** - Railway configuration  
✅ **`Procfile`** - Updated for Railway  
✅ **`requirements.txt`** - Complete dependencies  
✅ **`runtime.txt`** - Python version specification  
✅ **`.railwayignore`** - Exclude unnecessary files  
✅ **`deploy_railway.sh`** - Automated deployment script  

## Key Changes Made

- **Entry Point**: Changed from `app_heroku:app` to `app:app`
- **Port Binding**: Uses `$PORT` environment variable
- **Gunicorn Settings**: Optimized for Railway (2 workers, 120s timeout)
- **Dependencies**: Added `python-multipart` for form handling

## Your App is Ready!

After deployment, your ResuMatch app will be available at a Railway URL like:
`https://your-app-name.railway.app`

## Need Help?

- **Full Guide**: See `RAILWAY_DEPLOYMENT.md`
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Community**: [Railway Discord](https://discord.gg/railway)
