#!/usr/bin/env python3
"""
ResuMatch Web Interface
A Flask web application for easy resume generation
"""

import os
import json
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from resume_generator import ResumeGenerator
from job_matcher import ResumeTailor, BulletPoint
import uuid

app = Flask(__name__)
app.secret_key = 'resumatch-secret-key-2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'json'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with resume generation form"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_resume():
    """Generate resume from form data"""
    try:
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        name = request.form.get('name', 'Your Name').strip()
        contact_info = request.form.get('contact_info', 'email@example.com | phone | location').strip()
        
        # Handle experience data
        experience_data = None
        experience_format = request.form.get('experience_format', 'json')
        
        if experience_format == 'json':
            # Parse JSON experience data
            experience_json = request.form.get('experience_json', '{}')
            try:
                experience_data = json.loads(experience_json)
            except json.JSONDecodeError:
                flash('Invalid JSON format in experience data', 'error')
                return redirect(url_for('index'))
        
        elif experience_format == 'text':
            # Use plain text experience
            experience_data = request.form.get('experience_text', '')
        
        # Validate inputs
        if not job_description:
            flash('Job description is required', 'error')
            return redirect(url_for('index'))
        
        if not experience_data:
            flash('Experience data is required', 'error')
            return redirect(url_for('index'))
        
        # Generate unique filename
        resume_id = str(uuid.uuid4())[:8]
        output_filename = f"resume_{resume_id}.pdf"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Initialize resume generator
        free_mode = request.form.get('free_mode') == 'on'
        use_openai = request.form.get('use_openai') == 'on' and not free_mode
        
        generator = ResumeGenerator(
            use_openai=use_openai,
            max_pages=int(request.form.get('max_pages', 2)),
            include_projects=request.form.get('include_projects') == 'on'
        )
        
        # Generate resume
        result = generator.generate_resume(
            job_description=job_description,
            experience_data=experience_data,
            output_path=output_path,
            name=name,
            contact_info=contact_info
        )
        
        if result:
            # Check if result is an HTML file (fallback case)
            if result.endswith('.html'):
                # Update filename to reflect HTML format
                html_filename = f"resume_{resume_id}.html"
                html_path = os.path.join(UPLOAD_FOLDER, html_filename)
                
                # Copy the HTML file to uploads directory
                import shutil
                shutil.copy2(result, html_path)
                
                flash(f'Resume generated successfully! ID: {resume_id} (HTML format)', 'success')
                return jsonify({
                    'success': True,
                    'message': 'Resume generated successfully (HTML format)',
                    'download_url': url_for('download_resume', filename=html_filename),
                    'resume_id': resume_id
                })
            else:
                # PDF was generated successfully
                flash(f'Resume generated successfully! ID: {resume_id}', 'success')
                return jsonify({
                    'success': True,
                    'message': 'Resume generated successfully',
                    'download_url': url_for('download_resume', filename=output_filename),
                    'resume_id': resume_id
                })
        else:
            flash('Failed to generate resume', 'error')
            return jsonify({'success': False, 'message': 'Failed to generate resume'})
    
    except Exception as e:
        flash(f'Error generating resume: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download/<filename>')
