#!/usr/bin/env python3
"""
Generate targeted resumes for specific job roles
"""

import os
import json
import subprocess
from datetime import datetime

# Job templates and their target titles
JOB_TARGETS = {
    "revops_developer": {
        "template": "job_templates/revops_developer.txt",
        "title": "RevOps Developer",
        "summary_focus": "RevOps automation, CPQ integration, workflow optimization"
    },
    "business_systems_analyst": {
        "template": "job_templates/business_systems_analyst.txt", 
        "title": "Business Systems Analyst",
        "summary_focus": "Business analysis, CRM optimization, requirements gathering"
    },
    "salesforce_administrator": {
        "template": "job_templates/salesforce_administrator.txt",
        "title": "Salesforce Administrator",
        "summary_focus": "Salesforce CRM, system administration, user support"
    },
    "data_analyst": {
        "template": "job_templates/data_analyst.txt",
        "title": "Data Analyst",
        "summary_focus": "Data analysis, SQL, Python automation, business intelligence"
    }
}

def generate_resume_for_role(role_key, job_info):
    """Generate a targeted resume for a specific role"""
    
    print(f"\n🎯 Generating resume for: {job_info['title']}")
    print(f"📄 Template: {job_info['template']}")
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ammr_{role_key}_{timestamp}.pdf"
    
    # Run the resume generator
    cmd = [
        "python3", "cli.py",
        "--job-file", job_info['template'],
        "--experience-file", "my_experience.json",
        "--output", output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Successfully generated: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating resume: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return None

def generate_job_tailor_analysis(role_key, job_info):
    """Generate job tailor analysis for a specific role"""
    
    print(f"\n🔍 Analyzing job match for: {job_info['title']}")
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ammr_{role_key}_analysis_{timestamp}.json"
    
    # Run the job tailor
    cmd = [
        "python3", "job_tailor_cli.py",
        "--job-file", job_info['template'],
        "--bullets", "my_bullets.json",
        "--output", output_file,
        "--top-n", "8"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Successfully generated analysis: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating analysis: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    """Generate targeted resumes for all job roles"""
    
    print("🚀 ResuMatch - Targeted Resume Generator")
    print("=" * 50)
    
    generated_files = []
    
    for role_key, job_info in JOB_TARGETS.items():
        print(f"\n{'='*60}")
        print(f"🎯 Processing: {job_info['title']}")
        print(f"📋 Focus: {job_info['summary_focus']}")
        
        # Generate standard resume
        resume_file = generate_resume_for_role(role_key, job_info)
        if resume_file:
            generated_files.append(("Resume", resume_file))
        
        # Generate job tailor analysis
        analysis_file = generate_job_tailor_analysis(role_key, job_info)
        if analysis_file:
            generated_files.append(("Analysis", analysis_file))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 GENERATION SUMMARY")
    print("=" * 60)
    
    if generated_files:
        print(f"✅ Successfully generated {len(generated_files)} files:")
        for file_type, filename in generated_files:
            print(f"   📄 {file_type}: {filename}")
    else:
        print("❌ No files were generated successfully")
    
    print(f"\n💡 Next Steps:")
    print("   1. Review the generated PDF resumes")
    print("   2. Check the analysis files for bullet point matching")
    print("   3. Customize as needed for specific applications")
    print("   4. Use the Job Tailor feature for further customization")

if __name__ == "__main__":
    main() 