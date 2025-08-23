#!/usr/bin/env python3
"""
Harvard-Style PDF Resume Generator
Implements professional resume formatting following Harvard best practices:
- Professional typography and spacing
- Clear visual hierarchy
- ATS-optimized formatting
- Achievement-oriented bullet points
- Smart page management
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from typing import Dict, List, Union, Optional
import re

class HarvardStylePDFGenerator:
    """Generate Harvard-style professional PDF resumes"""
    
    def __init__(self, page_size='letter', max_pages=2):
        self.page_size = letter if page_size == 'letter' else A4
        self.max_pages = max_pages
        self.styles = getSampleStyleSheet()
        self._setup_harvard_styles()
    
    def _setup_harvard_styles(self):
        """Setup Harvard-style professional formatting"""
        
        # Name - Large, centered, professional
        self.styles.add(ParagraphStyle(
            name='HarvardName',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=8,
            spaceBefore=0,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=28
        ))
        
        # Contact info - Centered, professional
        self.styles.add(ParagraphStyle(
            name='HarvardContact',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=0,
            textColor=colors.black,
            fontName='Helvetica',
            leading=12
        ))
        
        # Section headers - Bold, underlined, professional
        self.styles.add(ParagraphStyle(
            name='HarvardSectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=16,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leftIndent=0,
            rightIndent=0,
            leading=14,
            borderWidth=0,
            borderColor=colors.black,
            borderPadding=0
        ))
        
        # Job title - Bold, professional
        self.styles.add(ParagraphStyle(
            name='HarvardJobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=2,
            spaceBefore=0,
            leading=13,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica-Bold',
            textColor=colors.black
        ))
        
        # Company and duration - Italic, professional
        self.styles.add(ParagraphStyle(
            name='HarvardCompany',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=0,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica-Oblique',
            textColor=colors.black
        ))
        
        # Bullet points - Professional, properly indented
        self.styles.add(ParagraphStyle(
            name='HarvardBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            spaceBefore=0,
            leading=12,
            leftIndent=0.25*inch,
            rightIndent=0,
            fontName='Helvetica',
            textColor=colors.black,
            bulletIndent=0.1*inch
        ))
        
        # Summary text - Professional body text
        self.styles.add(ParagraphStyle(
            name='HarvardSummary',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            spaceBefore=0,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica',
            textColor=colors.black,
            alignment=TA_JUSTIFY
        ))
        
        # Skills - Professional list format
        self.styles.add(ParagraphStyle(
            name='HarvardSkill',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            spaceBefore=0,
            leading=12,
            leftIndent=0.25*inch,
            rightIndent=0,
            fontName='Helvetica',
            textColor=colors.black
        ))
        
        # Project name - Bold, professional
        self.styles.add(ParagraphStyle(
            name='HarvardProjectName',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            spaceBefore=0,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica-Bold',
            textColor=colors.black
        ))
        
        # Certification - Professional format
        self.styles.add(ParagraphStyle(
            name='HarvardCertification',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            spaceBefore=0,
            leading=12,
            leftIndent=0.25*inch,
            rightIndent=0,
            fontName='Helvetica',
            textColor=colors.black
        ))
        
        # Education - Professional format
        self.styles.add(ParagraphStyle(
            name='HarvardEducation',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            spaceBefore=0,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica',
            textColor=colors.black
        ))
    
    def _ensure_achievement_verbs(self, text: str) -> str:
        """Ensure bullet points start with strong action verbs"""
        if not text.strip():
            return text
        
        # Strong action verbs for professional resumes
        action_verbs = [
            'Led', 'Developed', 'Engineered', 'Implemented', 'Designed', 'Built',
            'Created', 'Managed', 'Optimized', 'Increased', 'Reduced', 'Improved',
            'Automated', 'Streamlined', 'Enhanced', 'Delivered', 'Coordinated',
            'Analyzed', 'Researched', 'Established', 'Maintained', 'Configured',
            'Deployed', 'Integrated', 'Troubleshot', 'Mentored', 'Collaborated'
        ]
        
        # Check if text already starts with a strong verb
        text_lower = text.lower().strip()
        if any(text_lower.startswith(verb.lower()) for verb in action_verbs):
            return text
        
        # If not, try to find a good starting point
        sentences = text.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if first_sentence:
                # Try to find a verb and make it stronger
                words = first_sentence.split()
                if len(words) > 2:
                    # Look for common weak verbs to replace
                    weak_verbs = ['did', 'was', 'were', 'had', 'worked', 'helped', 'used']
                    for i, word in enumerate(words):
                        if word.lower() in weak_verbs and i < len(words) - 1:
                            # Replace with a stronger verb
                            words[i] = action_verbs[0]  # Use first strong verb
                            return ' '.join(words) + '. ' + '. '.join(sentences[1:])
        
        return text
    
    def _format_contact_info(self, contact: Dict) -> str:
        """Format contact information professionally"""
        contact_lines = []
        
        if contact.get('email'):
            contact_lines.append(contact['email'])
        if contact.get('phone'):
            contact_lines.append(contact['phone'])
        if contact.get('location'):
            contact_lines.append(contact['location'])
        if contact.get('linkedin'):
            contact_lines.append(f"LinkedIn: {contact['linkedin']}")
        if contact.get('github'):
            contact_lines.append(f"GitHub: {contact['github']}")
        
        return ' | '.join(contact_lines)
    
    def generate_harvard_pdf(self, experience_data: Union[str, Dict], output_path: str, 
                            name: str = "Your Name", contact_info: str = "email@example.com | phone | location") -> str:
        """Generate Harvard-style professional PDF resume"""
        
        # Parse experience data
        if isinstance(experience_data, str):
            try:
                import json
                experience_data = json.loads(experience_data)
            except:
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
        
        # Create PDF document with Harvard-style margins
        doc = SimpleDocTemplate(output_path, pagesize=self.page_size,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Build story (content)
        story = []
        
        # Header section - Harvard style
        story.append(Paragraph(name, self.styles['HarvardName']))
        
        # Format contact info
        if isinstance(experience_data, dict) and 'contact' in experience_data:
            contact_formatted = self._format_contact_info(experience_data['contact'])
        else:
            contact_formatted = contact_info
        
        story.append(Paragraph(contact_formatted, self.styles['HarvardContact']))
        
        # Professional Summary - Harvard style
        if experience_data.get('summary') and experience_data['summary'].strip():
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['HarvardSectionHeader']))
            story.append(Paragraph(experience_data['summary'], self.styles['HarvardSummary']))
        
        # Professional Experience - Harvard style
        if experience_data.get('experience'):
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['HarvardSectionHeader']))
            
            for i, job in enumerate(experience_data['experience']):
                # Keep each job together to avoid page breaks
                job_content = []
                
                # Job title
                job_title = job.get('title', '')
                if job_title:
                    job_content.append(Paragraph(job_title, self.styles['HarvardJobTitle']))
                
                # Company and duration
                company = job.get('company', '')
                duration = job.get('duration', '')
                if company or duration:
                    company_line = []
                    if company:
                        company_line.append(company)
                    if duration:
                        company_line.append(duration)
                    job_content.append(Paragraph(' • '.join(company_line), self.styles['HarvardCompany']))
                
                # Job description with achievement-oriented bullets
                description = job.get('description', '')
                if description:
                    if isinstance(description, list):
                        for bullet in description:
                            if bullet.strip():
                                # Ensure bullet points start with strong action verbs
                                enhanced_bullet = self._ensure_achievement_verbs(bullet)
                                job_content.append(Paragraph(f"• {enhanced_bullet}", self.styles['HarvardBullet']))
                    else:
                        # Single description - split into sentences for better formatting
                        sentences = description.split('.')
                        for sentence in sentences:
                            if sentence.strip():
                                enhanced_sentence = self._ensure_achievement_verbs(sentence.strip())
                                job_content.append(Paragraph(f"• {enhanced_sentence}.", self.styles['HarvardBullet']))
                
                # Add spacing between jobs
                if i < len(experience_data['experience']) - 1:
                    job_content.append(Spacer(1, 0.1*inch))
                
                # Keep job content together
                story.append(KeepTogether(job_content))
        
        # Technical Skills - Harvard style
        if experience_data.get('skills'):
            story.append(Paragraph("TECHNICAL SKILLS & EXPERTISE", self.styles['HarvardSectionHeader']))
            
            skills = experience_data['skills']
            if skills:
                # Format skills as a professional list
                for skill in skills:
                    if isinstance(skill, dict):
                        skill_name = skill.get('name', str(skill))
                    else:
                        skill_name = str(skill)
                    
                    if skill_name.strip():
                        story.append(Paragraph(f"• {skill_name}", self.styles['HarvardSkill']))
        
        # Projects - Harvard style
        if experience_data.get('projects'):
            story.append(Paragraph("PROJECTS & ACHIEVEMENTS", self.styles['HarvardSectionHeader']))
            
            for i, project in enumerate(experience_data['projects']):
                project_content = []
                
                # Project name
                project_name = project.get('name', '')
                if project_name:
                    project_content.append(Paragraph(project_name, self.styles['HarvardProjectName']))
                
                # Project description
                project_desc = project.get('description', '')
                if project_desc:
                    if isinstance(project_desc, list):
                        for desc in project_desc:
                            if desc.strip():
                                enhanced_desc = self._ensure_achievement_verbs(desc)
                                project_content.append(Paragraph(f"• {enhanced_desc}", self.styles['HarvardBullet']))
                    else:
                        enhanced_desc = self._ensure_achievement_verbs(project_desc)
                        project_content.append(Paragraph(f"• {enhanced_desc}", self.styles['HarvardBullet']))
                
                # Project technologies
                tech_list = project.get('technologies', [])
                if tech_list:
                    tech_text = ', '.join(tech_list)
                    project_content.append(Paragraph(f"<i>Technologies: {tech_text}</i>", self.styles['HarvardBullet']))
                
                # Add spacing between projects
                if i < len(experience_data['projects']) - 1:
                    project_content.append(Spacer(1, 0.08*inch))
                
                # Keep project content together
                story.append(KeepTogether(project_content))
        
        # Certifications - Harvard style
        if experience_data.get('certifications'):
            story.append(Paragraph("CERTIFICATIONS & TRAINING", self.styles['HarvardSectionHeader']))
            
            for cert in experience_data['certifications']:
                if cert.strip():
                    story.append(Paragraph(f"• {cert}", self.styles['HarvardCertification']))
        
        # Education - Harvard style
        if experience_data.get('education'):
            story.append(Paragraph("EDUCATION", self.styles['HarvardSectionHeader']))
            
            for edu in experience_data['education']:
                education_content = []
                
                # Degree
                degree = edu.get('degree', '')
                if degree:
                    education_content.append(Paragraph(degree, self.styles['HarvardEducation']))
                
                # Institution
                institution = edu.get('institution', '')
                if institution:
                    education_content.append(Paragraph(institution, self.styles['HarvardEducation']))
                
                # Year and GPA
                year = edu.get('year', '')
                gpa = edu.get('gpa', '')
                if year or gpa:
                    details = []
                    if year:
                        details.append(year)
                    if gpa:
                        details.append(gpa)
                    education_content.append(Paragraph(' • '.join(details), self.styles['HarvardEducation']))
                
                # Keep education content together
                story.append(KeepTogether(education_content))
        
        # Build PDF
        doc.build(story)
        
        return output_path

def generate_harvard_pdf_resume(experience_data: Union[str, Dict], output_path: str, 
                               name: str = "Your Name", contact_info: str = "email@example.com | phone | location") -> str:
    """Convenience function for Harvard-style PDF resume generation"""
    generator = HarvardStylePDFGenerator()
    return generator.generate_harvard_pdf(experience_data, output_path, name, contact_info)

if __name__ == "__main__":
    # Test the Harvard-style PDF generator
    test_data = {
        "summary": "Experienced software engineer with expertise in Python, web development, and cloud technologies.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "duration": "2020-2023",
                "description": [
                    "Led development of scalable web applications using Python and React",
                    "Engineered microservices architecture improving system performance by 40%",
                    "Mentored junior developers and established coding standards"
                ]
            }
        ],
        "skills": ["Python", "React", "AWS", "Docker", "Kubernetes"],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": ["Built full-stack e-commerce solution", "Implemented payment processing"],
                "technologies": ["Python", "React", "PostgreSQL"]
            }
        ],
        "certifications": ["AWS Certified Developer", "Python Professional"],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "year": "2019",
                "gpa": "3.8/4.0"
            }
        ]
    }
    
    output_file = "test_harvard_resume.pdf"
    result = generate_harvard_pdf_resume(test_data, output_file, "John Doe", "john@example.com | 555-1234 | New York")
    print(f"✅ Harvard-style PDF generated: {result}")
