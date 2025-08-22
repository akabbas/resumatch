#!/usr/bin/env python3
"""
Test script for improved resume formatting
"""

import json
from resume_generator import ResumeGenerator

def test_improved_formatting():
    """Test the improved resume formatting"""
    print("🧪 Testing Improved Resume Formatting...")
    
    # Sample experience data
    experience_data = {
        "name": "John Doe",
        "contact": {
            "email": "john.doe@email.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA"
        },
        "summary": "Experienced software engineer with 5+ years in full-stack development, specializing in Python, JavaScript, and cloud technologies. Proven track record of delivering scalable solutions and leading development teams.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "duration": "2022 - Present",
                "description": [
                    "Led development of microservices architecture serving 1M+ users",
                    "Implemented CI/CD pipelines reducing deployment time by 60%",
                    "Mentored junior developers and conducted code reviews"
                ]
            },
            {
                "title": "Software Engineer",
                "company": "Startup Inc",
                "duration": "2020 - 2022",
                "description": [
                    "Developed RESTful APIs using Python Flask and Django",
                    "Built responsive web applications with React and Node.js",
                    "Collaborated with cross-functional teams in Agile environment"
                ]
            }
        ],
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "Django", "Flask",
            "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Git",
            "CI/CD", "Agile", "Microservices", "REST APIs", "GraphQL"
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": [
                    "Built full-stack e-commerce solution with 10K+ users",
                    "Implemented payment processing and inventory management",
                    "Deployed on AWS with auto-scaling capabilities"
                ]
            }
        ],
        "certifications": [
            "AWS Certified Developer Associate",
            "Certified Scrum Master (CSM)",
            "Python Professional Certification"
        ]
    }
    
    # Job description
    job_description = """
    Senior Software Engineer - Full Stack Development
    
    We are seeking a talented Senior Software Engineer to join our growing team. 
    You will be responsible for designing, developing, and maintaining scalable 
    web applications and microservices.
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python and JavaScript
    - Experience with React, Node.js, and cloud platforms
    - Knowledge of microservices architecture
    - Experience with CI/CD and DevOps practices
    """
    
    # Initialize resume generator
    generator = ResumeGenerator(
        use_openai=False,
        max_pages=2,
        include_projects=True
    )
    
    # Generate resume
    output_path = "test_improved_formatting.pdf"
    result = generator.generate_resume(
        job_description=job_description,
        experience_data=experience_data,
        output_path=output_path,
        name="John Doe",
        contact_info="john.doe@email.com | (555) 123-4567 | San Francisco, CA"
    )
    
    if result:
        print(f"✅ Resume generated successfully: {result}")
        print("📋 Check the formatting improvements:")
        print("   - Reduced left indentation (0.05in instead of 0.1in)")
        print("   - Optimized margins (0.4in instead of 0.75in)")
        print("   - Better page utilization")
        print("   - Controlled page breaks")
        print("   - Professional spacing")
    else:
        print("❌ Resume generation failed")

if __name__ == "__main__":
    test_improved_formatting()
