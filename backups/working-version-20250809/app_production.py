#!/usr/bin/env python3
"""
ResuMatch Production Web Interface
A production-ready Flask application with all current features enabled
"""

import os
import json
import tempfile
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from resume_generator import ResumeGenerator
from job_matcher import ResumeTailor, BulletPoint
import uuid
from dotenv import load_dotenv

# Load production environment variables
load_dotenv('env.production')

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'WARNING')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Security headers
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

# Feature flags - all current features enabled
ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'True').lower() == 'true'
ENABLE_INTELLIGENT_SKILL_MATCHING = os.getenv('ENABLE_INTELLIGENT_SKILL_MATCHING', 'True').lower() == 'true'
ENABLE_JOB_TITLE_OPTIMIZATION = os.getenv('ENABLE_JOB_TITLE_OPTIMIZATION', 'True').lower() == 'true'
ENABLE_SUMMARY_OPTIMIZATION = os.getenv('ENABLE_SUMMARY_OPTIMIZATION', 'True').lower() == 'true'
ENABLE_BULLET_OPTIMIZATION = os.getenv('ENABLE_BULLET_OPTIMIZATION', 'True').lower() == 'true'
ENABLE_PAGE_OPTIMIZATION = os.getenv('ENABLE_PAGE_OPTIMIZATION', 'True').lower() == 'true'

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'txt,json').split(','))
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize monitoring if enabled
if ENABLE_MONITORING:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[FlaskIntegration()],
            environment='production',
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1
        )
        logger.info("Sentry monitoring initialized")
    except ImportError:
        logger.warning("Sentry SDK not available, monitoring disabled")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")

# Add ProxyFix for proper handling behind reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with resume generation form"""
    return render_template('index.html', 
                         env='production',
                         features={
                             'intelligent_skill_matching': ENABLE_INTELLIGENT_SKILL_MATCHING,
                             'job_title_optimization': ENABLE_JOB_TITLE_OPTIMIZATION,
                             'summary_optimization': ENABLE_SUMMARY_OPTIMIZATION,
                             'bullet_optimization': ENABLE_BULLET_OPTIMIZATION,
                             'page_optimization': ENABLE_PAGE_OPTIMIZATION
                         })

