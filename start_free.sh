#!/bin/bash

echo "🎉 Starting ResuMatch FREE Version"
echo "=================================="
echo "✅ No API costs - 100% FREE!"
echo "✅ Local AI processing"
echo "✅ Privacy focused"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "resumatch_env" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv resumatch_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source resumatch_env/bin/activate

# Install free dependencies
echo "📦 Installing FREE dependencies..."
pip install -r requirements.free.txt

# Test the free version
echo "🧪 Testing FREE AI generator..."
python free_ai_generator.py

echo ""
echo "🎯 Your FREE ResuMatch is ready!"
echo "💡 Features available:"
echo "   - Local AI resume generation"
echo "   - Skill extraction and optimization"
echo "   - ATS optimization"
echo "   - Professional formatting"
echo ""
echo "🚀 To generate a resume:"
echo "   python free_ai_generator.py"
echo ""
echo "🌐 To start web interface (if available):"
echo "   python app.py"
