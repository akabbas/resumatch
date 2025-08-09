#!/bin/bash

# Development Environment Setup Script with GPT-5 Features
set -e

echo "🚀 Setting up ResuMatch Development Environment with GPT-5 Features..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads_dev
mkdir -p logs_dev
mkdir -p environments/development

# Create development virtual environment
echo "🐍 Creating development virtual environment..."
python3 -m venv resumatch_dev

# Activate and install dependencies
echo "📦 Installing development dependencies with GPT-5 features..."
source resumatch_dev/bin/activate
pip install --upgrade pip
pip install -r environments/development/requirements.txt

# Download required NLP models
echo "🤖 Downloading NLP models..."
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"

# Install development tools
echo "🔧 Installing development tools..."
pip install pre-commit
pre-commit install

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 uploads_dev
chmod 755 logs_dev

# Create development configuration
echo "⚙️  Setting up development configuration..."
if [ ! -f "env.development" ]; then
    echo "⚠️  env.development not found. Please create it with your API keys."
fi

echo "✅ Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update env.development with your GPT-5 API keys:"
echo "   - OPENAI_API_KEY=your_gpt5_key_here"
echo "   - ANTHROPIC_API_KEY=your_anthropic_key_here (optional)"
echo "   - COHERE_API_KEY=your_cohere_key_here (optional)"
echo ""
echo "2. Run development server:"
echo "   ./scripts/run_development.sh"
echo ""
echo "3. Or use Docker:"
echo "   docker-compose -f docker-compose.development.yml up --build"
echo ""
echo "4. Access development tools:"
echo "   - Web Interface: http://localhost:8001"
echo "   - Jupyter Lab: http://localhost:8888"
echo "   - Health Check: http://localhost:8001/health"
echo ""
echo "🎯 GPT-5 Features Available:"
echo "   - Advanced Content Generation"
echo "   - Intelligent Career Advice"
echo "   - Advanced Job Analysis"
echo "   - Real-time Optimization"
echo "   - Multi-model AI Integration"
echo "   - LangChain Integration"
