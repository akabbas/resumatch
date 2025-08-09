#!/bin/bash

# Production Environment Setup Script
set -e

echo "🚀 Setting up ResuMatch Production Environment..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p environments/production

# Create production virtual environment
echo "🐍 Creating production virtual environment..."
python3 -m venv resumatch_prod

# Activate and install dependencies
echo "📦 Installing production dependencies..."
source resumatch_prod/bin/activate
pip install --upgrade pip
pip install -r environments/production/requirements.txt

# Download required NLP models
echo "🤖 Downloading NLP models..."
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 uploads
chmod 755 logs

echo "✅ Production environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update env.production with your actual API keys and settings"
echo "2. Run: source resumatch_prod/bin/activate"
echo "3. Run: python app_production.py"
echo ""
echo "🐳 Or use Docker:"
echo "docker-compose -f docker-compose.production.yml up --build"
