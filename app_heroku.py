#!/usr/bin/env python3
"""
ResuMatch Web Interface - Heroku Production Version
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
app.secret_key = os.environ.get('SECRET_KEY', 'resumatch-secret-key-2024')

# Configuration for Heroku
UPLOAD_FOLDER = '/tmp'  # Use temp directory on Heroku
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

@app.route('/form')
def form():
    """Resume form page"""
    return render_template('form.html')

@app.route('/form', methods=['POST'])
def form_submit():
    """Handle form submission and generate resume"""
    try:
        # Get form data directly from request
        summary = request.form.get('summary', '').strip()
        job_title = request.form.get('job_title', '').strip()
        company = request.form.get('company', '').strip()
        job_description = request.form.get('job_description', '').strip()
        skills = request.form.get('skills', '').strip()
        
        # Basic validation
        if not all([summary, job_title, company, job_description, skills]):
            flash('All fields are required', 'error')
            return redirect('/form')
        
        # Convert form data to JSON format expected by resume generator
        experience_data = {
            "summary": summary,
            "experience": [{
                "title": job_title,
                "company": company,
                "description": [job_description],  # Convert to list format
                "duration": "Current"  # Default duration
            }],
            "skills": [s.strip() for s in skills.split(",") if s.strip()],
            "certifications": [],
            "projects": []
        }
        
        # Generate unique filename
        resume_id = str(uuid.uuid4())[:8]
        output_filename = f"resume_{resume_id}.pdf"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Initialize resume generator with default settings
        generator = ResumeGenerator(
            use_openai=False,  # Default to free mode
            max_pages=2,
            include_projects=False
        )
        
        # Generate resume using existing logic
        result = generator.generate_resume(
            job_description=job_description,
            experience_data=experience_data,
            output_path=output_path,
            name="Your Name",  # Default name
            contact_info="email@example.com | phone | location"  # Default contact
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
                return redirect(url_for('download_resume', filename=html_filename))
            else:
                # PDF was generated successfully
                flash(f'Resume generated successfully! ID: {resume_id}', 'success')
                return redirect(url_for('download_resume', filename=output_filename))
        else:
            flash('Failed to generate resume', 'error')
            return redirect('/form')
            
    except Exception as e:
        flash(f'Error generating resume: {str(e)}', 'error')
        return redirect('/form')

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
        ]
    }
    
    return jsonify({
        'experience': sample_experience,
        'job_description': "Business Systems Analyst - Revenue Operations\n\nWe are seeking a talented Business Systems Analyst to join our Revenue Operations team. You will be responsible for optimizing our quote-to-cash processes and integrating CRM/ERP systems.",
        'bullets': "Sample bullet points for testing..."
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting ResuMatch on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌐 Access at: http://localhost:{port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