@app.route('/generate', methods=['POST'])
def generate_resume():
    """Generate resume from form data with all features enabled"""
    try:
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        name = request.form.get('name', 'Your Name').strip()
        contact_info = request.form.get('contact_info', 'email@example.com | phone | location').strip()
        
        # Handle experience data
        experience_data = None
        experience_format = request.form.get('experience_format', 'json')
        
        if experience_format == 'json':
            experience_json = request.form.get('experience_json', '{}')
            try:
                experience_data = json.loads(experience_json)
            except json.JSONDecodeError:
                logger.error("Invalid JSON format in experience data")
                flash('Invalid JSON format in experience data', 'error')
                return redirect(url_for('index'))
        
        elif experience_format == 'text':
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
        
        # Initialize resume generator with all features enabled
        generator = ResumeGenerator(
            use_openai=request.form.get('use_openai') == 'on',
            max_pages=int(request.form.get('max_pages', 2)),
            include_projects=request.form.get('include_projects') == 'on'
        )
        
        # Generate resume
        logger.info(f"Generating resume {resume_id} for job: {job_description[:100]}...")
        result = generator.generate_resume(
            job_description=job_description,
            experience_data=experience_data,
            output_path=output_path,
            name=name,
            contact_info=contact_info
        )
        
        if result:
            # Log analytics if enabled
            if ENABLE_ANALYTICS:
                log_resume_generation(resume_id, job_description[:100])
            
            logger.info(f"Resume {resume_id} generated successfully")
            flash(f'Resume generated successfully! ID: {resume_id}', 'success')
            return jsonify({
                'success': True,
                'message': 'Resume generated successfully',
                'download_url': url_for('download_resume', filename=output_filename),
                'resume_id': resume_id,
                'environment': 'production',
                'features_enabled': {
                    'intelligent_skill_matching': ENABLE_INTELLIGENT_SKILL_MATCHING,
                    'job_title_optimization': ENABLE_JOB_TITLE_OPTIMIZATION,
                    'summary_optimization': ENABLE_SUMMARY_OPTIMIZATION,
                    'bullet_optimization': ENABLE_BULLET_OPTIMIZATION,
                    'page_optimization': ENABLE_PAGE_OPTIMIZATION
                }
            })
        else:
            logger.error(f"Failed to generate resume {resume_id}")
            flash('Failed to generate resume', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}", exc_info=True)
        
        if ENABLE_MONITORING:
            try:
                import sentry_sdk
                sentry_sdk.capture_exception(e)
            except:
                pass
        
        flash(f'Error generating resume: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_resume(filename):
    """Download generated resume"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            logger.info(f"Downloading resume: {filename}")
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            logger.warning(f"Resume file not found: {filename}")
            flash('Resume file not found', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error downloading resume {filename}: {str(e)}")
        flash('Error downloading resume', 'error')
        return redirect(url_for('index'))

@app.route('/api/sample-data')
def get_sample_data():
    """Get sample data for the form"""
    sample_data = {
        'experience_json': json.dumps({
            "summary": "Experienced software developer with expertise in Python, web development, and AI/ML technologies. Proven track record of delivering scalable solutions and leading technical projects.",
            "experience": [
                {
                    "title": "Software Developer",
                    "company": "Tech Company",
                    "duration": "2022 - Present",
                    "description": [
                        "Developed REST APIs using Django and FastAPI serving 1M+ requests daily",
                        "Implemented microservices architecture with Docker and Kubernetes",
                        "Managed PostgreSQL databases and optimized queries for 40% performance improvement",
                        "Integrated React frontend with REST APIs and implemented real-time features"
                    ],
                    "skills_used": ["Python", "Django", "FastAPI", "React", "PostgreSQL", "Docker", "Kubernetes"]
                }
            ],
            "skills": ["Python", "JavaScript", "React", "Django", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Git"],
            "projects": [
                {
                    "name": "ResuMatch - AI Resume Generator",
                    "description": [
                        "Built intelligent resume generation system using Python, Flask, and NLP",
                        "Implemented AI-powered job title optimization and skill matching",
                        "Created web interface with Bootstrap 5 and professional PDF output"
                    ],
                    "technologies": ["Python", "Flask", "NLP", "AI/ML", "Bootstrap", "WeasyPrint"]
                }
            ],
            "certifications": ["AWS Certified Developer", "Python Professional Certification"],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "school": "University Name",
                    "graduation_year": "2022"
                }
            ]
        }, indent=2),
        'job_description': "We are seeking a talented Senior Python Developer to join our dynamic team. You will be responsible for developing and maintaining high-quality software solutions.\n\nRequirements:\n- 5+ years of experience with Python development\n- Strong experience with Django and web frameworks\n- Experience with cloud platforms (AWS, Azure, GCP)\n- Knowledge of database systems and SQL\n- Experience with CI/CD pipelines\n- Understanding of microservices architecture"
    }
    return jsonify(sample_data)

@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    return jsonify({
        'status': 'healthy',
        'environment': 'production',
        'features_enabled': {
            'intelligent_skill_matching': ENABLE_INTELLIGENT_SKILL_MATCHING,
            'job_title_optimization': ENABLE_JOB_TITLE_OPTIMIZATION,
            'summary_optimization': ENABLE_SUMMARY_OPTIMIZATION,
            'bullet_optimization': ENABLE_BULLET_OPTIMIZATION,
            'page_optimization': ENABLE_PAGE_OPTIMIZATION
        }
    })

def log_resume_generation(resume_id: str, job_description_preview: str):
    """Log resume generation for analytics"""
    try:
        logger.info(f"Resume generation analytics - ID: {resume_id}, Job: {job_description_preview}")
        # Here you could send to analytics service like Google Analytics, Mixpanel, etc.
    except Exception as e:
        logger.error(f"Failed to log analytics: {e}")

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting ResuMatch production server on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
