#!/usr/bin/env python3
"""
ResuMatch Web Interface - Heroku Production Version
A Flask web application for easy resume generation
"""

import os
import json
import tempfile
from pathlib import Path
import uuid
import re
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from resume_generator_simple import SimpleResumeGenerator
from pdf_generator import PDFResumeGenerator

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

@app.route('/form', methods=['GET', 'POST'])
def form_submit():
    """Handle form submission and generate resume"""
    if request.method == 'GET':
        return render_template('form.html')
    
    # POST method handling
    try:
        # Get form data directly from request
        summary = request.form.get('summary', '').strip()
        job_title = request.form.get('job_title', '').strip()
        company = request.form.get('company', '').strip()
        job_description = request.form.get('job_description', '').strip()
        skills = request.form.get('skills', '').strip()
        
        # Basic validation
        if not all([summary, job_title, company, job_description, skills]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            })
        
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
        
        # Generate unique filename for both HTML and PDF
        resume_id = str(uuid.uuid4())[:8]
        html_filename = f"resume_{resume_id}.html"
        pdf_filename = f"resume_{resume_id}.pdf"
        
        html_path = os.path.join(UPLOAD_FOLDER, html_filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        # Generate HTML version
        html_generator = SimpleResumeGenerator(
            max_pages=2,
            include_projects=False
        )
        
        html_result = html_generator.generate_resume(
            job_description=job_description,
            experience_data=experience_data,
            output_path=html_path,
            name="Your Name",  # Default name
            contact_info="email@example.com | phone | location"  # Default contact
        )
        
        # Generate PDF version
        pdf_generator = PDFResumeGenerator()
        pdf_result = pdf_generator.generate_pdf(
            experience_data=experience_data,
            output_path=pdf_path,
            name="Your Name",  # Default name
            contact_info="email@example.com | phone | location"  # Default contact
        )
        
        if html_result and os.path.exists(html_path) and pdf_result and os.path.exists(pdf_path):
            # Both formats generated successfully
            return jsonify({
                'success': True,
                'message': 'Resume generated successfully in both HTML and PDF formats',
                'view_url': url_for('view_resume', filename=html_filename),
                'html_download_url': url_for('download_resume', filename=html_filename),
                'pdf_download_url': url_for('download_resume', filename=pdf_filename),
                'resume_id': resume_id,
                'formats': ['html', 'pdf']
            })
        elif html_result and os.path.exists(html_path):
            # Only HTML generated
            return jsonify({
                'success': True,
                'message': 'Resume generated successfully (HTML format)',
                'view_url': url_for('view_resume', filename=html_filename),
                'download_url': url_for('download_resume', filename=html_filename),
                'resume_id': resume_id,
                'format': 'html'
            })
        else:
            flash('Failed to generate resume', 'error')
            return jsonify({'success': False, 'message': 'Failed to generate resume'})
    
    except Exception as e:
        flash(f'Error generating resume: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/detailed-form', methods=['GET', 'POST'])
def detailed_form():
    """Detailed form page for comprehensive resume creation"""
    if request.method == 'GET':
        return render_template('detailed_form.html')
    
    # POST method handling for detailed form
    try:
        # Debug: Print all received form data
        print("🔍 Detailed form submission received")
        print("📝 Form data received:")
        for key, value in request.form.items():
            print(f"   {key}: {value}")
        
        # Get form data from the detailed form
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        linkedin = request.form.get('linkedin', '').strip()
        github = request.form.get('github', '').strip()
        summary = request.form.get('summary', '').strip()
        skills = request.form.get('skills', '').strip()
        target_job_description = request.form.get('target_job_description', '').strip()
        
        print(f"📋 Extracted data:")
        print(f"   Name: '{name}'")
        print(f"   Email: '{email}'")
        print(f"   Summary: '{summary}'")
        print(f"   Skills: '{skills}'")
        print(f"   Target Job Description: '{target_job_description[:100]}{'...' if len(target_job_description) > 100 else ''}'")
        
        # Get experience data (multiple entries)
        experience_data = []
        experience_count = 0
        
        # First, find all experience entries by looking for any index
        experience_indices = set()
        for key in request.form.keys():
            if key.startswith('experience[') and '][title]' in key:
                # Extract the index from experience[index][title]
                index_match = re.search(r'experience\[(\d+)\]\[title\]', key)
                if index_match:
                    experience_indices.add(int(index_match.group(1)))
        
        # Sort indices to process in order
        for index in sorted(experience_indices):
            title = request.form.get(f'experience[{index}][title]', '').strip()
            company = request.form.get(f'experience[{index}][company]', '').strip()
            duration = request.form.get(f'experience[{index}][duration]', '').strip()
            description = request.form.get(f'experience[{index}][description]', '').strip()
            
            print(f"   Experience {index}:")
            print(f"     Title: '{title}'")
            print(f"     Company: '{company}'")
            print(f"     Description: '{description}'")
            
            if title and company and description:  # Only add if required fields are filled
                experience_data.append({
                    "title": title,
                    "company": company,
                    "duration": duration,
                    "description": [description]  # Convert to list format
                })
        
        print(f"   Total experience entries: {len(experience_data)}")
        
        # Get education data (multiple entries)
        education_data = []
        
        # First, find all education entries by looking for any index
        education_indices = set()
        for key in request.form.keys():
            if key.startswith('education[') and '][degree]' in key:
                # Extract the index from education[index][degree]
                index_match = re.search(r'education\[(\d+)\]\[degree\]', key)
                if index_match:
                    education_indices.add(int(index_match.group(1)))
        
        # Sort indices to process in order
        for index in sorted(education_indices):
            degree = request.form.get(f'education[{index}][degree]', '').strip()
            institution = request.form.get(f'education[{index}][institution]', '').strip()
            year = request.form.get(f'education[{index}][year]', '').strip()
            
            if degree and institution:  # Only add if required fields are filled
                education_data.append({
                    "degree": degree,
                    "institution": institution,
                    "year": year
                })
        
        # Basic validation
        print(f"🔍 Validation check:")
        print(f"   Name filled: {bool(name)}")
        print(f"   Email filled: {bool(email)}")
        print(f"   Summary filled: {bool(summary)}")
        print(f"   Skills filled: {bool(skills)}")
        print(f"   Target Job Description filled: {bool(target_job_description)}")
        print(f"   Experience entries: {len(experience_data)}")
        
        if not all([name, email, summary, skills, target_job_description]) or not experience_data:
            missing_fields = []
            if not name: missing_fields.append("Name")
            if not email: missing_fields.append("Email")
            if not summary: missing_fields.append("Summary")
            if not skills: missing_fields.append("Skills")
            if not target_job_description: missing_fields.append("Target Job Description")
            if not experience_data: missing_fields.append("Work Experience")
            
            error_msg = f"Please fill in all required fields: {', '.join(missing_fields)}."
            print(f"❌ Validation failed: {error_msg}")
            return jsonify({
                'success': False,
                'message': error_msg
            })
        
        # Convert form data to JSON format expected by resume generator
        resume_data = {
            "name": name,
            "contact_info": f"{email} | {phone} | {location}",
            "summary": summary,
            "experience": experience_data,
            "education": education_data,
            "skills": [s.strip() for s in skills.split(",") if s.strip()],
            "certifications": [],
            "projects": [],
            "linkedin": linkedin,
            "github": github
        }
        
        # Generate unique filename for both HTML and PDF
        resume_id = str(uuid.uuid4())[:8]
        html_filename = f"resume_{resume_id}.html"
        pdf_filename = f"resume_{resume_id}.pdf"
        
        html_path = os.path.join(UPLOAD_FOLDER, html_filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        # Generate HTML version
        html_generator = SimpleResumeGenerator(
            max_pages=2,
            include_projects=False
        )
        
        # Use target job description for intelligent bullet point generation
        # If no target job description provided, fall back to first experience description
        job_description_for_generation = target_job_description if target_job_description else (experience_data[0]['description'][0] if experience_data else summary)
        
        html_result = html_generator.generate_resume(
            job_description=job_description_for_generation,
            experience_data=resume_data,
            output_path=html_path,
            name=name,
            contact_info=resume_data["contact_info"]
        )
        
        # Generate PDF version
        pdf_generator = PDFResumeGenerator()
        pdf_result = pdf_generator.generate_pdf(
            experience_data=resume_data,
            output_path=pdf_path,
            name=name,
            contact_info=resume_data["contact_info"]
        )
        
        if html_result and os.path.exists(html_path) and pdf_result and os.path.exists(pdf_path):
            # Both formats generated successfully
            return jsonify({
                'success': True,
                'message': 'Resume generated successfully in both HTML and PDF formats',
                'view_url': url_for('view_resume', filename=html_filename),
                'html_download_url': url_for('download_resume', filename=html_filename),
                'pdf_download_url': url_for('download_resume', filename=pdf_filename),
                'resume_id': resume_id,
                'formats': ['html', 'pdf']
            })
        elif html_result and os.path.exists(html_path):
            # Only HTML generated
            return jsonify({
                'success': True,
                'message': 'Resume generated successfully (HTML format)',
                'view_url': url_for('view_resume', filename=html_filename),
                'download_url': url_for('download_resume', filename=html_filename),
                'resume_id': resume_id,
                'format': 'html'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate resume. Please try again.'
            })
    
    except Exception as e:
        print(f"💥 Error in detailed form processing: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing detailed form: {str(e)}'
        })

@app.route('/dashboard')
def dashboard():
    """User dashboard showing resume history and analytics"""
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    """User profile page"""
    return render_template('profile.html')

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
        
        # Generate unique filename for HTML (since SimpleResumeGenerator creates HTML)
        resume_id = str(uuid.uuid4())[:8]
        html_filename = f"resume_{resume_id}.html"
        output_path = os.path.join(UPLOAD_FOLDER, html_filename)
        
        # Initialize resume generator
        generator = SimpleResumeGenerator(
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
        
        if result and os.path.exists(result):
            # HTML was generated successfully
            flash(f'Resume generated successfully! ID: {resume_id}', 'success')
            return jsonify({
                'success': True,
                'message': 'Resume generated successfully (HTML format)',
                'view_url': url_for('view_resume', filename=html_filename),
                'download_url': url_for('download_resume', filename=html_filename),
                'resume_id': resume_id,
                'format': 'html'
            })
        else:
            flash('Failed to generate resume', 'error')
            return jsonify({'success': False, 'message': 'Failed to generate resume'})
    
    except Exception as e:
        flash(f'Error generating resume: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/view/<filename>')
def view_resume(filename):
    """View generated resume in browser"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        print(f"🔍 View resume request for: {filename}")
        print(f"📁 File path: {file_path}")
        print(f"📂 Upload folder: {UPLOAD_FOLDER}")
        print(f"📄 File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path) and filename.endswith('.html'):
            print(f"✅ Rendering view_resume.html template for {filename}")
            return render_template('view_resume.html', filename=filename, resume_id=filename.replace('.html', '').replace('resume_', ''))
        else:
            print(f"❌ File not found or invalid format: {filename}")
            flash('Resume not found or invalid format', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"💥 Error in view_resume: {str(e)}")
        flash(f'Error viewing resume: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_resume(filename):
    """Download generated resume"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            # For HTML files, serve them in the browser for better viewing
            if filename.endswith('.html'):
                return send_file(file_path, mimetype='text/html')
            else:
                # For other file types, download as attachment
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
    
    # Multiple sample job scenarios
    sample_scenarios = {
        "business_analyst": {
            "summary": "Detail-oriented Business Systems Analyst with 2.5+ years driving revenue operations optimization through data-driven automation, ETL workflows, and cross-platform system integration. Proficient in Python scripting, SQL querying, and REST API development to streamline quote-to-cash processes across CPQ, CRM, and ERP platforms.",
            "job_title": "Business Systems Analyst",
            "company": "Flowserve",
            "job_description": "We are seeking a talented Business Systems Analyst to join our Revenue Operations team. You will be responsible for optimizing our quote-to-cash processes and integrating CRM/ERP systems.\n\nRequirements:\n- 2+ years of experience with business systems analysis\n- Strong experience with Salesforce CRM and Oracle CPQ\n- Experience with Python scripting and SQL databases\n- Knowledge of REST API integrations\n- Experience with workflow automation and process optimization",
            "skills": "Python, SQL, Salesforce CRM, Oracle CPQ, REST APIs, Data Analysis, ETL Workflows, Workflow Automation, Requirements Gathering, UAT, Agile/Scrum, Stakeholder Management"
        },
        "data_analyst": {
            "summary": "Experienced Data Analyst with expertise in transforming complex business data into actionable insights. Skilled in SQL, Python, and data visualization tools to drive strategic decision-making and process improvements across multiple business units.",
            "job_title": "Senior Data Analyst",
            "company": "TechCorp",
            "job_description": "We are looking for a Senior Data Analyst to join our Analytics team. You will be responsible for analyzing business data, creating reports, and providing insights to support strategic decision-making.\n\nRequirements:\n- 3+ years of experience in data analysis\n- Strong SQL and Python programming skills\n- Experience with data visualization tools (Tableau, Power BI)\n- Knowledge of statistical analysis and modeling\n- Experience with ETL processes and data warehousing",
            "skills": "SQL, Python, R, Tableau, Power BI, Excel, Statistical Analysis, Data Visualization, ETL, Data Warehousing, Business Intelligence, A/B Testing"
        },
        "software_developer": {
            "summary": "Full-stack Software Developer with 3+ years of experience building scalable web applications and APIs. Proficient in modern JavaScript frameworks, Python backend development, and cloud deployment using AWS and Docker.",
            "job_title": "Full-Stack Developer",
            "company": "InnovateTech",
            "job_description": "We are seeking a Full-Stack Developer to join our engineering team. You will be responsible for developing and maintaining web applications, APIs, and database systems.\n\nRequirements:\n- 3+ years of full-stack development experience\n- Strong JavaScript/TypeScript and Python skills\n- Experience with React, Node.js, and Django/Flask\n- Knowledge of database design and SQL\n- Experience with cloud platforms (AWS, Azure, GCP)",
            "skills": "JavaScript, TypeScript, React, Node.js, Python, Django, Flask, SQL, PostgreSQL, MongoDB, AWS, Docker, Git, REST APIs, GraphQL"
        },
        "salesforce_admin": {
            "summary": "Certified Salesforce Administrator with 2+ years of experience managing Salesforce orgs, implementing automation workflows, and optimizing business processes. Skilled in user management, security, and custom object development.",
            "job_title": "Salesforce Administrator",
            "company": "SalesForce Solutions",
            "job_description": "We are looking for a Salesforce Administrator to join our team. You will be responsible for managing our Salesforce org, implementing automation, and ensuring optimal system performance.\n\nRequirements:\n- 2+ years of Salesforce administration experience\n- Salesforce Administrator certification\n- Experience with Process Builder, Flow, and Workflow Rules\n- Knowledge of Salesforce security and user management\n- Experience with custom objects, fields, and validation rules",
            "skills": "Salesforce CRM, Process Builder, Flow, Workflow Rules, User Management, Security, Custom Objects, Validation Rules, Reports & Dashboards, Data Import/Export, Apex, Lightning Components"
        }
    }
    
    return jsonify({
        'scenarios': sample_scenarios,
        'current_scenario': 'business_analyst'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting ResuMatch on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌐 Access at: http://localhost:{port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
