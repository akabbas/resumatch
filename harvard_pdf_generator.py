#!/usr/bin/env python3
"""
Harvard-Style PDF Resume Generator with Strict Page Limit Enforcement
Implements professional resume formatting following Harvard best practices:
- Professional typography and spacing
- Clear visual hierarchy
- ATS-optimized formatting
- Achievement-oriented bullet points
- STRICT page limit enforcement with intelligent compression
"""

import os
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from typing import Dict, List, Union, Optional, Tuple
import re
import tempfile
from PyPDF2 import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HarvardStylePDFGenerator:
    """Generate Harvard-style professional PDF resumes with strict page limit enforcement"""
    
    def __init__(self, page_size='letter', max_pages=2):
        self.page_size = letter if page_size == 'letter' else A4
        self.max_pages = max_pages
        self.styles = getSampleStyleSheet()
        self._setup_harvard_styles()
        
        # Page limit enforcement settings
        self.min_font_size = 9  # Minimum readable font size
        self.min_margin = 0.5 * inch  # Minimum margin size
        self.max_compression_attempts = 5  # Maximum compression attempts
        
        # Initial styling values
        self.current_font_size = 10
        self.current_margin = 0.75 * inch
        self.current_line_spacing = 1.2
        
        logger.info(f"Initialized HarvardStylePDFGenerator with max_pages={max_pages}")
    
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
    
    def _update_styles_for_compression(self, font_size: float, margin: float, line_spacing: float):
        """Update all styles with new compression settings"""
        logger.info(f"Applying compression: font_size={font_size}, margin={margin}, line_spacing={line_spacing}")
        
        # Update style parameters
        style_updates = {
            'HarvardName': {'fontSize': max(18, font_size + 14), 'leading': max(22, (font_size + 14) * 1.2)},
            'HarvardContact': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(12, font_size * 1.2)},
            'HarvardSectionHeader': {'fontSize': max(10, font_size + 2), 'leading': max(12, (font_size + 2) * 1.2), 'spaceAfter': max(6, font_size * 0.6), 'spaceBefore': max(12, font_size * 1.2)},
            'HarvardJobTitle': {'fontSize': max(9, font_size + 1), 'leading': max(11, (font_size + 1) * 1.2), 'spaceAfter': max(1, font_size * 0.1)},
            'HarvardCompany': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(4, font_size * 0.4)},
            'HarvardBullet': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(2, font_size * 0.2), 'leftIndent': max(0.15*inch, margin * 0.2)},
            'HarvardSummary': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(6, font_size * 0.6)},
            'HarvardSkill': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(1, font_size * 0.1), 'leftIndent': max(0.15*inch, margin * 0.2)},
            'HarvardProjectName': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(1, font_size * 0.1)},
            'HarvardCertification': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(2, font_size * 0.2), 'leftIndent': max(0.15*inch, margin * 0.2)},
            'HarvardEducation': {'fontSize': font_size, 'leading': font_size * 1.2, 'spaceAfter': max(2, font_size * 0.2)}
        }
        
        for style_name, updates in style_updates.items():
            if style_name in self.styles:
                for attr, value in updates.items():
                    setattr(self.styles[style_name], attr, value)
    
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
    
    def _calculate_ats_relevance_score(self, item: Union[str, Dict], job_keywords: List[str]) -> float:
        """Calculate ATS relevance score for content prioritization"""
        if isinstance(item, str):
            text = item.lower()
        elif isinstance(item, dict):
            # Combine all text fields
            text = ' '.join([str(v) for v in item.values() if isinstance(v, str)]).lower()
        else:
            return 0.0
        
        # Count keyword matches
        keyword_matches = sum(1 for keyword in job_keywords if keyword.lower() in text)
        
        # Calculate relevance score (0.0 to 1.0)
        relevance_score = min(1.0, keyword_matches / max(1, len(job_keywords)))
        
        return relevance_score
    
    def _prune_content_by_relevance(self, experience_data: Dict, job_description: str, target_pages: int) -> Dict:
        """Prune content based on ATS relevance to fit page limit"""
        logger.info(f"Pruning content to fit {target_pages} pages")
        
        # Extract keywords from job description
        job_keywords = re.findall(r'\b\w+\b', job_description.lower())
        job_keywords = [kw for kw in job_keywords if len(kw) > 3]  # Filter short words
        
        # Create a copy to modify
        pruned_data = experience_data.copy()
        
        # Sort experience items by relevance
        if 'experience' in pruned_data and pruned_data['experience']:
            experience_with_scores = []
            for exp in pruned_data['experience']:
                score = self._calculate_ats_relevance_score(exp, job_keywords)
                experience_with_scores.append((exp, score))
            
            # Sort by relevance (highest first)
            experience_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only the most relevant items - more aggressive for single page
            if target_pages == 1:
                max_experience_items = 2  # Reduced from 3 to 2 for single page
                # For single page, also limit bullet points per job
                for exp, _ in experience_with_scores[:max_experience_items]:
                    if 'description' in exp and isinstance(exp['description'], list):
                        # Keep only top 2-3 bullet points for single page
                        exp['description'] = exp['description'][:2]
            else:
                max_experience_items = 5
            
            pruned_data['experience'] = [exp for exp, score in experience_with_scores[:max_experience_items]]
            
            # Add note about additional experience
            if len(experience_with_scores) > max_experience_items:
                pruned_data['experience'].append({
                    'title': 'Additional Experience',
                    'company': 'Various Companies',
                    'duration': 'Previous Roles',
                    'description': ['Additional professional experience available upon request.']
                })
            
            logger.info(f"Pruned experience from {len(experience_with_scores)} to {len(pruned_data['experience'])} items")
        
        # Prune skills - more aggressive for single page
        if 'skills' in pruned_data and pruned_data['skills']:
            skills_with_scores = []
            for skill in pruned_data['skills']:
                score = self._calculate_ats_relevance_score(skill, job_keywords)
                skills_with_scores.append((skill, score))
            
            # Sort by relevance and keep top skills
            skills_with_scores.sort(key=lambda x: x[1], reverse=True)
            if target_pages == 1:
                max_skills = 6  # Reduced from 8 to 6 for single page
            else:
                max_skills = 15
            pruned_data['skills'] = [skill for skill, score in skills_with_scores[:max_skills]]
            
            logger.info(f"Pruned skills from {len(skills_with_scores)} to {len(pruned_data['skills'])} items")
        
        # Prune projects - more aggressive for single page
        if 'projects' in pruned_data and pruned_data['projects']:
            projects_with_scores = []
            for project in pruned_data['projects']:
                score = self._calculate_ats_relevance_score(project, job_keywords)
                projects_with_scores.append((project, score))
            
            # Sort by relevance and keep top projects
            projects_with_scores.sort(key=lambda x: x[1], reverse=True)
            if target_pages == 1:
                max_projects = 1  # Reduced from 2 to 1 for single page
                # For single page, limit project descriptions
                for project, _ in projects_with_scores[:max_projects]:
                    if 'description' in project and isinstance(project['description'], list):
                        project['description'] = project['description'][:1]  # Keep only 1 bullet point
            else:
                max_projects = 4
            pruned_data['projects'] = [project for project, score in projects_with_scores[:max_projects]]
            
            logger.info(f"Pruned projects from {len(projects_with_scores)} to {len(pruned_data['projects'])} items")
        
        # For single page, also truncate summary
        if target_pages == 1 and 'summary' in pruned_data:
            summary = pruned_data['summary']
            if len(summary) > 150:  # Limit summary length for single page
                pruned_data['summary'] = summary[:150] + "..."
                logger.info("Truncated summary for single-page resume")
        
        return pruned_data
    
    def _aggressive_content_pruning(self, experience_data: Dict, job_description: str) -> Dict:
        """Apply extremely aggressive content pruning for single-page resumes"""
        logger.warning("Applying aggressive content pruning for single-page resume")
        
        # Create a copy to modify
        pruned_data = experience_data.copy()
        
        # Extract keywords from job description
        job_keywords = re.findall(r'\b\w+\b', job_description.lower())
        job_keywords = [kw for kw in job_keywords if len(kw) > 3]
        
        # Keep only 1 most relevant experience item
        if 'experience' in pruned_data and pruned_data['experience']:
            experience_with_scores = []
            for exp in pruned_data['experience']:
                score = self._calculate_ats_relevance_score(exp, job_keywords)
                experience_with_scores.append((exp, score))
            
            experience_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only the top 1 experience item with minimal bullets
            if experience_with_scores:
                top_exp = experience_with_scores[0][0].copy()
                if 'description' in top_exp and isinstance(top_exp['description'], list):
                    top_exp['description'] = top_exp['description'][:1]  # Keep only 1 bullet point
                pruned_data['experience'] = [top_exp]
                
                # Add note about additional experience
                pruned_data['experience'].append({
                    'title': 'Additional Experience',
                    'company': 'Various Companies',
                    'duration': 'Previous Roles',
                    'description': ['Additional professional experience available upon request.']
                })
            
            logger.info("Aggressively pruned experience to 1 item with minimal bullets")
        
        # Keep only top 4 skills
        if 'skills' in pruned_data and pruned_data['skills']:
            skills_with_scores = []
            for skill in pruned_data['skills']:
                score = self._calculate_ats_relevance_score(skill, job_keywords)
                skills_with_scores.append((skill, score))
            
            skills_with_scores.sort(key=lambda x: x[1], reverse=True)
            pruned_data['skills'] = [skill for skill, score in skills_with_scores[:4]]
            logger.info("Aggressively pruned skills to top 4")
        
        # Keep only 1 most relevant project
        if 'projects' in pruned_data and pruned_data['projects']:
            projects_with_scores = []
            for project in pruned_data['projects']:
                score = self._calculate_ats_relevance_score(project, job_keywords)
                projects_with_scores.append((project, score))
            
            projects_with_scores.sort(key=lambda x: x[1], reverse=True)
            if projects_with_scores:
                top_project = projects_with_scores[0][0].copy()
                if 'description' in top_project and isinstance(top_project['description'], list):
                    top_project['description'] = top_project['description'][:1]  # Keep only 1 bullet point
                pruned_data['projects'] = [top_project]
                logger.info("Aggressively pruned projects to 1 item with minimal bullets")
        
        # Truncate summary aggressively
        if 'summary' in pruned_data:
            summary = pruned_data['summary']
            if len(summary) > 100:  # Very short summary for aggressive pruning
                pruned_data['summary'] = summary[:100] + "..."
                logger.info("Aggressively truncated summary to 100 characters")
        
        # Remove certifications and education for aggressive pruning
        if 'certifications' in pruned_data:
            pruned_data['certifications'] = []
            logger.info("Removed certifications for aggressive pruning")
        
        if 'education' in pruned_data:
            pruned_data['education'] = []
            logger.info("Removed education for aggressive pruning")
        
        return pruned_data
    
    def _count_pdf_pages(self, pdf_path: str) -> int:
        """Count the number of pages in a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            logger.warning(f"Could not count PDF pages: {e}")
            # Fallback: estimate based on file size and content
            file_size = os.path.getsize(pdf_path)
            # Rough estimate: 1 page ≈ 50KB for typical resume
            estimated_pages = max(1, file_size // 50000)
            logger.info(f"Estimated pages based on file size: {estimated_pages}")
            return estimated_pages
    
    def _generate_pdf_with_settings(self, experience_data: Dict, output_path: str, 
                                   name: str, contact_info: str, 
                                   font_size: float, margin: float, line_spacing: float) -> str:
        """Generate PDF with specific compression settings"""
        # Update styles with current compression settings
        self._update_styles_for_compression(font_size, margin, line_spacing)
        
        # Create PDF document with current margins
        doc = SimpleDocTemplate(output_path, pagesize=self.page_size,
                              rightMargin=margin, leftMargin=margin,
                              topMargin=margin, bottomMargin=margin)
        
        # Build story (content)
        story = []
        
        # Header section - Harvard style
        story.append(Paragraph(name, self.styles['HarvardName']))
        story.append(Paragraph(contact_info, self.styles['HarvardContact']))
        
        # Professional Summary
        if experience_data.get('summary') and experience_data['summary'].strip():
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['HarvardSectionHeader']))
            story.append(Paragraph(experience_data['summary'], self.styles['HarvardSummary']))
        
        # Professional Experience
        if experience_data.get('experience'):
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['HarvardSectionHeader']))
            
            for i, job in enumerate(experience_data['experience']):
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
                                enhanced_bullet = self._ensure_achievement_verbs(bullet)
                                job_content.append(Paragraph(f"• {enhanced_bullet}", self.styles['HarvardBullet']))
                    else:
                        sentences = description.split('.')
                        for sentence in sentences:
                            if sentence.strip():
                                enhanced_sentence = self._ensure_achievement_verbs(sentence.strip())
                                job_content.append(Paragraph(f"• {enhanced_sentence}.", self.styles['HarvardBullet']))
                
                # Add spacing between jobs
                if i < len(experience_data['experience']) - 1:
                    job_content.append(Spacer(1, max(0.05*inch, font_size * 0.005*inch)))
                
                story.append(KeepTogether(job_content))
        
        # Technical Skills
        if experience_data.get('skills'):
            story.append(Paragraph("TECHNICAL SKILLS & EXPERTISE", self.styles['HarvardSectionHeader']))
            
            skills = experience_data['skills']
            if skills:
                for skill in skills:
                    if isinstance(skill, dict):
                        skill_name = skill.get('name', str(skill))
                    else:
                        skill_name = str(skill)
                    
                    if skill_name.strip():
                        story.append(Paragraph(f"• {skill_name}", self.styles['HarvardSkill']))
        
        # Projects
        if experience_data.get('projects'):
            story.append(Paragraph("PROJECTS & ACHIEVEMENTS", self.styles['HarvardSectionHeader']))
            
            for i, project in enumerate(experience_data['projects']):
                project_content = []
                
                project_name = project.get('name', '')
                if project_name:
                    project_content.append(Paragraph(project_name, self.styles['HarvardProjectName']))
                
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
                
                tech_list = project.get('technologies', [])
                if tech_list:
                    tech_text = ', '.join(tech_list)
                    project_content.append(Paragraph(f"<i>Technologies: {tech_text}</i>", self.styles['HarvardBullet']))
                
                if i < len(experience_data['projects']) - 1:
                    project_content.append(Spacer(1, max(0.04*inch, font_size * 0.004*inch)))
                
                story.append(KeepTogether(project_content))
        
        # Certifications
        if experience_data.get('certifications'):
            story.append(Paragraph("CERTIFICATIONS & TRAINING", self.styles['HarvardSectionHeader']))
            
            for cert in experience_data['certifications']:
                if cert.strip():
                    story.append(Paragraph(f"• {cert}", self.styles['HarvardCertification']))
        
        # Education
        if experience_data.get('education'):
            story.append(Paragraph("EDUCATION", self.styles['HarvardSectionHeader']))
            
            for edu in experience_data['education']:
                education_content = []
                
                degree = edu.get('degree', '')
                if degree:
                    education_content.append(Paragraph(degree, self.styles['HarvardEducation']))
                
                institution = edu.get('institution', '')
                if institution:
                    education_content.append(Paragraph(institution, self.styles['HarvardEducation']))
                
                year = edu.get('year', '')
                gpa = edu.get('gpa', '')
                if year or gpa:
                    details = []
                    if year:
                        details.append(year)
                    if gpa:
                        details.append(gpa)
                    education_content.append(Paragraph(' • '.join(details), self.styles['HarvardEducation']))
                
                story.append(KeepTogether(education_content))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def generate_harvard_pdf(self, experience_data: Union[str, Dict], output_path: str, 
                            name: str = "Your Name", contact_info: str = "email@example.com | phone | location",
                            job_description: str = "") -> str:
        """Generate Harvard-style professional PDF resume with STRICT page limit enforcement"""
        
        logger.info(f"Starting PDF generation with max_pages={self.max_pages}")
        
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
        
        # Initialize compression settings
        font_size = self.current_font_size
        margin = self.current_margin
        line_spacing = self.current_line_spacing
        
        # Strategy 1: Content Pruning (if job description provided)
        if job_description and self.max_pages == 1:
            logger.info("Applying Strategy 1: Content pruning for single-page resume")
            experience_data = self._prune_content_by_relevance(experience_data, job_description, self.max_pages)
        
        # Iterative compression loop
        for attempt in range(self.max_compression_attempts):
            logger.info(f"Compression attempt {attempt + 1}/{self.max_compression_attempts}")
            
            # Generate PDF with current settings
            temp_output = f"{output_path}.temp_{attempt}.pdf"
            try:
                self._generate_pdf_with_settings(experience_data, temp_output, name, contact_info, 
                                               font_size, margin, line_spacing)
                
                # Check page count
                page_count = self._count_pdf_pages(temp_output)
                logger.info(f"Generated PDF with {page_count} pages (target: {self.max_pages})")
                
                # Check if we're within page limit
                if page_count <= self.max_pages:
                    logger.info(f"✅ Page limit achieved! Moving temp file to final location")
                    os.replace(temp_output, output_path)
                    return output_path
                
                # Strategy 2: Font Size Reduction
                if font_size > self.min_font_size:
                    font_size = max(self.min_font_size, font_size - 0.5)
                    logger.info(f"Strategy 2: Reduced font size to {font_size}pt")
                    continue
                
                # Strategy 3: Margin Reduction
                if margin > self.min_margin:
                    margin = max(self.min_margin, margin - 0.1 * inch)
                    logger.info(f"Strategy 3: Reduced margins to {margin/inch:.2f} inches")
                    continue
                
                # Strategy 4: Line Spacing Reduction
                if line_spacing > 1.0:
                    line_spacing = max(1.0, line_spacing - 0.05)
                    logger.info(f"Strategy 4: Reduced line spacing to {line_spacing}")
                    continue
                
                # Strategy 5: Aggressive Content Pruning
                if attempt == self.max_compression_attempts - 1:
                    logger.warning("Final attempt: Applying aggressive content pruning")
                    experience_data = self._aggressive_content_pruning(experience_data, job_description)
                    # Reset compression settings for final attempt
                    font_size = self.min_font_size
                    margin = self.min_margin
                    line_spacing = 1.0
                    continue
                
            except Exception as e:
                logger.error(f"Error in compression attempt {attempt + 1}: {e}")
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                continue
            finally:
                # Clean up temp files
                if os.path.exists(temp_output) and temp_output != output_path:
                    try:
                        os.remove(temp_output)
                    except:
                        pass
        
        # If we get here, we couldn't meet the page limit with normal compression
        # Apply one final aggressive pruning and try again
        logger.warning("Applying final aggressive pruning to ensure page limit compliance")
        experience_data = self._aggressive_content_pruning(experience_data, job_description)
        
        # Try one more time with maximum compression
        try:
            self._generate_pdf_with_settings(experience_data, output_path, name, contact_info,
                                           self.min_font_size, self.min_margin, 1.0)
            
            # Final page count check
            final_page_count = self._count_pdf_pages(output_path)
            if final_page_count <= self.max_pages:
                logger.info(f"✅ Final aggressive pruning successful! Page limit achieved: {final_page_count} <= {self.max_pages}")
                return output_path
            else:
                logger.error(f"❌ Even aggressive pruning failed to meet page limit: {final_page_count} > {self.max_pages}")
                
        except Exception as e:
            logger.error(f"Error in final aggressive generation: {e}")
        
        # If we still can't meet the limit, create a minimal version
        logger.error(f"❌ FAILED to meet page limit after all compression strategies")
        logger.error(f"Generated PDF exceeds {self.max_pages} page limit")
        
        # Create absolute minimal version
        minimal_data = {
            "summary": "Professional summary available upon request.",
            "experience": [{
                "title": "Professional Experience",
                "company": "Various Companies",
                "duration": "Current",
                "description": ["Additional experience available upon request."]
            }],
            "skills": ["Skills list available upon request."]
        }
        
        logger.info("Generating minimal version to ensure page limit compliance")
        self._generate_pdf_with_settings(minimal_data, output_path, name, contact_info,
                                       self.min_font_size, self.min_margin, 1.0)
        
        # Add a warning note about page limit
        logger.warning("⚠️  WARNING: Generated minimal PDF due to page limit constraints")
        logger.warning("Consider reducing content or increasing max_pages parameter")
        
        return output_path

def generate_harvard_pdf_resume(experience_data: Union[str, Dict], output_path: str, 
                               name: str = "Your Name", contact_info: str = "email@example.com | phone | location",
                               max_pages: int = 2, job_description: str = "") -> str:
    """Convenience function for Harvard-style PDF resume generation with page limit enforcement"""
    generator = HarvardStylePDFGenerator(max_pages=max_pages)
    return generator.generate_harvard_pdf(experience_data, output_path, name, contact_info, job_description)

if __name__ == "__main__":
    # Test the enhanced Harvard-style PDF generator
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
    
    # Test with different page limits
    for max_pages in [1, 2]:
        output_file = f"test_harvard_resume_{max_pages}page.pdf"
        logger.info(f"Testing {max_pages}-page generation...")
        
        result = generate_harvard_pdf_resume(
            test_data, output_file, "John Doe", 
            "john@example.com | 555-1234 | New York",
            max_pages=max_pages,
            job_description="Software engineer Python React AWS"
        )
        
        logger.info(f"✅ {max_pages}-page PDF generated: {result}")
