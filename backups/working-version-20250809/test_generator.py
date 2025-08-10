#!/usr/bin/env python3
"""
Test script for ATS Resume Generator
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_generator import ResumeGenerator

def test_basic_generation():
    """Test basic resume generation with sample data"""
    print("🧪 Testing basic resume generation...")
    
    # Sample job description
    job_desc = """
    Senior Python Developer
    
    We are looking for a Senior Python Developer to join our team. 
    The ideal candidate should have:
    - 5+ years of experience with Python
    - Experience with Django, Flask, or FastAPI
    - Knowledge of PostgreSQL, MySQL, or MongoDB
    - Experience with AWS, Docker, and Kubernetes
    - Familiarity with React, JavaScript, and HTML/CSS
    - Experience with Git and CI/CD pipelines
    - Knowledge of REST APIs and microservices architecture
    """
    
    # Sample experience data
    experience_data = {
        "summary": "Experienced software developer with 5+ years in Python development, specializing in web applications and API development.",
        "experience": [
            {
                "title": "Senior Python Developer",
                "company": "Tech Solutions Inc.",
                "duration": "2020-2023",
                "description": "Led development of REST APIs using Django and FastAPI. Implemented microservices architecture with Docker and Kubernetes. Managed PostgreSQL databases and integrated with React frontend."
            },
            {
                "title": "Python Developer",
                "company": "StartupXYZ",
                "duration": "2018-2020",
                "description": "Developed web applications using Flask and SQLAlchemy. Deployed applications on AWS using Docker containers. Worked with MongoDB and Redis for data storage."
            }
        ],
        "skills": ["Python", "Django", "Flask", "FastAPI", "PostgreSQL", "MongoDB", "AWS", "Docker", "Kubernetes", "React", "JavaScript", "Git", "REST APIs"],
        "certifications": ["AWS Certified Developer", "Docker Certified Associate"],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built a full-stack e-commerce platform using Django, React, and PostgreSQL. Implemented payment processing with Stripe API.",
                "technologies": ["Django", "React", "PostgreSQL", "Stripe", "Docker"]
            }
        ]
    }
    
    # Initialize generator
    generator = ResumeGenerator(use_openai=False, max_pages=2, include_projects=True)
    
    # Generate resume
    output_path = "test_resume.pdf"
    result = generator.generate_resume(
        job_description=job_desc,
        experience_data=experience_data,
        output_path=output_path,
        name="John Doe",
        contact_info="john.doe@email.com | (555) 123-4567 | San Francisco, CA"
    )
    
    if os.path.exists(output_path):
        print(f"✅ Test passed! Resume generated: {output_path}")
        print(f"📄 File size: {os.path.getsize(output_path)} bytes")
        return True
    else:
        print("❌ Test failed! Resume file not created.")
        return False

def test_file_input():
    """Test resume generation using file inputs"""
    print("\n🧪 Testing file input generation...")
    
    # Check if example files exist
    job_file = "examples/sample_job_description.txt"
    exp_file = "examples/sample_experience.json"
    
    if not os.path.exists(job_file):
        print(f"❌ Job description file not found: {job_file}")
        return False
    
    if not os.path.exists(exp_file):
        print(f"❌ Experience file not found: {exp_file}")
        return False
    
    # Initialize generator
    generator = ResumeGenerator(use_openai=False, max_pages=2, include_projects=True)
    
    # Read files
    with open(job_file, 'r', encoding='utf-8') as f:
        job_desc = f.read()
    
    with open(exp_file, 'r', encoding='utf-8') as f:
        import json
        experience_data = json.load(f)
    
    # Generate resume
    output_path = "test_file_resume.pdf"
    result = generator.generate_resume(
        job_description=job_desc,
        experience_data=experience_data,
        output_path=output_path,
        name="Jane Smith",
        contact_info="jane.smith@email.com | (555) 987-6543 | New York, NY"
    )
    
    if os.path.exists(output_path):
        print(f"✅ File input test passed! Resume generated: {output_path}")
        print(f"📄 File size: {os.path.getsize(output_path)} bytes")
        return True
    else:
        print("❌ File input test failed! Resume file not created.")
        return False

def test_keyword_extraction():
    """Test keyword extraction functionality"""
    print("\n🧪 Testing keyword extraction...")
    
    from resume_generator import KeywordExtractor
    
    extractor = KeywordExtractor(use_openai=False)
    
    # Test text
    test_text = """
    Senior Python Developer needed with experience in:
    - Django, Flask, FastAPI
    - PostgreSQL, MongoDB, Redis
    - AWS, Docker, Kubernetes
    - React, JavaScript, HTML/CSS
    - Git, CI/CD, REST APIs
    """
    
    keywords = extractor.extract_keywords(test_text)
    print(f"✅ Extracted keywords: {keywords[:10]}...")
    
    if len(keywords) > 0:
        print("✅ Keyword extraction test passed!")
        return True
    else:
        print("❌ Keyword extraction test failed!")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting ATS Resume Generator Tests\n")
    
    tests = [
        test_keyword_extraction,
        test_basic_generation,
        test_file_input
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The resume generator is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    # Clean up test files
    test_files = ["test_resume.pdf", "test_file_resume.pdf"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleaned up: {file}")

if __name__ == "__main__":
    main() 