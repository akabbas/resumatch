# Railway Deployment Guide for ResuMatch

This guide covers migrating your Flask app from Heroku to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install the Railway CLI tool
3. **Git Repository**: Ensure your code is in a Git repository

## Installation

### Install Railway CLI

```bash
# Using npm (recommended)
npm install -g @railway/cli

# Using yarn
yarn global add @railway/cli

# Using Homebrew (macOS)
brew install railway
```

### Login to Railway

```bash
railway login
```

## Deployment Steps

### 1. Initialize Railway Project

```bash
# Navigate to your project directory
cd /path/to/resumatch

# Initialize Railway project
railway init

# This will create a .railway directory and link your project
```

### 2. Configure Environment Variables

```bash
# Set environment variables (replace with your actual values)
railway variables set FLASK_ENV=production
railway variables set FLASK_DEBUG=false
railway variables set SECRET_KEY=your-secret-key-here

# If you have OpenAI API keys
railway variables set OPENAI_API_KEY=your-openai-api-key

# View all variables
railway variables
```

### 3. Deploy to Railway

```bash
# Deploy your application
railway up

# Or deploy to a specific environment
railway up --environment production
```

### 4. Check Deployment Status

```bash
# View deployment logs
railway logs

# Check service status
railway status

# View service details
railway service
```

### 5. Open Your App

```bash
# Open the deployed application
railway open
```

## Configuration Files

### railway.json
- **Builder**: Uses NIXPACKS for automatic dependency detection
- **Start Command**: Gunicorn with optimized settings for Railway
- **Health Check**: Monitors the root path for application health
- **Restart Policy**: Automatically restarts on failures

### Procfile
- **Updated**: Now points to `app:app` instead of `app_heroku:app`
- **Port Binding**: Uses `$PORT` environment variable (Railway sets this automatically)
- **Workers**: 2 Gunicorn workers for better performance
- **Timeout**: 120 seconds for long-running resume generation tasks

### requirements.txt
- **Gunicorn**: Included for production WSGI server
- **ReportLab**: Included for PDF generation
- **Additional Dependencies**: Added `python-multipart` for form handling

## Environment Variables

### Required Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secret-key-here
```

### Optional Variables
```bash
OPENAI_API_KEY=your-openai-api-key
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

## Monitoring and Maintenance

### View Logs
```bash
# Real-time logs
railway logs --follow

# Logs for specific service
railway logs --service web
```

### Scale Your App
```bash
# Scale horizontally
railway scale web 2

# Check current scaling
railway scale
```

### Update Your App
```bash
# Deploy updates
git add .
git commit -m "Update app for Railway"
railway up
```

## Troubleshooting

### Common Issues

1. **Port Binding Error**
   - Ensure your app uses `$PORT` environment variable
   - Check that Gunicorn is binding to `0.0.0.0:$PORT`

2. **Build Failures**
   - Verify all dependencies in `requirements.txt`
   - Check Python version compatibility
   - Review build logs: `railway logs --build`

3. **Runtime Errors**
   - Check application logs: `railway logs`
   - Verify environment variables: `railway variables`
   - Test locally before deploying

4. **Memory Issues**
   - Monitor resource usage in Railway dashboard
   - Consider optimizing image processing for resume generation
   - Scale up if needed: `railway scale web 2`

### Debug Commands

```bash
# Check service status
railway status

# View service details
railway service

# Check environment variables
railway variables

# View recent deployments
railway deployments

# Rollback to previous deployment
railway rollback
```

## Performance Optimization

### Gunicorn Settings
- **Workers**: 2 workers for optimal performance
- **Timeout**: 120 seconds for resume generation
- **Bind**: `0.0.0.0:$PORT` for proper port binding

### Railway Features
- **Auto-scaling**: Railway can automatically scale based on traffic
- **Health Checks**: Monitors application health and restarts if needed
- **Rolling Deployments**: Zero-downtime deployments

## Cost Considerations

### Railway Pricing
- **Free Tier**: Limited usage per month
- **Pay-as-you-go**: Pay only for what you use
- **Predictable**: No hidden costs or overage charges

### Optimization Tips
- **Resource Monitoring**: Use Railway dashboard to monitor usage
- **Efficient Scaling**: Scale down during low-traffic periods
- **Image Optimization**: Compress images to reduce storage costs

## Migration Checklist

- [ ] Install Railway CLI
- [ ] Login to Railway account
- [ ] Initialize Railway project
- [ ] Update configuration files
- [ ] Set environment variables
- [ ] Test deployment locally
- [ ] Deploy to Railway
- [ ] Verify application functionality
- [ ] Update DNS/domain if needed
- [ ] Monitor performance and logs
- [ ] Set up monitoring alerts

## Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Community**: [Railway Discord](https://discord.gg/railway)
- **GitHub**: [Railway GitHub](https://github.com/railwayapp)

## Next Steps

After successful deployment:

1. **Domain Setup**: Configure custom domain if needed
2. **SSL Certificate**: Railway provides automatic SSL
3. **Monitoring**: Set up performance monitoring
4. **Backup Strategy**: Implement data backup procedures
5. **CI/CD**: Set up automated deployments from Git
