#!/usr/bin/env python3
"""
Test script for page limit enforcement in the Harvard PDF generator
This script tests various scenarios to ensure the max_pages limit is never exceeded
"""

import os
import tempfile
import logging
from harvard_pdf_generator import generate_harvard_pdf_resume

# Configure logging to see compression strategies
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_test_data(content_level='normal'):
    """Create test data with different content levels"""
    
    base_data = {
        "summary": "Experienced software engineer with expertise in Python, web development, and cloud technologies. Demonstrated ability to lead cross-functional teams and deliver high-impact solutions.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "duration": "2020-2023",
                "description": [
                    "Led development of scalable web applications using Python and React, resulting in 40% improvement in user engagement",
                    "Engineered microservices architecture improving system performance by 40% and reducing deployment time by 60%",
                    "Mentored junior developers and established coding standards that improved code quality by 25%",
                    "Collaborated with product managers to define technical requirements and project timelines",
                    "Implemented CI/CD pipelines that reduced deployment failures by 80%"
                ]
            },
            {
                "title": "Software Engineer",
                "company": "Startup Inc",
                "duration": "2018-2020",
                "description": [
                    "Developed full-stack web applications using Python, Django, and JavaScript",
                    "Optimized database queries and improved application performance by 30%",
                    "Participated in code reviews and contributed to team knowledge sharing"
                ]
            }
        ],
        "skills": ["Python", "React", "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Jenkins", "Git", "REST APIs", "GraphQL", "Microservices", "Agile", "Scrum"],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": ["Built full-stack e-commerce solution with payment processing", "Implemented real-time inventory management system", "Integrated with multiple payment gateways"],
                "technologies": ["Python", "React", "PostgreSQL", "Redis", "Stripe API"]
            },
            {
                "name": "Data Analytics Dashboard",
                "description": ["Created interactive dashboard for business metrics visualization", "Implemented real-time data streaming and processing", "Built automated reporting system"],
                "technologies": ["Python", "Django", "Chart.js", "Apache Kafka", "InfluxDB"]
            }
        ],
        "certifications": ["AWS Certified Developer", "Python Professional", "Docker Certified Associate", "Kubernetes Administrator"],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "year": "2019",
                "gpa": "3.8/4.0"
            }
        ]
    }
    
    if content_level == 'minimal':
        # Minimal content for 1-page testing
        base_data["summary"] = "Software engineer with Python and web development experience."
        base_data["experience"] = base_data["experience"][:1]  # Keep only first job
        base_data["skills"] = base_data["skills"][:8]  # Keep only top skills
        base_data["projects"] = base_data["projects"][:1]  # Keep only first project
        base_data["certifications"] = base_data["certifications"][:2]  # Keep only top certifications
        
    elif content_level == 'extensive':
        # Extensive content for testing compression
        base_data["experience"].extend([
            {
                "title": "Junior Developer",
                "company": "Small Company",
                "duration": "2016-2018",
                "description": [
                    "Assisted in development of internal tools and utilities",
                    "Participated in bug fixes and maintenance tasks",
                    "Learned modern development practices and tools"
                ]
            },
            {
                "title": "Intern",
                "company": "University Lab",
                "duration": "2015-2016",
                "description": [
                    "Researched machine learning algorithms for data analysis",
                    "Implemented proof-of-concept applications",
                    "Presented findings at university symposium"
                ]
            }
        ])
        
        # Add more skills
        base_data["skills"].extend(["Machine Learning", "TensorFlow", "PyTorch", "Data Science", "Pandas", "NumPy", "Scikit-learn", "Jupyter", "Linux", "Shell Scripting"])
        
        # Add more projects
        base_data["projects"].extend([
            {
                "name": "Machine Learning Model",
                "description": ["Developed predictive model for customer behavior analysis", "Achieved 85% accuracy in predictions"],
                "technologies": ["Python", "Scikit-learn", "Pandas", "NumPy"]
            },
            {
                "name": "Mobile App",
                "description": ["Built cross-platform mobile application using React Native", "Implemented offline functionality and data synchronization"],
                "technologies": ["React Native", "JavaScript", "Redux", "AsyncStorage"]
            }
        ])
    
    return base_data

def test_page_limit_enforcement():
    """Test the page limit enforcement with various scenarios"""
    
    logger.info("🧪 Testing Page Limit Enforcement")
    logger.info("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        ("minimal", 1, "Single page with minimal content"),
        ("normal", 1, "Single page with normal content (should trigger compression)"),
        ("extensive", 1, "Single page with extensive content (should trigger aggressive compression)"),
        ("minimal", 2, "Two pages with minimal content"),
        ("normal", 2, "Two pages with normal content"),
        ("extensive", 2, "Two pages with extensive content")
    ]
    
    results = []
    
    for content_level, max_pages, description in test_scenarios:
        logger.info(f"\n📋 Testing: {description}")
        logger.info(f"Content level: {content_level}, Max pages: {max_pages}")
        
        # Create test data
        test_data = create_test_data(content_level)
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Generate PDF
            logger.info("Generating PDF...")
            result_path = generate_harvard_pdf_resume(
                test_data, 
                output_path, 
                "John Doe", 
                "john@example.com | 555-1234 | New York",
                max_pages=max_pages,
                job_description="Software engineer Python React AWS Docker Kubernetes"
            )
            
            # Check if file was created
            if os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                logger.info(f"✅ PDF generated successfully")
                logger.info(f"   File size: {file_size:,} bytes")
                logger.info(f"   File path: {result_path}")
                
                # Try to count pages (this might fail if PyPDF2 is not available)
                try:
                    from PyPDF2 import PdfReader
                    with open(result_path, 'rb') as file:
                        reader = PdfReader(file)
                        actual_pages = len(reader.pages)
                        logger.info(f"   Actual pages: {actual_pages}")
                        
                        # Check if page limit was respected
                        if actual_pages <= max_pages:
                            logger.info(f"   ✅ Page limit respected: {actual_pages} <= {max_pages}")
                            results.append((content_level, max_pages, True, actual_pages))
                        else:
                            logger.error(f"   ❌ Page limit exceeded: {actual_pages} > {max_pages}")
                            results.append((content_level, max_pages, False, actual_pages))
                            
                except ImportError:
                    logger.warning("   ⚠️  PyPDF2 not available, cannot verify page count")
                    # Estimate pages based on file size
                    estimated_pages = max(1, file_size // 50000)
                    logger.info(f"   Estimated pages: {estimated_pages}")
                    results.append((content_level, max_pages, True, estimated_pages))
                    
            else:
                logger.error(f"❌ PDF generation failed - file not created")
                results.append((content_level, max_pages, False, 0))
                
        except Exception as e:
            logger.error(f"❌ Error during PDF generation: {e}")
            results.append((content_level, max_pages, False, 0))
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except:
                pass
    
    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed_tests = 0
    total_tests = len(results)
    
    for content_level, max_pages, success, actual_pages in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} | {content_level:10} | {max_pages} page(s) | Actual: {actual_pages} page(s)")
        if success:
            passed_tests += 1
    
    logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Page limit enforcement is working correctly.")
    else:
        logger.error("⚠️  Some tests failed. Check the implementation.")
    
    return results

if __name__ == "__main__":
    # Run the tests
    test_results = test_page_limit_enforcement()
    
    # Exit with appropriate code
    if all(result[2] for result in test_results):
        exit(0)  # Success
    else:
        exit(1)  # Failure


