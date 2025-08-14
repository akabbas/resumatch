# 🚀 ResuMatch Heroku Deployment Guide

This guide will walk you through deploying ResuMatch to Heroku, making it accessible worldwide with a simple web form interface.

## 📋 Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Ensure your project is in a Git repository

## 🔧 Setup Steps

### 1. Install Heroku CLI
```bash
# macOS (using Homebrew)
brew tap heroku/brew && brew install heroku

# Or download from Heroku website
```

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create Heroku App
```bash
# Navigate to your project directory
cd /path/to/resumatch

# Create a new Heroku app
heroku create your-resumatch-app-name

# Or let Heroku generate a name
heroku create
```

### 4. Set Environment Variables
```bash
# Set a secure secret key
heroku config:set SECRET_KEY="your-super-secret-key-here"

# Set Flask environment
heroku config:set FLASK_ENV=production
```

### 5. Add Buildpacks (Required for WeasyPrint)
```bash
# Add Python buildpack
heroku buildpacks:set heroku/python

# Add system dependencies for WeasyPrint
heroku buildpacks:add --index 1 heroku-community/apt
```

### 6. Create APT Dependencies File
Create `Aptfile` in your project root:
```
libcairo2-dev
libpango1.0-dev
libgdk-pixbuf2.0-dev
libffi-dev
shared-mime-info
```

### 7. Deploy to Heroku
```bash
# Add all files to git
git add .

# Commit changes
git commit -m "Prepare for Heroku deployment"

# Push to Heroku
git push heroku main

# Or if you're on master branch
git push heroku master
```

### 8. Open Your App
```bash
heroku open
```

## 🌐 Your App Will Be Available At

- **Main URL**: `https://your-app-name.herokuapp.com/`
- **Simple Form**: `https://your-app-name.herokuapp.com/form`

## 🔍 Troubleshooting

### Common Issues

1. **Buildpack Errors**
   ```bash
   # Check buildpacks
   heroku buildpacks
   
   # Clear and reset if needed
   heroku buildpacks:clear
   heroku buildpacks:set heroku/python
   heroku buildpacks:add --index 1 heroku-community/apt
   ```

2. **WeasyPrint Dependencies**
   - Ensure `Aptfile` is in your project root
   - The buildpack will install system dependencies automatically

3. **Memory Issues**
   ```bash
   # Check app logs
   heroku logs --tail
   
   # Scale up if needed
   heroku ps:scale web=1
   ```

4. **Port Issues**
   - Heroku automatically sets the `PORT` environment variable
   - Your app uses `os.environ.get('PORT', 8000)` to handle this

### View Logs
```bash
# Real-time logs
heroku logs --tail

# Recent logs
heroku logs --num 100
```

## 📁 File Structure for Heroku

```
resumatch/
├── app_heroku.py          # Main Heroku app file
├── Procfile               # Tells Heroku how to run the app
├── runtime.txt            # Python version specification
├── requirements.txt       # Python dependencies
├── Aptfile               # System dependencies for WeasyPrint
├── templates/             # HTML templates
├── resume_generator.py    # Core resume generation logic
├── job_matcher.py         # Job matching logic
└── ... (other files)
```

## 🚀 Post-Deployment

### 1. Test Your App
- Visit the main page
- Test the simple form
- Generate a sample resume
- Verify PDF download works

### 2. Custom Domain (Optional)
```bash
# Add custom domain
heroku domains:add www.yourdomain.com

# Configure DNS with your domain provider
```

### 3. Monitoring
```bash
# Check app status
heroku ps

# Monitor performance
heroku addons:open scout
```

## 💰 Cost Considerations

- **Free Tier**: No longer available on Heroku
- **Basic Dyno**: $7/month - suitable for personal use
- **Standard Dyno**: $25/month - better performance
- **Professional Dyno**: $250/month - production use

## 🔒 Security Notes

1. **Secret Key**: Always use a strong, unique secret key
2. **Environment Variables**: Never commit sensitive data to Git
3. **HTTPS**: Heroku provides SSL certificates automatically
4. **File Uploads**: Files are stored in `/tmp` and cleaned up automatically

## 📞 Support

If you encounter issues:

1. Check the logs: `heroku logs --tail`
2. Verify buildpacks: `heroku buildpacks`
3. Check environment variables: `heroku config`
4. Restart the app: `heroku restart`

## 🎉 Success!

Once deployed, your ResuMatch app will be:
- ✅ Accessible worldwide via web browser
- ✅ Handle multiple users simultaneously
- ✅ Generate ATS-optimized resumes
- ✅ Provide both simple form and advanced JSON options
- ✅ Automatically scale based on demand

Your users can now create perfect resumes without touching any JSON, all through a beautiful web interface!
