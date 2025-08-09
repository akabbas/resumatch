#!/bin/bash

# Production Run Script
set -e

echo "🚀 Starting ResuMatch Production Server..."

# Check if virtual environment exists
if [ ! -d "resumatch_prod" ]; then
    echo "❌ Production environment not found. Run setup first:"
    echo "   ./scripts/setup_production.sh"
    exit 1
fi

# Activate virtual environment
source resumatch_prod/bin/activate

# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False
export FLASK_PORT=8000

# Check if env.production exists
if [ ! -f "env.production" ]; then
    echo "⚠️  Warning: env.production not found. Using default settings."
fi

# Start production server with Gunicorn
echo "🔄 Starting Gunicorn production server..."
gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 8 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level warning \
    app_production:app
