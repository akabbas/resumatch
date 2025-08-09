#!/usr/bin/env python3
"""
Test script to verify production environment setup
"""

import os
import sys
import json
from pathlib import Path

def test_production_setup():
    """Test production environment setup"""
    print("🧪 Testing ResuMatch Production Environment...")
    
    # Test 1: Check if production files exist
    print("\n📁 Checking production files...")
    required_files = [
        'app_production.py',
        'env.production',
        'environments/production/requirements.txt',
        'Dockerfile.production',
        'docker-compose.production.yml',
        'scripts/setup_production.sh',
        'scripts/run_production.sh',
        'templates/404.html',
        'templates/500.html',
        'PRODUCTION_SETUP.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        return False
    
    # Test 2: Check environment configuration
    print("\n⚙️  Checking environment configuration...")
    try:
        # Try to import dotenv, but don't fail if it's not available
        try:
            from dotenv import load_dotenv
            load_dotenv('env.production')
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping environment variable check")
            # Read env file manually
            if os.path.exists('env.production'):
                with open('env.production', 'r') as f:
                    env_content = f.read()
                print("✅ env.production file exists and is readable")
            else:
                print("❌ env.production file not found")
                return False
        
        # Check if we can read environment variables
        required_env_vars = [
            'FLASK_ENV',
            'FLASK_DEBUG',
            'FLASK_PORT',
            'LOG_LEVEL',
            'SECRET_KEY',
            'ENABLE_ANALYTICS',
            'ENABLE_MONITORING',
            'ENABLE_INTELLIGENT_SKILL_MATCHING',
            'ENABLE_JOB_TITLE_OPTIMIZATION',
            'ENABLE_SUMMARY_OPTIMIZATION',
            'ENABLE_BULLET_OPTIMIZATION',
            'ENABLE_PAGE_OPTIMIZATION'
        ]
        
        missing_env_vars = []
        for var in required_env_vars:
            if os.getenv(var) is not None:
                print(f"✅ {var}")
            else:
                print(f"⚠️  {var} (will use default)")
                missing_env_vars.append(var)
        
        if len(missing_env_vars) == len(required_env_vars):
            print("⚠️  No environment variables found, will use defaults")
            
    except Exception as e:
        print(f"❌ Environment configuration error: {e}")
        return False
    
    # Test 3: Check if core modules can be imported
    print("\n📦 Checking core modules...")
    try:
        import resume_generator
        print("✅ resume_generator imported successfully")
    except ImportError as e:
        print(f"❌ resume_generator import error: {e}")
        return False
    
    try:
        import intelligent_skill_matcher
        print("✅ intelligent_skill_matcher imported successfully")
    except ImportError as e:
        print(f"❌ intelligent_skill_matcher import error: {e}")
        return False
    
    try:
        import job_matcher
        print("✅ job_matcher imported successfully")
    except ImportError as e:
        print(f"❌ job_matcher import error: {e}")
        return False
    
    # Test 4: Check if production app can be imported
    print("\n🚀 Checking production app...")
    try:
        import app_production
        print("✅ Production app imported successfully")
    except ImportError as e:
        print(f"❌ Production app import error: {e}")
        return False
    
    # Test 5: Check feature flags (if environment is loaded)
    print("\n🎛️  Checking feature flags...")
    feature_flags = {
        'ENABLE_INTELLIGENT_SKILL_MATCHING': os.getenv('ENABLE_INTELLIGENT_SKILL_MATCHING', 'True'),
        'ENABLE_JOB_TITLE_OPTIMIZATION': os.getenv('ENABLE_JOB_TITLE_OPTIMIZATION', 'True'),
        'ENABLE_SUMMARY_OPTIMIZATION': os.getenv('ENABLE_SUMMARY_OPTIMIZATION', 'True'),
        'ENABLE_BULLET_OPTIMIZATION': os.getenv('ENABLE_BULLET_OPTIMIZATION', 'True'),
        'ENABLE_PAGE_OPTIMIZATION': os.getenv('ENABLE_PAGE_OPTIMIZATION', 'True')
    }
    
    for flag, value in feature_flags.items():
        status = "✅" if value == 'True' else "❌"
        print(f"{status} {flag}: {value}")
    
    # Test 6: Check directories
    print("\n📂 Checking directories...")
    required_dirs = ['uploads', 'logs', 'environments/production']
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️  {dir_path} (will be created during setup)")
    
    # Test 7: Check if scripts are executable
    print("\n🔧 Checking scripts...")
    script_files = ['scripts/setup_production.sh', 'scripts/run_production.sh']
    for script in script_files:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✅ {script} (executable)")
            else:
                print(f"⚠️  {script} (not executable)")
        else:
            print(f"❌ {script} (not found)")
    
    print("\n🎉 Production environment setup test completed!")
    print("\n📋 Next steps:")
    print("1. Run: ./scripts/setup_production.sh")
    print("2. Update env.production with your API keys")
    print("3. Run: ./scripts/run_production.sh")
    print("4. Or use Docker: docker-compose -f docker-compose.production.yml up --build")
    
    return True

if __name__ == "__main__":
    success = test_production_setup()
    sys.exit(0 if success else 1)
