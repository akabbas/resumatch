#!/usr/bin/env python3
"""
Simplified Resume Generator for Heroku
Basic version without heavy ML dependencies
"""

import os
import json
import re
import uuid
from typing import Dict, List, Union
from jinja2 import Template
import tempfile

class SimpleResumeGenerator:
    """Simplified resume generator for Heroku deployment"""
    
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
        
        # Generate HTML
        html_content = self.template.render(
            name=name,
            contact_info=contact_info,
            summary=experience_data.get('summary', ''),
            experience=experience_data.get('experience', []),
            skills=experience_data.get('skills', []),
            projects=experience_data.get('projects', []),
            certifications=experience_data.get('certifications', []),
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
