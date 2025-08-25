#!/usr/bin/env python3
"""
ResuMatch Production Web Interface
Production-ready Flask application with health checks and monitoring
"""

import os
import json
import tempfile
import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from dynamic_resume_generator_enhanced import EnhancedDynamicResumeGenerator
from job_matcher_simple import ResumeTailor, BulletPoint
import uuid
from resume_parser import parse_resume_file
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from models import db, User
from auth import auth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'production-secret-key-change-this')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'production-secret-key-change-this')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Production database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///resumatch.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Add Jinja2 global functions
@app.context_processor
def inject_functions():
    """Inject utility functions into Jinja2 templates"""
    return {
        'min': min,
        'max': max,
        'abs': abs,
        'round': round
    }

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'json', 'pdf', 'docx', 'doc'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(auth)

# Health check endpoint for production
@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Basic health checks
        db_status = "healthy"
        try:
            db.session.execute("SELECT 1")
        except Exception:
            db_status = "unhealthy"
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': str(datetime.datetime.utcnow())
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': str(datetime.datetime.utcnow())
        }), 500

# Database initialization route
@app.route('/init-db')
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
        return jsonify({'success': True, 'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error initializing database: {str(e)}'})

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
    # Check if we have resume data from the detailed form
    resume_data = session.get('resume_data', {})
    return render_template('form.html', resume_data=resume_data)

@app.route('/form', methods=['POST'])
@csrf.exempt
def form_submit():
    """Handle form submission and generate resume"""
    try:
        # Get form data directly from request
        summary = request.form.get('summary', '').strip()
        skills = request.form.get('skills', '').strip()
        job_description = request.form.get('job_description', '').strip()
        enable_ai_transform = request.form.get('enable_ai_transform') == 'on'
        
        # Validate required fields
        if not summary or not skills:
            return jsonify({
                'success': False,
                'message': 'Professional summary and skills are required.'
            }), 400
        
        # Create temporary experience data
        experience_data = {
            'summary': summary,
            'skills': skills.split(','),
            'experience': [],
            'education': [],
            'projects': []
        }
        
        # Generate resume
        generator = EnhancedDynamicResumeGenerator(
            experience_data=experience_data,
            job_description=job_description,
            no_transform=not enable_ai_transform
        )
        
        # Generate HTML resume
        html_content = generator.generate_html_resume()
        
        # Generate unique filename
        filename = f"resume_{uuid.uuid4().hex[:8]}.html"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return jsonify({
            'success': True,
            'message': 'Resume generated successfully!',
            'download_url': url_for('download_resume', filename=filename, _external=True)
        })
        
    except Exception as e:
        app.logger.error(f"Error generating resume: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating resume: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_resume(filename):
    """Download generated resume file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/detailed-form')
def detailed_form():
    """Detailed resume form page"""
    return render_template('detailed_form.html')

@app.route('/generate', methods=['POST'])
def generate_resume():
    """Generate resume from detailed form data"""
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        # Extract basic information
        name = form_data.get('name', '')
        email = form_data.get('email', '')
        phone = form_data.get('phone', '')
        location = form_data.get('location', '')
        linkedin = form_data.get('linkedin', '')
        github = form_data.get('github', '')
        summary = form_data.get('summary', '')
        skills = form_data.get('skills', '')
        job_description = form_data.get('job_description', '')
        enable_ai_transform = form_data.get('enable_ai_transform') == 'on'
        
        # Validate required fields
        if not name or not summary or not skills:
            return jsonify({
                'success': False,
                'message': 'Name, professional summary, and skills are required.'
            }), 400
        
        # Create experience data structure
        experience_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'github': github,
            'summary': summary,
            'skills': [skill.strip() for skill in skills.split(',') if skill.strip()],
            'experience': [],
            'education': [],
            'projects': []
        }
        
        # Extract experience items
        i = 0
        while f'experience[{i}][title]' in form_data:
            title = form_data.get(f'experience[{i}][title]', '')
            company = form_data.get(f'experience[{i}][company]', '')
            duration = form_data.get(f'experience[{i}][duration]', '')
            description = form_data.get(f'experience[{i}][description]', '')
            
            if title and company:
                experience_data['experience'].append({
                    'title': title,
                    'company': company,
                    'duration': duration,
                    'description': description
                })
            i += 1
        
        # Extract education items
        i = 0
        while f'education[{i}][degree]' in form_data:
            degree = form_data.get(f'education[{i}][degree]', '')
            institution = form_data.get(f'education[{i}][institution]', '')
            year = form_data.get(f'education[{i}][year]', '')
            gpa = form_data.get(f'education[{i}][gpa]', '')
            field = form_data.get(f'education[{i}][field]', '')
            
            if degree and institution:
                experience_data['education'].append({
                    'degree': degree,
                    'institution': institution,
                    'year': year,
                    'gpa': gpa,
                    'field': field
                })
            i += 1
        
        # Extract project items
        i = 0
        while f'projects[{i}][name]' in form_data:
            name = form_data.get(f'projects[{i}][name]', '')
            technologies = form_data.get(f'projects[{i}][technologies]', '')
            description = form_data.get(f'projects[{i}][description]', '')
            
            if name and description:
                experience_data['projects'].append({
                    'name': name,
                    'technologies': technologies,
                    'description': description
                })
            i += 1
        
        # Generate resume
        generator = EnhancedDynamicResumeGenerator(
            experience_data=experience_data,
            job_description=job_description,
            no_transform=not enable_ai_transform
        )
        
        # Generate HTML resume
        html_content = generator.generate_html_resume()
        
        # Generate unique filename
        filename = f"resume_{uuid.uuid4().hex[:8]}.html"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return jsonify({
            'success': True,
            'message': 'Resume generated successfully!',
            'download_url': url_for('download_resume', filename=filename, _external=True)
        })
        
    except Exception as e:
        app.logger.error(f"Error generating resume: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating resume: {str(e)}'
        }), 500

@app.route('/api/sample-data')
def get_sample_data():
    """Get sample data for form population"""
    try:
        # Load sample data from JSON file
        sample_file = 'my_experience.json'
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
            return jsonify(sample_data)
        else:
            return jsonify({'error': 'Sample data file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample-data/<scenario>')
def get_scenario_data(scenario):
    """Get sample data for specific scenarios"""
    try:
        # Load sample data from JSON file
        sample_file = 'my_experience.json'
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
            
            # Return specific scenario data if available
            if scenario in sample_data:
                return jsonify(sample_data[scenario])
            else:
                return jsonify({'error': f'Scenario {scenario} not found'}), 404
        else:
            return jsonify({'error': 'Sample data file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/view/<filename>')
def view_resume(filename):
    """View generated resume file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Production settings
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
