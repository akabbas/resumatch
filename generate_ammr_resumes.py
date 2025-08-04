#!/usr/bin/env python3
"""
Generate targeted resumes for Ammr's job applications
"""

import json
import os
from datetime import datetime
from simple_resume_generator import SimpleResumeGenerator

# Job targets with their descriptions
JOB_TARGETS = {
    "revops_developer": {
        "title": "RevOps Developer",
        "description": "RevOps Developer position requiring experience with Salesforce CRM, Oracle CPQ, Python automation, REST API integration, workflow optimization, quote-to-cash processes, and revenue operations automation.",
        "focus": "RevOps automation, CPQ integration, workflow optimization"
    },
    "business_systems_analyst": {
        "title": "Business Systems Analyst",
        "description": "Business Systems Analyst role focusing on CRM optimization, requirements gathering, business process mapping, stakeholder management, user training, and system administration for Salesforce and other business systems.",
        "focus": "Business analysis, CRM optimization, requirements gathering"
    },
    "salesforce_administrator": {
        "title": "Salesforce Administrator",
        "description": "Salesforce Administrator position requiring experience with Salesforce CRM administration, user management, system configuration, custom fields, workflows, reports, dashboards, and end-user training.",
        "focus": "Salesforce CRM, system administration, user support"
    },
    "data_analyst": {
        "title": "Data Analyst",
        "description": "Data Analyst role focusing on SQL queries, Python scripting, data analysis, business intelligence, reporting, data visualization, Excel automation, and CRM data analysis for revenue operations.",
        "focus": "Data analysis, SQL, Python automation, business intelligence"
    },
    "crm_automation_engineer": {
        "title": "CRM Automation Engineer",
        "description": "CRM Automation Engineer position requiring experience with workflow automation, Python scripting, CRM system integration, REST API development, business process optimization, and technical support.",
        "focus": "CRM automation, workflow optimization, Python scripting"
    },
    "revenue_operations_analyst": {
        "title": "Revenue Operations Analyst",
        "description": "Revenue Operations Analyst role focusing on quote-to-cash processes, revenue analysis, sales operations, data reporting, process optimization, and cross-functional collaboration with sales and finance teams.",
        "focus": "Revenue operations, data analysis, process optimization"
    }
}

def generate_targeted_resumes():
    """Generate targeted resumes for all job roles"""
    
    print("🚀 Ammr's Targeted Resume Generator")
    print("=" * 50)
    
    # Load experience data
    try:
        with open('my_experience.json', 'r', encoding='utf-8') as f:
            experience_data = json.load(f)
    except FileNotFoundError:
        print("❌ my_experience.json not found. Please create it first.")
        return
    
    generator = SimpleResumeGenerator()
    generated_files = []
    
    for role_key, job_info in JOB_TARGETS.items():
        print(f"\n{'='*60}")
        print(f"🎯 Generating resume for: {job_info['title']}")
        print(f"📋 Focus: {job_info['focus']}")
        
        # Generate resume
        html = generator.generate_resume_html(experience_data, job_info['description'])
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ammr_{role_key}_{timestamp}.html"
        
        # Save file
        generator.save_html(html, filename)
        generated_files.append((job_info['title'], filename))
        
        # Show extracted keywords
        keywords = generator.extract_keywords(job_info['description'])
        print(f"🎯 Keywords matched: {', '.join(keywords[:5])}...")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 GENERATION SUMMARY")
    print("=" * 60)
    
    if generated_files:
        print(f"✅ Successfully generated {len(generated_files)} resumes:")
        for job_title, filename in generated_files:
            print(f"   📄 {job_title}: {filename}")
    else:
        print("❌ No files were generated successfully")
    
    print(f"\n💡 Next Steps:")
    print("   1. Open the HTML files in your browser")
    print("   2. Print to PDF or save as PDF")
    print("   3. Customize as needed for specific applications")
    print("   4. Use the Job Tailor feature for further customization")

def generate_single_resume(role_key: str, custom_description: str = ""):
    """Generate a single targeted resume"""
    
    if role_key not in JOB_TARGETS:
        print(f"❌ Unknown role: {role_key}")
        print(f"Available roles: {', '.join(JOB_TARGETS.keys())}")
        return
    
    job_info = JOB_TARGETS[role_key]
    description = custom_description if custom_description else job_info['description']
    
    print(f"🎯 Generating resume for: {job_info['title']}")
    print(f"📋 Focus: {job_info['focus']}")
    
    # Load experience data
    try:
        with open('my_experience.json', 'r', encoding='utf-8') as f:
            experience_data = json.load(f)
    except FileNotFoundError:
        print("❌ my_experience.json not found. Please create it first.")
        return
    
    generator = SimpleResumeGenerator()
    
    # Generate resume
    html = generator.generate_resume_html(experience_data, description)
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ammr_{role_key}_{timestamp}.html"
    
    # Save file
    generator.save_html(html, filename)
    
    # Show extracted keywords
    keywords = generator.extract_keywords(description)
    print(f"🎯 Keywords matched: {', '.join(keywords)}")
    
    return filename

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Generate single resume
        role_key = sys.argv[1]
        custom_description = sys.argv[2] if len(sys.argv) > 2 else ""
        generate_single_resume(role_key, custom_description)
    else:
        # Generate all resumes
        generate_targeted_resumes() 