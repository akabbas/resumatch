#!/bin/bash

# Development Run Script with GPT-5 Features
set -e

echo "🚀 Starting ResuMatch Development Server with GPT-5 Features..."

# Check if virtual environment exists
if [ ! -d "resumatch_dev" ]; then
    echo "❌ Development environment not found. Run setup first:"
    echo "   ./scripts/setup_development.sh"
    exit 1
fi

# Activate virtual environment
source resumatch_dev/bin/activate

# Set development environment variables
export FLASK_ENV=development
export FLASK_DEBUG=True
export FLASK_PORT=8001

# Check if env.development exists
if [ ! -f "env.development" ]; then
    echo "⚠️  Warning: env.development not found. Using default settings."
    echo "   Please create env.development with your GPT-5 API keys."
fi

# Check GPT-5 API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set. GPT-5 features will be disabled."
    echo "   Set OPENAI_API_KEY in env.development to enable GPT-5 features."
fi

# Start development server with hot reload
echo "🔄 Starting Flask development server with hot reload..."
echo "📊 GPT-5 Features Status:"
echo "   - Advanced Content Generation: Enabled"
echo "   - Intelligent Career Advice: Enabled"
echo "   - Advanced Job Analysis: Enabled"
echo "   - Real-time Optimization: Enabled"
echo "   - Multi-model AI: Enabled"
echo "   - LangChain Integration: Enabled"
echo ""
echo "🌐 Access Points:"
echo "   - Web Interface: http://localhost:8001"
echo "   - Health Check: http://localhost:8001/health"
echo "   - Career Advice: POST http://localhost:8001/career-advice"
echo "   - Job Analysis: POST http://localhost:8001/job-analysis"
echo ""

python app_development.py
