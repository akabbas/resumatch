#!/usr/bin/env python3
"""
Simplified Resume Generator for Ammr's Personal Use
Works without heavy NLP dependencies
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any

class SimpleResumeGenerator:
    def __init__(self):
        self.html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resume - {name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .name {{ font-size: 28px; font-weight: bold; margin-bottom: 5px; }}
        .contact {{ font-size: 14px; color: #666; margin-bottom: 20px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 18px; font-weight: bold; border-bottom: 2px solid #333; margin-bottom: 15px; }}
        .job {{ margin-bottom: 20px; }}
        .job-title {{ font-weight: bold; font-size: 16px; }}
        .job-company {{ font-weight: bold; color: #333; }}
        .job-duration {{ color: #666; font-style: italic; }}
        .job-description {{ margin-top: 10px; }}
        .skills {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .skill {{ background: #f0f0f0; padding: 5px 10px; border-radius: 15px; font-size: 12px; }}
        .project {{ margin-bottom: 15px; }}
        .project-name {{ font-weight: bold; }}
        .project-description {{ margin-top: 5px; }}
        .project-tech {{ color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{name}</div>
        <div class="contact">
            {email} • {phone} • {location}<br>
            {linkedin} • {github}
        </div>
    </div>

    <div class="section">
        <div class="section-title">PROFESSIONAL SUMMARY</div>
        <div>{summary}</div>
    </div>

    <div class="section">
        <div class="section-title">PROFESSIONAL EXPERIENCE</div>
        {experience_html}
    </div>

    <div class="section">
        <div class="section-title">TECHNICAL SKILLS</div>
        <div class="skills">
            {skills_html}
        </div>
    </div>

    <div class="section">
        <div class="section-title">PROJECTS</div>
        {projects_html}
    </div>

    <div class="section">
        <div class="section-title">CERTIFICATIONS</div>
        {certifications_html}
    </div>

    <div class="section">
        <div class="section-title">EDUCATION</div>
        {education_html}
    </div>
</body>
</html>
        """

    def extract_keywords(self, job_description: str) -> List[str]:
        """Simple keyword extraction without NLP"""
        # Common technical keywords
        tech_keywords = [
            'python', 'sql', 'javascript', 'react', 'node.js', 'aws', 'docker', 'kubernetes',
            'salesforce', 'oracle', 'crm', 'cpq', 'erp', 'api', 'rest', 'automation',
            'data', 'analysis', 'reporting', 'integration', 'workflow', 'agile', 'scrum',
            'git', 'azure', 'devops', 'cloud', 'database', 'etl', 'bi', 'dashboard'
        ]
        
        # Extract keywords from job description
        found_keywords = []
        job_lower = job_description.lower()
        
        for keyword in tech_keywords:
            if keyword in job_lower:
                found_keywords.append(keyword)
        
        return found_keywords

    def match_skills(self, job_keywords: List[str], user_skills: List[str]) -> List[str]:
        """Match user skills to job requirements"""
        matched_skills = []
        job_keywords_set = set(job_keywords)
        
        for skill in user_skills:
            skill_lower = skill.lower()
            # Check for exact matches or partial matches
            for keyword in job_keywords_set:
                if keyword in skill_lower or skill_lower in keyword:
                    matched_skills.append(skill)
                    break
        
        return matched_skills[:15]  # Limit to top 15 skills

    def generate_summary(self, job_description: str, experience_data: Dict) -> str:
        """Generate a tailored summary based on job description"""
        keywords = self.extract_keywords(job_description)
        
        # Base summary
        base_summary = experience_data.get('summary', '')
        
        # Add job-specific focus
        focus_areas = []
        if any(kw in job_description.lower() for kw in ['revops', 'revenue', 'sales']):
            focus_areas.append('revenue operations')
        if any(kw in job_description.lower() for kw in ['crm', 'salesforce']):
            focus_areas.append('CRM systems')
        if any(kw in job_description.lower() for kw in ['automation', 'python']):
            focus_areas.append('process automation')
        if any(kw in job_description.lower() for kw in ['data', 'analysis']):
            focus_areas.append('data analysis')
        
        if focus_areas:
            focus_text = f" with expertise in {', '.join(focus_areas)}"
            # Insert focus into summary
            if 'with' in base_summary:
                base_summary = base_summary.replace('with', focus_text + ' and')
            else:
                base_summary += focus_text
        
        return base_summary

    def generate_resume_html(self, experience_data: Dict, job_description: str = "") -> str:
        """Generate HTML resume"""
        
        # Generate tailored summary
        summary = self.generate_summary(job_description, experience_data)
        
        # Generate experience HTML
        experience_html = ""
        for job in experience_data.get('experience', []):
            experience_html += f"""
            <div class="job">
                <div class="job-title">{job['title']}</div>
                <div class="job-company">{job['company']} • <span class="job-duration">{job['duration']}</span></div>
                <div class="job-description">{job['description']}</div>
            </div>
            """
        
        # Generate skills HTML
        user_skills = experience_data.get('skills', [])
        if job_description:
            job_keywords = self.extract_keywords(job_description)
            matched_skills = self.match_skills(job_keywords, user_skills)
            skills_to_show = matched_skills if matched_skills else user_skills[:20]
        else:
            skills_to_show = user_skills[:20]
        
        skills_html = ""
        for skill in skills_to_show:
            skills_html += f'<span class="skill">{skill}</span>'
        
        # Generate projects HTML
        projects_html = ""
        for project in experience_data.get('projects', []):
            tech_list = ', '.join(project.get('technologies', []))
            projects_html += f"""
            <div class="project">
                <div class="project-name">{project['name']}</div>
                <div class="project-description">{project['description']}</div>
                <div class="project-tech">Technologies: {tech_list}</div>
            </div>
            """
        
        # Generate certifications HTML
        certifications_html = ""
        for cert in experience_data.get('certifications', []):
            certifications_html += f"<div>• {cert}</div>"
        
        # Generate education HTML
        education_html = ""
        for edu in experience_data.get('education', []):
            education_html += f"""
            <div>
                <strong>{edu['institution']}</strong><br>
                {edu['degree']} ({edu['year']}) • GPA: {edu['gpa']}
            </div>
            """
        
        # Get contact info
        contact = experience_data.get('contact', {})
        
        # Fill template
        html = self.html_template.format(
            name=contact.get('name', ''),
            email=contact.get('email', ''),
            phone=contact.get('phone', ''),
            location=contact.get('location', ''),
            linkedin=contact.get('linkedin', ''),
            github=contact.get('github', ''),
            summary=summary,
            experience_html=experience_html,
            skills_html=skills_html,
            projects_html=projects_html,
            certifications_html=certifications_html,
            education_html=education_html
        )
        
        return html

    def save_html(self, html: str, filename: str):
        """Save HTML to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Resume saved as: {filename}")

def main():
    """Main function for testing"""
    generator = SimpleResumeGenerator()
    
    # Load experience data
    try:
        with open('my_experience.json', 'r', encoding='utf-8') as f:
            experience_data = json.load(f)
    except FileNotFoundError:
        print("❌ my_experience.json not found. Please create it first.")
        return
    
    # Example job description
    job_description = """
    RevOps Developer position requiring experience with Salesforce CRM, 
    Oracle CPQ, Python automation, REST API integration, and workflow optimization.
    """
    
    # Generate resume
    html = generator.generate_resume_html(experience_data, job_description)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ammr_resume_{timestamp}.html"
    generator.save_html(html, filename)
    
    print(f"🎯 Resume generated with focus on: {generator.extract_keywords(job_description)}")

if __name__ == "__main__":
    main() 