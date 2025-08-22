#!/usr/bin/env python3
"""
Test script for ResuMatch with fallback model support
"""

import os
import sys
from dotenv import load_dotenv

def test_openai_models():
    """Test OpenAI models with fallback support"""
    print("🔗 Testing OpenAI Models with Fallback...")
    
    # Load environment variables
    load_dotenv('env.gpt4o')
    
    try:
        import openai
        
        # Get configuration
        api_key = os.getenv('OPENAI_API_KEY')
        primary_model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        fallback_model = os.getenv('OPENAI_FALLBACK_MODEL', 'gpt-3.5-turbo')
        
        if not api_key:
            print("   ❌ OpenAI API key not configured")
            return False
        
        print(f"   🔑 API Key: {api_key[:20]}...")
        print(f"   🎯 Primary Model: {primary_model}")
        print(f"   🆘 Fallback Model: {fallback_model}")
        
        # Test primary model
        print(f"\n   🧪 Testing {primary_model}...")
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=primary_model,
                messages=[{"role": "user", "content": "Say 'Hello World' in 3 words"}],
                max_tokens=10
            )
            print(f"   ✅ {primary_model} working: {response.choices[0].message.content}")
            return True
            
        except Exception as e:
            print(f"   ❌ {primary_model} failed: {str(e)[:100]}...")
            
            # Try fallback model
            if fallback_model and fallback_model != primary_model:
                print(f"\n   🆘 Trying fallback model {fallback_model}...")
                try:
                    response = client.chat.completions.create(
                        model=fallback_model,
                        messages=[{"role": "user", "content": "Say 'Hello World' in 3 words"}],
                        max_tokens=10
                    )
                    print(f"   ✅ {fallback_model} working: {response.choices[0].message.content}")
                    print(f"   💡 Using fallback model for now")
                    return True
                    
                except Exception as e2:
                    print(f"   ❌ {fallback_model} also failed: {str(e2)[:100]}...")
                    return False
            else:
                return False
                
    except ImportError:
        print("   ❌ OpenAI library not available")
        return False

def test_app_with_fallback():
    """Test if the app can import with fallback configuration"""
    print("\n🚀 Testing App Import with Fallback...")
    
    try:
        from app import app
        print("   ✅ Main app imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import main app: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ResuMatch Fallback Model Test")
    print("=" * 50)
    
    tests = [
        ("OpenAI Models", test_openai_models),
        ("App Import", test_app_with_fallback),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready!")
        print("\n💡 Next steps:")
        print("   1. Run: ./start_gpt4o.sh")
        print("   2. Access: http://localhost:8001")
        print("   3. Test resume generation")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n🔧 Common fixes:")
        print("   1. Check OpenAI account billing and credits")
        print("   2. Try using GPT-3.5-turbo as fallback")
        print("   3. Verify API key is valid and active")

if __name__ == "__main__":
    main()