def download_resume(filename):
    """Download generated resume"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            flash('Resume file not found', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error downloading resume: {str(e)}', 'error')
        return redirect(url_for('index'))



@app.route('/api/sample-data')
def get_sample_data():
    """Get sample data for the interface"""
    sample_experience = {
        "name": "Ammr Abbasher",
        "contact": {
            "email": "AmmrAbbasher@gmail.com",
            "phone": "817-575-7791",
            "location": "Dallas, TX, USA",
            "linkedin": "LinkedIn",
            "github": "GitHub"
        },
        "summary": "Detail-oriented Data Automation & Integration Analyst with 2.5+ years driving revenue operations optimization through data-driven automation, ETL workflows, and cross-platform system integration. Proficient in Python scripting, SQL querying, and REST API development to streamline quote-to-cash processes across CPQ, CRM, and ERP platforms. Experienced collaborating with sales, IT, and finance stakeholders to gather requirements, design scalable technical solutions, and lead user acceptance testing (UAT). Currently pursuing Salesforce Certified Administrator to deepen CRM and workflow expertise and expand into automation and cloud roles.",
        "experience": [
            {
                "title": "Business Systems Analyst & Data Automation Specialist",
                "company": "Flowserve",
                "duration": "January 2023 - Present",
                "description": [
                    "Automated CPQ pricing validation, quote accuracy checks, and approval workflows using Python, SQL, and Excel VBA, reducing manual processing time by 50%",
                    "Designed and maintained REST API integrations linking Oracle CPQ, Salesforce CRM, and ERP systems (JD Edwards, Great Plains) to synchronize real-time sales data and pricing information",
                    "Developed custom guided selling flows and complex pricing rules within Oracle CPQ to accelerate quote-to-cash cycles for diverse product configurations",
                    "Built SQL-based sales dashboards and reports visualizing quote statuses, margin analysis, and key sales KPIs for executive leadership, enabling data-driven decisions",
                    "Led stakeholder engagement, requirements gathering, and user acceptance testing (UAT) for over 100 global users, increasing user adoption and reducing quote errors",
                    "Collaborated in Agile teams using Jira and Azure DevOps for sprint planning, backlog grooming, and iterative delivery of system enhancements",
                    "Authored detailed technical documentation covering API workflows, business process logic, and automation scripts to support knowledge transfer and ongoing maintenance"
                ]
            },
            {
                "title": "Software Developer / Business Analyst Intern",
                "company": "Salesforce",
                "duration": "April 2021 - August 2021",
                "description": [
                    "Collaborated with Solution Architects and MuleSoft Business Analysts to collect and validate client requirements for enterprise integration projects",
                    "Supported requirements analysis, use case development, and success criteria definition, improving alignment between technical teams and business stakeholders",
                    "Participated in Agile ceremonies and contributed to project scoping, effort estimation, and stakeholder communication",
                    "Gained hands-on exposure to Salesforce ecosystem tools, data mapping for CRM-ERP synchronization, and CPQ configuration basics",
                    "Documented business process flows, user stories, and lessons learned for internal knowledge bases, facilitating team learning and continuous improvement"
                ]
            }
        ],
        "skills": [
            "Python (scripting, automation)",
            "SQL (PostgreSQL, MySQL)",
            "Excel VBA",
            "JavaScript (ES6 basics)",
            "Oracle CPQ (BML, BMQL, Commerce Flows)",
            "Salesforce CRM",
            "ERP systems (JD Edwards, Great Plains)",
            "REST APIs",
            "Postman",
            "AWS (EC2, S3)",
            "Docker",
            "Azure DevOps",
            "Git",
            "Jira",
            "Workflow Automation",
            "Revenue Operations",
            "Quote-to-Cash",
            "Requirements Gathering",
            "UAT",
            "Data Analysis",
            "ETL Workflows",
            "Power BI (basic)",
            "Agile/Scrum",
            "Cross-Functional Collaboration",
            "Technical Writing",
            "Stakeholder Management"
        ],
        "certifications": [
            "Salesforce Certified Administrator (In Progress, Est. August 2025)",
            "Oracle CPQ Developer 2024 Certified Implementation Professional",
            "JavaScript Algorithms and Data Structures – FreeCodeCamp"
        ],
        "education": [
            {
                "degree": "Bachelor of Business Administration: Business Computer Information Systems & Marketing Business Analytics",
                "institution": "University of North Texas (UNT)",
                "year": "2020",
                "gpa": "GPA: 3.5"
            }
        ],
        "projects": [
            {
                "name": "Full Stack Task Manager",
                "description": [
                    "Developed a task management application using React, Node.js, PostgreSQL, and JWT authentication",
                    "Deployed on AWS EC2 with Docker for containerized scalability",
                    "Implemented user authentication, CRUD operations, and real-time task updates"
                ]
            },
            {
                "name": "Weather App",
                "description": [
                    "Created a React frontend integrated with OpenWeatherMap API showcasing data fetching, dynamic UI updates, and error handling"
                ]
            }
        ]
    }
    
    sample_job = """Business Systems Analyst - Revenue Operations

We are seeking a talented Business Systems Analyst to join our Revenue Operations team. You will be responsible for optimizing our quote-to-cash processes and integrating CRM/ERP systems.

Requirements:
- 2+ years of experience with business systems analysis
- Strong experience with Salesforce CRM and Oracle CPQ
- Experience with Python scripting and SQL databases
- Knowledge of REST API integrations
- Experience with workflow automation and process optimization
- Understanding of revenue operations and quote-to-cash processes
- Experience with requirements gathering and UAT
- Knowledge of Agile methodologies and stakeholder management

Preferred Qualifications:
- Salesforce Administrator certification
- Experience with ERP systems (JD Edwards, Great Plains)
- Experience with Azure DevOps and Jira
- Knowledge of data analysis and reporting tools

Responsibilities:
- Design and implement workflow automation solutions
- Integrate Salesforce CRM with Oracle CPQ and ERP systems
- Develop custom pricing rules and guided selling flows
- Build SQL-based dashboards and reports for sales KPIs
- Collaborate with stakeholders to gather requirements
- Lead user acceptance testing and system training
- Document business processes and technical workflows"""
    
    sample_bullets = """TEXT: Automated CPQ pricing validation, quote accuracy checks, and approval workflows using Python, SQL, and Excel VBA, reducing manual processing time by 50%
TAGS: Python, SQL, Excel VBA, Automation, CPQ, Workflow

TEXT: Designed and maintained REST API integrations linking Oracle CPQ, Salesforce CRM, and ERP systems (JD Edwards, Great Plains) to synchronize real-time sales data
TAGS: REST API, Oracle CPQ, Salesforce, ERP, Integration, Data Synchronization

TEXT: Developed custom guided selling flows and complex pricing rules within Oracle CPQ to accelerate quote-to-cash cycles for diverse product configurations
TAGS: Oracle CPQ, Guided Selling, Pricing Rules, Quote-to-Cash, Business Logic

TEXT: Built SQL-based sales dashboards and reports visualizing quote statuses, margin analysis, and key sales KPIs for executive leadership
TAGS: SQL, Dashboards, Reporting, KPIs, Data Visualization, Executive Reporting

TEXT: Led stakeholder engagement, requirements gathering, and user acceptance testing (UAT) for over 100 global users, increasing user adoption
TAGS: Stakeholder Management, Requirements Gathering, UAT, User Training, Change Management

TEXT: Collaborated in Agile teams using Jira and Azure DevOps for sprint planning, backlog grooming, and iterative delivery of system enhancements
TAGS: Agile, Jira, Azure DevOps, Sprint Planning, Project Management"""
    
    return jsonify({
        'experience': sample_experience,
        'job_description': sample_job,
        'bullets': sample_bullets
    })

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting ResuMatch on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌐 Access at: http://localhost:{port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port) 