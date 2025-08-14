#!/bin/bash

# 🚀 ResuMatch Heroku Deployment Script
# This script automates the deployment process

echo "🚀 Starting ResuMatch Heroku Deployment..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   brew tap heroku/brew && brew install heroku"
    exit 1
fi

# Check if user is logged in
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku first:"
    heroku login
fi

# Create Heroku app (if not exists)
echo "📱 Creating/checking Heroku app..."
if [ -z "$1" ]; then
    echo "   Creating new Heroku app..."
    heroku create
else
    echo "   Using existing app: $1"
    heroku git:remote -a "$1"
fi

# Get app name
APP_NAME=$(heroku info -s | grep "git_url" | sed 's/.*\///' | sed 's/\.git.*//')
echo "🏗️  Configuring app: $APP_NAME"

# Set environment variables
echo "🔧 Setting environment variables..."
heroku config:set SECRET_KEY="resumatch-$(openssl rand -hex 32)"
heroku config:set FLASK_ENV=production

# Add buildpacks
echo "📦 Adding buildpacks..."
heroku buildpacks:clear
heroku buildpacks:set heroku/python
heroku buildpacks:add --index 1 heroku-community/apt

# Verify buildpacks
echo "✅ Buildpacks configured:"
heroku buildpacks

# Deploy
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku - $(date)"
git push heroku main

# Open the app
echo "🌐 Opening your app..."
heroku open

echo ""
echo "🎉 Deployment complete!"
echo "📱 Your app is available at: https://$APP_NAME.herokuapp.com/"
echo "📝 Simple form: https://$APP_NAME.herokuapp.com/form"
echo ""
echo "📊 Check app status: heroku ps"
echo "📋 View logs: heroku logs --tail"
echo "🔧 Check config: heroku config"
