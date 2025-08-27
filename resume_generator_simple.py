#!/usr/bin/env python3
"""
Enhanced Resume Generator for Heroku
Creates intelligent, job-specific bullet points based on job requirements
"""

import os
import json
import re
import uuid
from typing import Dict, List, Union
from jinja2 import Template
import tempfile

class SimpleResumeGenerator:
    """Enhanced resume generator that creates job-specific bullet points"""
    
    def __init__(self, max_pages=2, include_projects=False):
        self.max_pages = max_pages
        self.include_projects = include_projects
        
        # Simple HTML template
        self.template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ name }} - Resume</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .name { font-size: 28px; font-weight: bold; margin-bottom: 10px; }
        .contact { font-size: 14px; color: #666; }
        .section { margin-bottom: 25px; }
        .section-title { font-size: 18px; font-weight: bold; border-bottom: 1px solid #ccc; margin-bottom: 15px; padding-bottom: 5px; }
        .job { margin-bottom: 20px; }
        .job-title { font-weight: bold; font-size: 16px; }
        .job-company { font-style: italic; color: #666; }
        .job-duration { color: #666; font-size: 14px; }
        .skills { display: flex; flex-wrap: wrap; gap: 10px; }
        .skill { background: #f0f0f0; padding: 5px 10px; border-radius: 15px; font-size: 14px; }
        .bullet { margin-bottom: 8px; padding-left: 20px; position: relative; }
        .bullet:before { content: "•"; position: absolute; left: 0; }
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{{ name }}</div>
        <div class="contact">{{ contact_info }}</div>
    </div>
    
    <div class="section">
        <div class="section-title">Professional Summary</div>
        <p>{{ summary }}</p>
    </div>
    
    <div class="section">
        <div class="section-title">Professional Experience</div>
        {% for job in experience %}
        <div class="job">
            <div class="job-title">{{ job.title }}</div>
            <div class="job-company">{{ job.company }}</div>
            <div class="job-duration">{{ job.duration }}</div>
            {% if job.description %}
                {% if job.description is string %}
                    <p>{{ job.description }}</p>
                {% else %}
                    {% for bullet in job.description %}
                        <div class="bullet">{{ bullet }}</div>
                    {% endfor %}
                {% endif %}
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <div class="section-title">Skills</div>
        <div class="skills">
            {% for skill in skills %}
                <span class="skill">{{ skill }}</span>
            {% endfor %}
        </div>
    </div>
    
    {% if certifications %}
    <div class="section">
        <div class="section-title">Certifications</div>
        {% for cert in certifications %}
            <div class="bullet">{{ cert }}</div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if projects and include_projects %}
    <div class="section">
        <div class="section-title">Projects</div>
        {% for project in projects %}
        <div class="job">
            <div class="job-title">{{ project.name }}</div>
            {% if project.description %}
                {% if project.description is string %}
                    <p>{{ project.description }}</p>
                {% else %}
                    {% for bullet in project.description %}
                        <div class="bullet">{{ bullet }}</div>
                    {% endfor %}
                {% endif %}
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
        """)
    
    def analyze_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Analyze job description to extract key requirements and skills"""
        requirements = {
            'technical_skills': [],
            'soft_skills': [],
            'tools_platforms': [],
            'methodologies': [],
            'industries': []
        }
        
        # Common technical skills to look for
        technical_patterns = {
            'programming': r'\b(python|java|javascript|typescript|sql|html|css|react|node\.js|angular|vue|django|flask|spring|\.net|php|ruby|go|rust|swift|kotlin)\b',
            'databases': r'\b(mysql|postgresql|mongodb|redis|oracle|sql server|dynamodb|elasticsearch|snowflake)\b',
            'cloud': r'\b(aws|azure|gcp|heroku|docker|kubernetes|terraform|jenkins|gitlab|github)\b',
            'analytics': r'\b(tableau|power bi|excel|r|matlab|spss|sas|looker|quicksight)\b'
        }
        
        # Common soft skills
        soft_patterns = {
            'leadership': r'\b(leadership|management|supervision|mentoring|coaching|team building)\b',
            'communication': r'\b(communication|presentation|documentation|reporting|stakeholder management)\b',
            'problem_solving': r'\b(problem solving|analytical|critical thinking|troubleshooting|optimization)\b',
            'project_management': r'\b(project management|agile|scrum|kanban|waterfall|planning)\b'
        }
        
        # Extract technical skills
        for category, pattern in technical_patterns.items():
            matches = re.findall(pattern, job_description.lower())
            requirements['technical_skills'].extend([match.title() for match in matches])
        
        # Extract soft skills
        for category, pattern in soft_patterns.items():
            matches = re.findall(pattern, job_description.lower())
            requirements['soft_skills'].extend([match.title() for match in matches])
        
        # Extract tools and platforms
        tools_pattern = r'\b(salesforce|oracle|sap|microsoft|google|adobe|slack|zoom|teams|jira|confluence|notion)\b'
        tools_matches = re.findall(tools_pattern, job_description.lower())
        requirements['tools_platforms'].extend([match.title() for match in tools_matches])
        
        # Extract methodologies
        methodology_pattern = r'\b(agile|scrum|kanban|waterfall|lean|six sigma|devops|ci/cd|tdd|bdd)\b'
        methodology_matches = re.findall(methodology_pattern, job_description.lower())
        requirements['methodologies'].extend([match.title() for match in methodology_matches])
        
        # Remove duplicates and clean up
        for key in requirements:
            requirements[key] = list(set(requirements[key]))
        
        return requirements
    
    def generate_job_specific_bullets(self, experience: Dict, job_requirements: Dict, original_description: str) -> List[str]:
        """Generate multiple job-specific bullet points for an experience"""
        bullets = []
        
        # Start with the original description as a base
        if original_description:
            bullets.append(original_description)
        
        # Ensure job_requirements has the expected structure
        if not isinstance(job_requirements, dict):
            print(f"⚠️ Warning: job_requirements is not a dict: {type(job_requirements)}")
            job_requirements = {
                'technical_skills': [],
                'soft_skills': [],
                'tools_platforms': [],
                'methodologies': [],
                'industries': []
            }
        
        # Generate additional relevant bullets based on job requirements
        title = experience.get('title', '').lower()
        company = experience.get('company', '')
        
        # Technical skills bullets
        if job_requirements.get('technical_skills') and isinstance(job_requirements['technical_skills'], list):
            for skill in job_requirements['technical_skills'][:3]:  # Top 3 skills
                if skill.lower() in title or any(skill.lower() in original_description.lower()):
                    bullets.append(f"Leveraged {skill} to develop scalable solutions and improve system performance")
        
        # Tools and platforms bullets
        if job_requirements.get('tools_platforms') and isinstance(job_requirements['tools_platforms'], list):
            for tool in job_requirements['tools_platforms'][:2]:  # Top 2 tools
                bullets.append(f"Utilized {tool} to streamline workflows and enhance team collaboration")
        
        # Methodologies bullets
        if job_requirements.get('methodologies') and isinstance(job_requirements['methodologies'], list):
            for method in job_requirements['methodologies'][:2]:  # Top 2 methodologies
                bullets.append(f"Applied {method.title()} methodologies to deliver projects on time and within scope")
        
        # Soft skills bullets
        if job_requirements.get('soft_skills') and isinstance(job_requirements['soft_skills'], list):
            for skill in job_requirements['soft_skills'][:2]:  # Top 2 soft skills
                if 'leadership' in skill.lower():
                    bullets.append("Led cross-functional teams and mentored junior team members")
                elif 'communication' in skill.lower():
                    bullets.append("Presented technical solutions to stakeholders and executive leadership")
                elif 'problem' in skill.lower():
                    bullets.append("Identified and resolved complex technical challenges through systematic analysis")
        
        # Quantified achievements (generic but effective)
        if len(bullets) < 4:  # Ensure we have enough bullets
            bullets.extend([
                "Improved process efficiency by implementing automated workflows and reducing manual tasks",
                "Collaborated with cross-functional teams to deliver high-quality solutions on schedule",
                "Maintained high standards for code quality and system reliability"
            ])
        
        # Ensure we don't have too many bullets (keep it to 4-6)
        return bullets[:6]
    
    def enhance_experience_data(self, experience_data: Dict, job_description: str) -> Dict:
        """Enhance experience data with job-specific bullet points"""
        print(f"🔍 Enhancing experience data with job description: {job_description[:100]}...")
        
        # Analyze job requirements
        job_requirements = self.analyze_job_requirements(job_description)
        print(f"📋 Extracted job requirements: {job_requirements}")
        
        # Enhance each experience entry
        enhanced_experience = []
        for experience in experience_data.get('experience', []):
            enhanced_exp = experience.copy()
            
            # Get original description
            original_description = ""
            if isinstance(experience.get('description'), list) and experience['description']:
                original_description = experience['description'][0]
            elif isinstance(experience.get('description'), str):
                original_description = experience['description']
            
            print(f"   Processing experience: {experience.get('title')} at {experience.get('company')}")
            print(f"   Original description: {original_description[:100]}...")
            
            # Generate enhanced bullet points
            enhanced_bullets = self.generate_job_specific_bullets(
                experience, job_requirements, original_description
            )
            
            print(f"   Generated {len(enhanced_bullets)} bullet points")
            
            # Update the experience with enhanced bullets
            enhanced_exp['description'] = enhanced_bullets
            enhanced_experience.append(enhanced_exp)
        
        # Update the experience data
        enhanced_data = experience_data.copy()
        enhanced_data['experience'] = enhanced_experience
        
        return enhanced_data
    
    def generate_resume(self, job_description: str, experience_data: Union[str, Dict], 
                       output_path: str, name: str = "Your Name", 
                       contact_info: str = "email@example.com | phone | location") -> str:
        """Generate a simple HTML resume"""
        
        # Parse experience data
        if isinstance(experience_data, str):
            try:
                experience_data = json.loads(experience_data)
            except json.JSONDecodeError:
                # Simple text format
                experience_data = {
                    "summary": experience_data[:200] + "..." if len(experience_data) > 200 else experience_data,
                    "experience": [],
                    "skills": []
                }
        
        # Ensure required fields exist
        if not isinstance(experience_data, dict):
            experience_data = {
                "summary": "Professional summary",
                "experience": [],
                "skills": []
            }
        
        # Enhance experience data with job-specific bullets
        enhanced_experience_data = self.enhance_experience_data(experience_data, job_description)
        
        # Generate HTML
        html_content = self.template.render(
            name=name,
            contact_info=contact_info,
            summary=enhanced_experience_data.get('summary', ''),
            experience=enhanced_experience_data.get('experience', []),
            skills=enhanced_experience_data.get('skills', []),
            projects=enhanced_experience_data.get('projects', []),
            certifications=enhanced_experience_data.get('certifications', []),
            include_projects=self.include_projects
        )
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

def generate_simple_resume(job_description: str, experience_data: Union[str, Dict], 
                          output_path: str, name: str = "Your Name", 
                          contact_info: str = "email@example.com | phone | location") -> str:
    """Convenience function for simple resume generation"""
    generator = SimpleResumeGenerator()
    return generator.generate_resume(job_description, experience_data, output_path, name, contact_info)
