#!/usr/bin/env python3
"""
Test script for the resume parser functionality
"""

import os
import tempfile
from resume_parser import ResumeParser, parse_resume_file

def test_resume_parser():
    """Test the resume parser with sample text"""
    
    # Create a sample resume text
    sample_resume_text = """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | San Francisco, CA
    
    SUMMARY
    Experienced software engineer with 5+ years developing scalable web applications using Python, JavaScript, and cloud technologies. Passionate about clean code, system design, and delivering high-quality software solutions.
    
    EXPERIENCE
    Senior Software Engineer
    TechCorp Inc. | 2021 - Present
    • Led development of microservices architecture serving 1M+ users
    • Implemented CI/CD pipelines reducing deployment time by 60%
    • Mentored junior developers and conducted code reviews
    
    Software Developer
    StartupXYZ | 2019 - 2021
    • Built full-stack web applications using React and Node.js
    • Collaborated with product team to deliver features on time
    • Optimized database queries improving performance by 40%
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, SQL, Git, Agile
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2019
    GPA: 3.8/4.0
    
    CERTIFICATIONS
    AWS Certified Developer Associate
    Google Cloud Professional Developer
    """
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_resume_text)
        temp_file = f.name
    
    try:
        # Test the parser
        print("🧪 Testing Resume Parser")
        print("=" * 50)
        
        parser = ResumeParser()
        result = parser.parse_resume(temp_file)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print("✅ Resume parsed successfully!")
        print(f"📊 Extracted {len(result)} sections")
        print()
        
        # Display results
        for section, content in result.items():
            if content:
                print(f"📋 {section.upper()}:")
                print("-" * 30)
                if isinstance(content, str) and len(content) > 100:
                    print(content[:100] + "...")
                else:
                    print(content)
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_parse_resume_file_function():
    """Test the convenience function"""
    print("\n🧪 Testing parse_resume_file convenience function")
    print("=" * 50)
    
    # Create another temporary file
    sample_text = """
    JANE SMITH
    Data Analyst
    jane.smith@email.com
    
    SUMMARY
    Data-driven analyst with expertise in SQL, Python, and data visualization tools.
    
    SKILLS
    SQL, Python, Tableau, Power BI, Excel, Statistical Analysis
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        temp_file = f.name
    
    try:
        result = parse_resume_file(temp_file)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print("✅ Convenience function works!")
        print(f"📊 Extracted sections: {list(result.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    print("🚀 Starting Resume Parser Tests")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_resume_parser()
    test2_passed = test_parse_resume_file_function()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed! Resume parser is working correctly.")
        exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        exit(1)
