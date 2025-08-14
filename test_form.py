#!/usr/bin/env python3
"""
Test script for ResuMatch form functionality
"""

import requests
import json

def test_form_submission():
    """Test the form submission endpoint"""
    
    # Test data
    form_data = {
        'summary': 'Experienced Business Systems Analyst with expertise in data automation and system integration.',
        'job_title': 'Business Systems Analyst',
        'company': 'Flowserve',
        'job_description': 'We are seeking a Business Systems Analyst to optimize our quote-to-cash processes and integrate CRM/ERP systems.',
        'skills': 'Python, SQL, Salesforce, REST APIs, Data Analysis, ETL Workflows'
    }
    
    try:
        # Submit form data
        response = requests.post('http://localhost:8000/form', data=form_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 302:  # Redirect after successful submission
            print("✅ Form submission successful - redirecting to download")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing ResuMatch Form Submission...")
    test_form_submission()
