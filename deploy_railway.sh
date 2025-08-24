#!/bin/bash

# Railway Deployment Script for ResuMatch
# This script automates the deployment process to Railway

set -e  # Exit on any error

echo "🚂 Railway Deployment Script for ResuMatch"
echo "=========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    
    # Try different installation methods
    if command -v npm &> /dev/null; then
        echo "📦 Installing via npm..."
        npm install -g @railway/cli
    elif command -v yarn &> /dev/null; then
        echo "🧶 Installing via yarn..."
        yarn global add @railway/cli
    elif command -v brew &> /dev/null; then
        echo "🍺 Installing via Homebrew..."
        brew install railway
    else
        echo "❌ No package manager found. Please install Railway CLI manually:"
        echo "   npm install -g @railway/cli"
        echo "   or visit: https://railway.app/docs/develop/cli"
        exit 1
    fi
fi

echo "✅ Railway CLI found"

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway..."
    railway login
fi

echo "✅ Logged in to Railway"

# Check if project is initialized
if [ ! -d ".railway" ]; then
    echo "🚀 Initializing Railway project..."
    railway init
fi

echo "✅ Railway project initialized"

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set FLASK_ENV=production
railway variables set FLASK_DEBUG=false

# Check if SECRET_KEY is set
if ! railway variables | grep -q "SECRET_KEY"; then
    echo "🔑 Setting SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    railway variables set SECRET_KEY="$SECRET_KEY"
    echo "✅ SECRET_KEY generated and set"
else
    echo "✅ SECRET_KEY already set"
fi

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment completed!"

# Show service status
echo "📊 Service status:"
railway status

# Show the deployed URL
echo "🌐 Your app is available at:"
railway open

echo ""
echo "🎉 Deployment successful! Your ResuMatch app is now running on Railway."
echo ""
echo "Useful commands:"
echo "  railway logs          - View logs"
echo "  railway status        - Check status"
echo "  railway variables     - View environment variables"
echo "  railway open          - Open in browser"
echo ""
echo "For more information, see: RAILWAY_DEPLOYMENT.md"
