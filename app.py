#!/usr/bin/env python3
"""
ResuMatch Web Interface
A Flask web application for easy resume generation
"""

import os
import json
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from dynamic_resume_generator_enhanced import EnhancedDynamicResumeGenerator
from job_matcher import ResumeTailor, BulletPoint
import uuid
from resume_parser import parse_resume_file

app = Flask(__name__)
app.secret_key = 'resumatch-secret-key-2024'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'json', 'pdf', 'docx', 'doc'}
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
    # Check if we have resume data from the detailed form
    resume_data = session.get('resume_data', {})
    return render_template('form.html', resume_data=resume_data)

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
        enable_ai_transform = request.form.get('enable_ai_transform', 'on') == 'on'
        
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
        generator = EnhancedDynamicResumeGenerator(
            use_openai=False,  # Default to free mode
            max_pages=2,
            include_projects=False,
            no_transform=not enable_ai_transform
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
        enable_ai_transform = request.form.get('enable_ai_transform', 'on') == 'on'
        
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
        
        generator = EnhancedDynamicResumeGenerator(
            use_openai=use_openai,
            max_pages=int(request.form.get('max_pages', 2)),
            include_projects=request.form.get('include_projects') == 'on',
            no_transform=not enable_ai_transform
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

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    """Handle resume file upload and parsing"""
    try:
        # Check if file was uploaded
        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['resume_file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type. Please upload PDF or Word document.'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Parse the resume
            parsed_data = parse_resume_file(temp_path)
            
            # Check for parsing errors
            if 'error' in parsed_data:
                return jsonify({
                    'success': False, 
                    'message': f'Failed to parse resume: {parsed_data["error"]}'
                }), 400
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            # Return parsed data
            return jsonify({
                'success': True,
                'message': 'Resume parsed successfully',
                'parsed_data': parsed_data
            })
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
            
    except Exception as e:
        app.logger.error(f"Error processing resume upload: {e}")
        return jsonify({
            'success': False, 
            'message': f'An error occurred while processing your resume: {str(e)}'
        }), 500

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
    """Get sample data for the interface with multiple job descriptions"""
    
    # Multiple realistic job descriptions covering different industries and roles
    job_descriptions = {
        "business_systems_analyst": {
            "title": "Business Systems Analyst - Revenue Operations",
            "company": "Tech Solutions Inc.",
            "description": """Business Systems Analyst - Revenue Operations

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
        },
        
        "data_scientist": {
            "title": "Senior Data Scientist - Machine Learning",
            "company": "DataCorp Analytics",
            "description": """Senior Data Scientist - Machine Learning

We are looking for a Senior Data Scientist to join our growing analytics team. You will be responsible for developing machine learning models and driving data-driven insights across the organization.

Requirements:
- 3+ years of experience in data science or machine learning
- Strong proficiency in Python (pandas, numpy, scikit-learn, tensorflow/pytorch)
- Experience with SQL and database systems
- Knowledge of statistical analysis and experimental design
- Experience with big data technologies (Spark, Hadoop)
- Understanding of machine learning algorithms and model development
- Experience with data visualization tools (Tableau, Power BI, matplotlib)
- Knowledge of cloud platforms (AWS, Azure, GCP)

Preferred Qualifications:
- PhD in Computer Science, Statistics, or related field
- Experience with deep learning and neural networks
- Experience with MLOps and model deployment
- Knowledge of natural language processing
- Experience with A/B testing and causal inference

Responsibilities:
- Develop and deploy machine learning models for business applications
- Analyze large datasets to identify patterns and insights
- Design and conduct experiments to test hypotheses
- Collaborate with engineering teams to integrate ML models
- Communicate findings to stakeholders through visualizations and reports
- Mentor junior data scientists and contribute to team knowledge sharing
- Stay current with latest developments in ML and data science"""
        },
        
        "software_engineer": {
            "title": "Full Stack Software Engineer",
            "company": "InnovateTech Solutions",
            "description": """Full Stack Software Engineer

We are seeking a Full Stack Software Engineer to join our development team. You will be responsible for building scalable web applications and contributing to our product development efforts.

Requirements:
- 2+ years of experience in full stack development
- Strong proficiency in JavaScript/TypeScript and modern frameworks (React, Angular, Vue)
- Experience with backend development (Node.js, Python, Java, or C#)
- Knowledge of database design and SQL/NoSQL databases
- Experience with RESTful APIs and microservices architecture
- Understanding of version control systems (Git)
- Knowledge of cloud platforms (AWS, Azure, GCP)
- Experience with Agile development methodologies

Preferred Qualifications:
- Experience with containerization (Docker, Kubernetes)
- Knowledge of CI/CD pipelines and DevOps practices
- Experience with testing frameworks and TDD
- Understanding of security best practices
- Experience with performance optimization and scalability

Responsibilities:
- Design and implement user-facing features and backend services
- Write clean, maintainable, and efficient code
- Collaborate with product managers and designers
- Participate in code reviews and technical discussions
- Debug and resolve technical issues
- Contribute to technical architecture decisions
- Mentor junior developers and share knowledge"""
        },
        
        "devops_engineer": {
            "title": "DevOps Engineer - Cloud Infrastructure",
            "company": "CloudScale Systems",
            "description": """DevOps Engineer - Cloud Infrastructure

We are looking for a DevOps Engineer to help us build and maintain our cloud infrastructure and CI/CD pipelines. You will be responsible for automating our deployment processes and ensuring system reliability.

Requirements:
- 3+ years of experience in DevOps or infrastructure engineering
- Strong experience with cloud platforms (AWS, Azure, or GCP)
- Experience with containerization (Docker, Kubernetes)
- Knowledge of infrastructure as code (Terraform, CloudFormation)
- Experience with CI/CD tools (Jenkins, GitLab CI, GitHub Actions)
- Understanding of monitoring and logging tools
- Experience with Linux systems administration
- Knowledge of networking and security principles

Preferred Qualifications:
- Experience with serverless architectures
- Knowledge of microservices and distributed systems
- Experience with monitoring tools (Prometheus, Grafana, ELK stack)
- Understanding of security compliance and best practices
- Experience with database administration

Responsibilities:
- Design and implement cloud infrastructure solutions
- Automate deployment and configuration processes
- Monitor system performance and troubleshoot issues
- Implement security best practices and compliance measures
- Collaborate with development teams to optimize deployment workflows
- Maintain and improve CI/CD pipelines
- Document infrastructure and operational procedures
- Participate in on-call rotations for production support"""
        },
        
        "product_manager": {
            "title": "Senior Product Manager - SaaS Platform",
            "company": "ProductFlow Inc.",
            "description": """Senior Product Manager - SaaS Platform

We are seeking a Senior Product Manager to lead product strategy and development for our SaaS platform. You will be responsible for driving product vision and ensuring successful delivery of features.

Requirements:
- 4+ years of experience in product management
- Experience with SaaS or B2B software products
- Strong analytical and problem-solving skills
- Experience with user research and customer interviews
- Knowledge of product analytics and data-driven decision making
- Experience with Agile development methodologies
- Understanding of technical concepts and ability to work with engineering teams
- Strong communication and stakeholder management skills

Preferred Qualifications:
- MBA or advanced degree in business or technology
- Experience with product-led growth strategies
- Knowledge of UX/UI design principles
- Experience with A/B testing and experimentation
- Understanding of pricing and business models

Responsibilities:
- Define product strategy and roadmap
- Conduct market research and competitive analysis
- Gather and prioritize product requirements
- Work closely with engineering teams to deliver features
- Analyze product metrics and user feedback
- Collaborate with marketing and sales teams
- Present product plans to stakeholders and executives
- Mentor junior product managers"""
        },
        
        "data_analyst": {
            "title": "Business Intelligence Analyst",
            "company": "InsightCorp",
            "description": """Business Intelligence Analyst

We are looking for a Business Intelligence Analyst to help us transform data into actionable insights. You will be responsible for creating reports, dashboards, and analytical solutions.

Requirements:
- 2+ years of experience in business intelligence or data analysis
- Strong proficiency in SQL and database systems
- Experience with data visualization tools (Tableau, Power BI, Looker)
- Knowledge of Excel and data manipulation
- Understanding of business metrics and KPIs
- Experience with data modeling and ETL processes
- Strong analytical and problem-solving skills
- Ability to communicate insights to non-technical stakeholders

Preferred Qualifications:
- Experience with Python or R for data analysis
- Knowledge of statistical analysis and hypothesis testing
- Experience with cloud data warehouses (Snowflake, BigQuery, Redshift)
- Understanding of data governance and quality
- Experience with predictive analytics

Responsibilities:
- Create and maintain business intelligence dashboards
- Analyze data to identify trends and insights
- Develop automated reporting solutions
- Collaborate with business stakeholders to understand requirements
- Ensure data accuracy and quality
- Present findings and recommendations to leadership
- Support data-driven decision making across the organization
- Train users on BI tools and reports"""
        },
        
        "salesforce_administrator": {
            "title": "Salesforce Administrator - CRM Specialist",
            "company": "SalesTech Solutions",
            "description": """Salesforce Administrator - CRM Specialist

We are seeking a Salesforce Administrator to manage and optimize our CRM system. You will be responsible for system configuration, user management, and process automation.

Requirements:
- 2+ years of experience as a Salesforce Administrator
- Salesforce Administrator certification
- Experience with Salesforce configuration and customization
- Knowledge of Salesforce security and user management
- Experience with workflow automation and process builder
- Understanding of data management and data quality
- Experience with reporting and dashboards
- Knowledge of Salesforce best practices

Preferred Qualifications:
- Experience with Salesforce CPQ or Sales Cloud
- Knowledge of Apex and Visualforce development
- Experience with Salesforce integrations and APIs
- Understanding of business process optimization
- Experience with change management and user training

Responsibilities:
- Configure and customize Salesforce to meet business needs
- Manage user access and security settings
- Create and maintain workflows and process automation
- Develop reports and dashboards for business users
- Ensure data quality and integrity
- Provide user training and support
- Collaborate with business stakeholders on system improvements
- Stay current with Salesforce releases and best practices"""
        },
        
        "cloud_architect": {
            "title": "Cloud Solutions Architect",
            "company": "CloudFirst Technologies",
            "description": """Cloud Solutions Architect

We are looking for a Cloud Solutions Architect to design and implement cloud-based solutions for our clients. You will be responsible for creating scalable and secure cloud architectures.

Requirements:
- 5+ years of experience in cloud architecture or infrastructure design
- Strong experience with major cloud platforms (AWS, Azure, GCP)
- Experience with containerization and orchestration (Docker, Kubernetes)
- Knowledge of microservices and distributed systems
- Understanding of security and compliance requirements
- Experience with infrastructure as code and automation
- Knowledge of networking and storage solutions
- Strong problem-solving and communication skills

Preferred Qualifications:
- Cloud platform certifications (AWS Solutions Architect, Azure Solutions Architect)
- Experience with serverless architectures
- Knowledge of DevOps and CI/CD practices
- Understanding of cost optimization strategies
- Experience with multi-cloud environments

Responsibilities:
- Design cloud-native solutions for client requirements
- Create technical architecture documents and diagrams
- Lead implementation of cloud solutions
- Ensure security and compliance requirements are met
- Optimize cloud costs and performance
- Mentor development teams on cloud best practices
- Stay current with cloud technologies and trends
- Collaborate with sales teams on solution proposals"""
        }
    }
    
    # Get a random job description (or specific one if requested)
    import random
    selected_job_key = random.choice(list(job_descriptions.keys()))
    selected_job = job_descriptions[selected_job_key]
    
    # Enhanced sample experience data with more diverse scenarios
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
    
    # Enhanced sample bullets with more diverse examples
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
        'job_description': selected_job['description'],
        'job_title': selected_job['title'],
        'company': selected_job['company'],
        'bullets': sample_bullets,
        'available_jobs': list(job_descriptions.keys()),
        'current_job': selected_job_key
    })

@app.route('/api/sample-data/<job_key>')
def get_specific_job_data(job_key):
    """Get sample data for a specific job description"""
    
    # Multiple realistic job descriptions covering different industries and roles
    job_descriptions = {
        "business_systems_analyst": {
            "title": "Business Systems Analyst - Revenue Operations",
            "company": "Tech Solutions Inc.",
            "description": """Business Systems Analyst - Revenue Operations

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
        },
        
        "data_scientist": {
            "title": "Senior Data Scientist - Machine Learning",
            "company": "DataCorp Analytics",
            "description": """Senior Data Scientist - Machine Learning

We are looking for a Senior Data Scientist to join our growing analytics team. You will be responsible for developing machine learning models and driving data-driven insights across the organization.

Requirements:
- 3+ years of experience in data science or machine learning
- Strong proficiency in Python (pandas, numpy, scikit-learn, tensorflow/pytorch)
- Experience with SQL and database systems
- Knowledge of statistical analysis and experimental design
- Experience with big data technologies (Spark, Hadoop)
- Understanding of machine learning algorithms and model development
- Experience with data visualization tools (Tableau, Power BI, matplotlib)
- Knowledge of cloud platforms (AWS, Azure, GCP)

Preferred Qualifications:
- PhD in Computer Science, Statistics, or related field
- Experience with deep learning and neural networks
- Experience with MLOps and model deployment
- Knowledge of natural language processing
- Experience with A/B testing and causal inference

Responsibilities:
- Develop and deploy machine learning models for business applications
- Analyze large datasets to identify patterns and insights
- Design and conduct experiments to test hypotheses
- Collaborate with engineering teams to integrate ML models
- Communicate findings to stakeholders through visualizations and reports
- Mentor junior data scientists and contribute to team knowledge sharing
- Stay current with latest developments in ML and data science"""
        },
        
        "software_engineer": {
            "title": "Full Stack Software Engineer",
            "company": "InnovateTech Solutions",
            "description": """Full Stack Software Engineer

We are seeking a Full Stack Software Engineer to join our development team. You will be responsible for building scalable web applications and contributing to our product development efforts.

Requirements:
- 2+ years of experience in full stack development
- Strong proficiency in JavaScript/TypeScript and modern frameworks (React, Angular, Vue)
- Experience with backend development (Node.js, Python, Java, or C#)
- Knowledge of database design and SQL/NoSQL databases
- Experience with RESTful APIs and microservices architecture
- Understanding of version control systems (Git)
- Knowledge of cloud platforms (AWS, Azure, GCP)
- Experience with Agile development methodologies

Preferred Qualifications:
- Experience with containerization (Docker, Kubernetes)
- Knowledge of CI/CD pipelines and DevOps practices
- Experience with testing frameworks and TDD
- Understanding of security best practices
- Experience with performance optimization and scalability

Responsibilities:
- Design and implement user-facing features and backend services
- Write clean, maintainable, and efficient code
- Collaborate with product managers and designers
- Participate in code reviews and technical discussions
- Debug and resolve technical issues
- Contribute to technical architecture decisions
- Mentor junior developers and share knowledge"""
        },
        
        "devops_engineer": {
            "title": "DevOps Engineer - Cloud Infrastructure",
            "company": "CloudScale Systems",
            "description": """DevOps Engineer - Cloud Infrastructure

We are looking for a DevOps Engineer to help us build and maintain our cloud infrastructure and CI/CD pipelines. You will be responsible for automating our deployment processes and ensuring system reliability.

Requirements:
- 3+ years of experience in DevOps or infrastructure engineering
- Strong experience with cloud platforms (AWS, Azure, or GCP)
- Experience with containerization (Docker, Kubernetes)
- Knowledge of infrastructure as code (Terraform, CloudFormation)
- Experience with CI/CD tools (Jenkins, GitLab CI, GitHub Actions)
- Understanding of monitoring and logging tools
- Experience with Linux systems administration
- Knowledge of networking and security principles

Preferred Qualifications:
- Experience with serverless architectures
- Knowledge of microservices and distributed systems
- Experience with monitoring tools (Prometheus, Grafana, ELK stack)
- Understanding of security compliance and best practices
- Experience with database administration

Responsibilities:
- Design and implement cloud infrastructure solutions
- Automate deployment and configuration processes
- Monitor system performance and troubleshoot issues
- Implement security best practices and compliance measures
- Collaborate with development teams to optimize deployment workflows
- Maintain and improve CI/CD pipelines
- Document infrastructure and operational procedures
- Participate in on-call rotations for production support"""
        },
        
        "product_manager": {
            "title": "Senior Product Manager - SaaS Platform",
            "company": "ProductFlow Inc.",
            "description": """Senior Product Manager - SaaS Platform

We are seeking a Senior Product Manager to lead product strategy and development for our SaaS platform. You will be responsible for driving product vision and ensuring successful delivery of features.

Requirements:
- 4+ years of experience in product management
- Experience with SaaS or B2B software products
- Strong analytical and problem-solving skills
- Experience with user research and customer interviews
- Knowledge of product analytics and data-driven decision making
- Experience with Agile development methodologies
- Understanding of technical concepts and ability to work with engineering teams
- Strong communication and stakeholder management skills

Preferred Qualifications:
- MBA or advanced degree in business or technology
- Experience with product-led growth strategies
- Knowledge of UX/UI design principles
- Experience with A/B testing and experimentation
- Understanding of pricing and business models

Responsibilities:
- Define product strategy and roadmap
- Conduct market research and competitive analysis
- Gather and prioritize product requirements
- Work closely with engineering teams to deliver features
- Analyze product metrics and user feedback
- Collaborate with marketing and sales teams
- Present product plans to stakeholders and executives
- Mentor junior product managers"""
        },
        
        "data_analyst": {
            "title": "Business Intelligence Analyst",
            "company": "InsightCorp",
            "description": """Business Intelligence Analyst

We are looking for a Business Intelligence Analyst to help us transform data into actionable insights. You will be responsible for creating reports, dashboards, and analytical solutions.

Requirements:
- 2+ years of experience in business intelligence or data analysis
- Strong proficiency in SQL and database systems
- Experience with data visualization tools (Tableau, Power BI, Looker)
- Knowledge of Excel and data manipulation
- Understanding of business metrics and KPIs
- Experience with data modeling and ETL processes
- Strong analytical and problem-solving skills
- Ability to communicate insights to non-technical stakeholders

Preferred Qualifications:
- Experience with Python or R for data analysis
- Knowledge of statistical analysis and hypothesis testing
- Experience with cloud data warehouses (Snowflake, BigQuery, Redshift)
- Understanding of data governance and quality
- Experience with predictive analytics

Responsibilities:
- Create and maintain business intelligence dashboards
- Analyze data to identify trends and insights
- Develop automated reporting solutions
- Collaborate with business stakeholders to understand requirements
- Ensure data accuracy and quality
- Present findings and recommendations to leadership
- Support data-driven decision making across the organization
- Train users on BI tools and reports"""
        },
        
        "salesforce_administrator": {
            "title": "Salesforce Administrator - CRM Specialist",
            "company": "SalesTech Solutions",
            "description": """Salesforce Administrator - CRM Specialist

We are seeking a Salesforce Administrator to manage and optimize our CRM system. You will be responsible for system configuration, user management, and process automation.

Requirements:
- 2+ years of experience as a Salesforce Administrator
- Salesforce Administrator certification
- Experience with Salesforce configuration and customization
- Knowledge of Salesforce security and user management
- Experience with workflow automation and process builder
- Understanding of data management and data quality
- Experience with reporting and dashboards
- Knowledge of Salesforce best practices

Preferred Qualifications:
- Experience with Salesforce CPQ or Sales Cloud
- Knowledge of Apex and Visualforce development
- Experience with Salesforce integrations and APIs
- Understanding of business process optimization
- Experience with change management and user training

Responsibilities:
- Configure and customize Salesforce to meet business needs
- Manage user access and security settings
- Create and maintain workflows and process automation
- Develop reports and dashboards for business users
- Ensure data quality and integrity
- Provide user training and support
- Collaborate with business stakeholders on system improvements
- Stay current with Salesforce releases and best practices"""
        },
        
        "cloud_architect": {
            "title": "Cloud Solutions Architect",
            "company": "CloudFirst Technologies",
            "description": """Cloud Solutions Architect

We are looking for a Cloud Solutions Architect to design and implement cloud-based solutions for our clients. You will be responsible for creating scalable and secure cloud architectures.

Requirements:
- 5+ years of experience in cloud architecture or infrastructure design
- Strong experience with major cloud platforms (AWS, Azure, GCP)
- Experience with containerization and orchestration (Docker, Kubernetes)
- Knowledge of microservices and distributed systems
- Understanding of security and compliance requirements
- Experience with infrastructure as code and automation
- Knowledge of networking and storage solutions
- Strong problem-solving and communication skills

Preferred Qualifications:
- Cloud platform certifications (AWS Solutions Architect, Azure Solutions Architect)
- Experience with serverless architectures
- Knowledge of DevOps and CI/CD practices
- Understanding of cost optimization strategies
- Experience with multi-cloud environments

Responsibilities:
- Design cloud-native solutions for client requirements
- Create technical architecture documents and diagrams
- Lead implementation of cloud solutions
- Ensure security and compliance requirements are met
- Optimize cloud costs and performance
- Mentor development teams on cloud best practices
- Stay current with cloud technologies and trends
- Collaborate with sales teams on solution proposals"""
        }
    }
    
    # Check if the requested job key exists
    if job_key not in job_descriptions:
        return jsonify({'error': 'Job not found', 'available_jobs': list(job_descriptions.keys())}), 404
    
    selected_job = job_descriptions[job_key]
    
    # Enhanced sample experience data with more diverse scenarios
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
    
    # Enhanced sample bullets with more diverse examples
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
        'job_description': selected_job['description'],
        'job_title': selected_job['title'],
        'company': selected_job['company'],
        'bullets': sample_bullets,
        'available_jobs': list(job_descriptions.keys()),
        'current_job': job_key
    })

@app.route('/api/job-list')
def get_job_list():
    """Get list of all available job descriptions"""
    job_descriptions = {
        "business_systems_analyst": "Business Systems Analyst - Revenue Operations",
        "data_scientist": "Senior Data Scientist - Machine Learning",
        "software_engineer": "Full Stack Software Engineer",
        "devops_engineer": "DevOps Engineer - Cloud Infrastructure",
        "product_manager": "Senior Product Manager - SaaS Platform",
        "data_analyst": "Business Intelligence Analyst",
        "salesforce_administrator": "Salesforce Administrator - CRM Specialist",
        "cloud_architect": "Cloud Solutions Architect"
    }
    
    return jsonify({
        'jobs': job_descriptions,
        'total_jobs': len(job_descriptions)
    })

@app.route('/api/job-description/<job_key>')
def get_job_description(job_key):
    """Get a specific job description by key"""
    
    job_descriptions = {
        "business_systems_analyst": {
            "title": "Business Systems Analyst - Revenue Operations",
            "company": "Tech Solutions Inc.",
            "description": """Business Systems Analyst - Revenue Operations

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
        },
        
        "data_scientist": {
            "title": "Senior Data Scientist - Machine Learning",
            "company": "DataCorp Analytics",
            "description": """Senior Data Scientist - Machine Learning

We are looking for a Senior Data Scientist to join our growing analytics team. You will be responsible for developing machine learning models and driving data-driven insights across the organization.

Requirements:
- 3+ years of experience in data science or machine learning
- Strong proficiency in Python (pandas, numpy, scikit-learn, tensorflow/pytorch)
- Experience with SQL and database systems
- Knowledge of statistical analysis and experimental design
- Experience with big data technologies (Spark, Hadoop)
- Understanding of machine learning algorithms and model development
- Experience with data visualization tools (Tableau, Power BI, matplotlib)
- Knowledge of cloud platforms (AWS, Azure, GCP)

Preferred Qualifications:
- PhD in Computer Science, Statistics, or related field
- Experience with deep learning and neural networks
- Experience with MLOps and model deployment
- Knowledge of natural language processing
- Experience with A/B testing and causal inference

Responsibilities:
- Develop and deploy machine learning models for business applications
- Analyze large datasets to identify patterns and insights
- Design and conduct experiments to test hypotheses
- Collaborate with engineering teams to integrate ML models
- Communicate findings to stakeholders through visualizations and reports
- Mentor junior data scientists and contribute to team knowledge sharing
- Stay current with latest developments in ML and data science"""
        },
        
        "software_engineer": {
            "title": "Full Stack Software Engineer",
            "company": "InnovateTech Solutions",
            "description": """Full Stack Software Engineer

We are seeking a Full Stack Software Engineer to join our development team. You will be responsible for building scalable web applications and contributing to our product development efforts.

Requirements:
- 2+ years of experience in full stack development
- Strong proficiency in JavaScript/TypeScript and modern frameworks (React, Angular, Vue)
- Experience with backend development (Node.js, Python, Java, or C#)
- Knowledge of database design and SQL/NoSQL databases
- Experience with RESTful APIs and microservices architecture
- Understanding of version control systems (Git)
- Knowledge of cloud platforms (AWS, Azure, GCP)
- Experience with Agile development methodologies

Preferred Qualifications:
- Experience with containerization (Docker, Kubernetes)
- Knowledge of CI/CD pipelines and DevOps practices
- Experience with testing frameworks and TDD
- Understanding of security best practices
- Experience with performance optimization and scalability

Responsibilities:
- Design and implement user-facing features and backend services
- Write clean, maintainable, and efficient code
- Collaborate with product managers and designers
- Participate in code reviews and technical discussions
- Debug and resolve technical issues
- Contribute to technical architecture decisions
- Mentor junior developers and share knowledge"""
        },
        
        "devops_engineer": {
            "title": "DevOps Engineer - Cloud Infrastructure",
            "company": "CloudScale Systems",
            "description": """DevOps Engineer - Cloud Infrastructure

We are looking for a DevOps Engineer to help us build and maintain our cloud infrastructure and CI/CD pipelines. You will be responsible for automating our deployment processes and ensuring system reliability.

Requirements:
- 3+ years of experience in DevOps or infrastructure engineering
- Strong experience with cloud platforms (AWS, Azure, or GCP)
- Experience with containerization (Docker, Kubernetes)
- Knowledge of infrastructure as code (Terraform, CloudFormation)
- Experience with CI/CD tools (Jenkins, GitLab CI, GitHub Actions)
- Understanding of monitoring and logging tools
- Experience with Linux systems administration
- Knowledge of networking and security principles

Preferred Qualifications:
- Experience with serverless architectures
- Knowledge of microservices and distributed systems
- Experience with monitoring tools (Prometheus, Grafana, ELK stack)
- Understanding of security compliance and best practices
- Experience with database administration

Responsibilities:
- Design and implement cloud infrastructure solutions
- Automate deployment and configuration processes
- Monitor system performance and troubleshoot issues
- Implement security best practices and compliance measures
- Collaborate with development teams to optimize deployment workflows
- Maintain and improve CI/CD pipelines
- Document infrastructure and operational procedures
- Participate in on-call rotations for production support"""
        },
        
        "product_manager": {
            "title": "Senior Product Manager - SaaS Platform",
            "company": "ProductFlow Inc.",
            "description": """Senior Product Manager - SaaS Platform

We are seeking a Senior Product Manager to lead product strategy and development for our SaaS platform. You will be responsible for driving product vision and ensuring successful delivery of features.

Requirements:
- 4+ years of experience in product management
- Experience with SaaS or B2B software products
- Strong analytical and problem-solving skills
- Experience with user research and customer interviews
- Knowledge of product analytics and data-driven decision making
- Experience with Agile development methodologies
- Understanding of technical concepts and ability to work with engineering teams
- Strong communication and stakeholder management skills

Preferred Qualifications:
- MBA or advanced degree in business or technology
- Experience with product-led growth strategies
- Knowledge of UX/UI design principles
- Experience with A/B testing and experimentation
- Understanding of pricing and business models

Responsibilities:
- Define product strategy and roadmap
- Conduct market research and competitive analysis
- Gather and prioritize product requirements
- Work closely with engineering teams to deliver features
- Analyze product metrics and user feedback
- Collaborate with marketing and sales teams
- Present product plans to stakeholders and executives
- Mentor junior product managers"""
        },
        
        "data_analyst": {
            "title": "Business Intelligence Analyst",
            "company": "InsightCorp",
            "description": """Business Intelligence Analyst

We are looking for a Business Intelligence Analyst to help us transform data into actionable insights. You will be responsible for creating reports, dashboards, and analytical solutions.

Requirements:
- 2+ years of experience in business intelligence or data analysis
- Strong proficiency in SQL and database systems
- Experience with data visualization tools (Tableau, Power BI, Looker)
- Knowledge of Excel and data manipulation
- Understanding of business metrics and KPIs
- Experience with data modeling and ETL processes
- Strong analytical and problem-solving skills
- Ability to communicate insights to non-technical stakeholders

Preferred Qualifications:
- Experience with Python or R for data analysis
- Knowledge of statistical analysis and hypothesis testing
- Experience with cloud data warehouses (Snowflake, BigQuery, Redshift)
- Understanding of data governance and quality
- Experience with predictive analytics

Responsibilities:
- Create and maintain business intelligence dashboards
- Analyze data to identify trends and insights
- Develop automated reporting solutions
- Collaborate with business stakeholders to understand requirements
- Ensure data accuracy and quality
- Present findings and recommendations to leadership
- Support data-driven decision making across the organization
- Train users on BI tools and reports"""
        },
        
        "salesforce_administrator": {
            "title": "Salesforce Administrator - CRM Specialist",
            "company": "SalesTech Solutions",
            "description": """Salesforce Administrator - CRM Specialist

We are seeking a Salesforce Administrator to manage and optimize our CRM system. You will be responsible for system configuration, user management, and process automation.

Requirements:
- 2+ years of experience as a Salesforce Administrator
- Salesforce Administrator certification
- Experience with Salesforce configuration and customization
- Knowledge of Salesforce security and user management
- Experience with workflow automation and process builder
- Understanding of data management and data quality
- Experience with reporting and dashboards
- Knowledge of Salesforce best practices

Preferred Qualifications:
- Experience with Salesforce CPQ or Sales Cloud
- Knowledge of Apex and Visualforce development
- Experience with Salesforce integrations and APIs
- Understanding of business process optimization
- Experience with change management and user training

Responsibilities:
- Configure and customize Salesforce to meet business needs
- Manage user access and security settings
- Create and maintain workflows and process automation
- Develop reports and dashboards for business users
- Ensure data quality and integrity
- Provide user training and support
- Collaborate with business stakeholders on system improvements
- Stay current with Salesforce releases and best practices"""
        },
        
        "cloud_architect": {
            "title": "Cloud Solutions Architect",
            "company": "CloudFirst Technologies",
            "description": """Cloud Solutions Architect

We are looking for a Cloud Solutions Architect to design and implement cloud-based solutions for our clients. You will be responsible for creating scalable and secure cloud architectures.

Requirements:
- 5+ years of experience in cloud architecture or infrastructure design
- Strong experience with major cloud platforms (AWS, Azure, GCP)
- Experience with containerization and orchestration (Docker, Kubernetes)
- Knowledge of microservices and distributed systems
- Understanding of security and compliance requirements
- Experience with infrastructure as code and automation
- Knowledge of networking and storage solutions
- Strong problem-solving and communication skills

Preferred Qualifications:
- Cloud platform certifications (AWS Solutions Architect, Azure Solutions Architect)
- Experience with serverless architectures
- Knowledge of DevOps and CI/CD practices
- Understanding of cost optimization strategies
- Experience with multi-cloud environments

Responsibilities:
- Design cloud-native solutions for client requirements
- Create technical architecture documents and diagrams
- Lead implementation of cloud solutions
- Ensure security and compliance requirements are met
- Optimize cloud costs and performance
- Mentor development teams on cloud best practices
- Stay current with cloud technologies and trends
- Collaborate with sales teams on solution proposals"""
        }
    }
    
    # Check if the requested job key exists
    if job_key not in job_descriptions:
        return jsonify({'error': 'Job not found', 'available_jobs': list(job_descriptions.keys())}), 404
    
    selected_job = job_descriptions[job_key]
    
    return jsonify({
        'success': True,
        'job_title': selected_job['title'],
        'company': selected_job['company'],
        'job_description': selected_job['description']
    })

@app.route('/detailed-form')
def detailed_form():
    """Display the detailed resume builder form"""
    return render_template('detailed_form.html')

@app.route('/detailed-form', methods=['POST'])
def detailed_form_submit():
    """Handle detailed form submission and convert to JSON structure"""
    try:
        # Extract form data
        form_data = request.form
        
        # Build the JSON structure matching my_experience.json format
        resume_data = {
            "summary": form_data.get('summary', ''),
            "contact": {
                "name": form_data.get('name', ''),
                "email": form_data.get('email', ''),
                "phone": form_data.get('phone', ''),
                "location": form_data.get('location', ''),
                "linkedin": form_data.get('linkedin', ''),
                "github": form_data.get('github', '')
            }
        }
        
        # Process experience data
        experience_data = []
        experience_index = 0
        while f'experience[{experience_index}][title]' in form_data:
            if form_data.get(f'experience[{experience_index}][title]'):
                experience_data.append({
                    "title": form_data.get(f'experience[{experience_index}][title]'),
                    "company": form_data.get(f'experience[{experience_index}][company]'),
                    "duration": form_data.get(f'experience[{experience_index}][duration]'),
                    "description": form_data.get(f'experience[{experience_index}][description]')
                })
            experience_index += 1
        
        resume_data["experience"] = experience_data
        
        # Process skills data
        skills_text = form_data.get('skills', '')
        skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
        resume_data["skills"] = skills_list
        
        # Process education data
        education_data = []
        education_index = 0
        while f'education[{education_index}][degree]' in form_data:
            if form_data.get(f'education[{education_index}][degree]'):
                education_item = {
                    "degree": form_data.get(f'education[{education_index}][degree]'),
                    "institution": form_data.get(f'education[{education_index}][institution]'),
                    "year": form_data.get(f'education[{education_index}][year]', ''),
                    "gpa": form_data.get(f'education[{education_index}][gpa]', '')
                }
                
                # Add field of study if provided
                field = form_data.get(f'education[{education_index}][field]', '')
                if field:
                    education_item["field"] = field
                
                education_data.append(education_item)
            education_index += 1
        
        resume_data["education"] = education_data
        
        # Process projects data
        projects_data = []
        project_index = 0
        while f'projects[{project_index}][name]' in form_data:
            if form_data.get(f'projects[{project_index}][name]'):
                project_item = {
                    "name": form_data.get(f'projects[{project_index}][name]'),
                    "description": form_data.get(f'projects[{project_index}][description]')
                }
                
                # Add optional fields
                technologies = form_data.get(f'projects[{project_index}][technologies]', '')
                if technologies:
                    project_item["technologies"] = [tech.strip() for tech in technologies.split(',') if tech.strip()]
                
                github = form_data.get(f'projects[{project_index}][github]', '')
                if github:
                    project_item["github"] = github
                
                live_demo = form_data.get(f'projects[{project_index}][live_demo]', '')
                if live_demo:
                    project_item["live_demo"] = live_demo
                
                projects_data.append(project_item)
            project_index += 1
        
        resume_data["projects"] = projects_data
        
        # Process certifications data
        certifications_data = []
        cert_index = 0
        while f'certifications[{cert_index}][name]' in form_data:
            if form_data.get(f'certifications[{cert_index}][name]'):
                cert_item = form_data.get(f'certifications[{cert_index}][name]')
                
                # Add year and issuer if provided
                year = form_data.get(f'certifications[{cert_index}][year]', '')
                issuer = form_data.get(f'certifications[{cert_index}][issuer]', '')
                
                if year or issuer:
                    cert_item = f"{cert_item}"
                    if year:
                        cert_item += f" ({year})"
                    if issuer:
                        cert_item += f" - {issuer}"
                
                certifications_data.append(cert_item)
            cert_index += 1
        
        resume_data["certifications"] = certifications_data
        
        # Process languages data
        languages_text = form_data.get('languages', '')
        if languages_text:
            languages_list = [lang.strip() for lang in languages_text.split(',') if lang.strip()]
            resume_data["languages"] = languages_list
        
        # Store in session for the next step
        session['resume_data'] = resume_data
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Resume data processed successfully',
            'redirect_url': '/form'  # Redirect to the job targeting form
        })
        
    except Exception as e:
        app.logger.error(f"Error processing detailed form: {e}")
        return jsonify({
            'success': False,
            'message': f'An error occurred while processing your form: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting ResuMatch on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌐 Access at: http://localhost:{port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port) 