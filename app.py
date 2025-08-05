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
        generator = ResumeGenerator(
            use_openai=request.form.get('use_openai') == 'on',
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

@app.route('/tailor', methods=['POST'])
def tailor_resume():
    """Tailor resume using Job Tailor feature"""
    try:
        job_description = request.form.get('job_description', '').strip()
        bullets_text = request.form.get('bullets_text', '').strip()
        
        if not job_description or not bullets_text:
            flash('Both job description and bullets are required', 'error')
            return redirect(url_for('index'))
        
        # Parse bullets from text format
        bullets = []
        current_bullet = None
        
        for line in bullets_text.split('\n'):
            line = line.strip()
            if line.startswith('TEXT:'):
                if current_bullet:
                    bullets.append(current_bullet)
                current_bullet = BulletPoint(
                    text=line[5:].strip(),
                    tags=[],
                    category="experience"
                )
            elif line.startswith('TAGS:') and current_bullet:
                tags = [tag.strip() for tag in line[5:].strip().split(',')]
                current_bullet.tags = tags
        
        if current_bullet:
            bullets.append(current_bullet)
        
        if not bullets:
            flash('No valid bullets found in the provided text', 'error')
            return redirect(url_for('index'))
        
        # Initialize tailor
        tailor = ResumeTailor()
        
        # Tailor resume
        tailored_result = tailor.tailor_resume(
            job_description=job_description,
            bullets=bullets,
            top_n=int(request.form.get('top_n', 8))
        )
        
        return jsonify({
            'success': True,
            'result': tailored_result
        })
    
    except Exception as e:
        flash(f'Error tailoring resume: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/sample-data')
def get_sample_data():
    """Get sample data for the interface"""
    sample_experience = {
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
    
    sample_job = """Senior Python Developer

We are seeking a talented Senior Python Developer to join our dynamic team. You will be responsible for developing and maintaining high-quality software solutions.

Requirements:
- 5+ years of experience with Python development
- Strong experience with Django, Flask, or FastAPI frameworks
- Proficiency with PostgreSQL, MySQL, or MongoDB databases
- Experience with AWS cloud services and Docker containerization
- Knowledge of Kubernetes for orchestration
- Familiarity with React, JavaScript, and modern frontend technologies
- Experience with Git version control and CI/CD pipelines
- Understanding of REST APIs and microservices architecture

Responsibilities:
- Design and implement scalable backend services
- Collaborate with frontend developers to integrate APIs
- Optimize database queries and application performance
- Deploy applications using Docker and Kubernetes
- Write clean, maintainable code with proper documentation
- Participate in code reviews and technical discussions
- Mentor junior developers and share best practices"""
    
    sample_bullets = """TEXT: Developed REST APIs using Django and FastAPI serving 1M+ requests daily
TAGS: Python, Django, FastAPI, REST APIs, Backend

TEXT: Implemented microservices architecture with Docker and Kubernetes on AWS
TAGS: Microservices, Docker, Kubernetes, AWS, DevOps

TEXT: Managed PostgreSQL databases and optimized queries for 40% performance improvement
TAGS: PostgreSQL, Database, Performance, SQL

TEXT: Integrated React frontend with REST APIs and implemented real-time features
TAGS: React, JavaScript, Frontend, REST APIs, Real-time

TEXT: Deployed applications using CI/CD pipelines with Jenkins and Git
TAGS: CI/CD, Jenkins, Git, DevOps, Automation"""
    
    return jsonify({
        'experience': sample_experience,
        'job_description': sample_job,
        'bullets': sample_bullets
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 