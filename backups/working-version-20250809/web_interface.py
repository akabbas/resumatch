#!/usr/bin/env python3
"""
ResuMatch Web Interface Startup Script
Run this to start the web interface
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import werkzeug
        print("✅ Flask dependencies found")
        return True
    except ImportError:
        print("❌ Flask not found. Installing dependencies...")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==2.3.3", "werkzeug==2.3.7"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_web_interface():
    """Start the Flask web interface"""
    print("🚀 Starting ResuMatch Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import and run the Flask app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

def main():
    """Main function"""
    print("🎯 ResuMatch Web Interface")
    print("=" * 50)
    
    # Check if dependencies are installed
    if not check_dependencies():
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually:")
            print("pip install flask==2.3.3 werkzeug==2.3.7")
            return
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found. Please ensure you're in the correct directory.")
        return
    
    # Start the web interface
    start_web_interface()

if __name__ == "__main__":
    main() 