#!/usr/bin/env python3
"""
Improved PDF Resume Generator using ReportLab
- Optimized margins and spacing
- Better page utilization
- Controlled page breaks
- Professional formatting
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from typing import Dict, List, Union

class ImprovedPDFResumeGenerator:
    """Generate PDF resumes with improved formatting and page control"""
    
    def __init__(self, page_size='letter'):
        self.page_size = letter if page_size == 'letter' else A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles with optimized formatting"""
        
        # Title style - centered at top
        self.styles.add(ParagraphStyle(
            name='ImprovedTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=15,
            spaceBefore=0,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Contact info style - centered below title
        self.styles.add(ParagraphStyle(
            name='ImprovedContact',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=0,
            textColor=colors.darkgrey,
            fontName='Helvetica'
        ))
        
        # Section heading style - left aligned with minimal spacing
        self.styles.add(ParagraphStyle(
            name='ImprovedHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=8,
            spaceBefore=16,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            leftIndent=0,
            rightIndent=0
        ))
        
        # Body text style - optimized spacing and alignment
        self.styles.add(ParagraphStyle(
            name='ImprovedBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            spaceBefore=0,
            leading=13,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica'
        ))
        
        # Job title style - bold with minimal spacing
        self.styles.add(ParagraphStyle(
            name='ImprovedJobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=2,
            spaceBefore=0,
            leading=14,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica-Bold'
        ))
        
        # Bullet point style - optimized indentation
        self.styles.add(ParagraphStyle(
            name='ImprovedBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            spaceBefore=0,
            leading=12,
            leftIndent=0.2*inch,
            rightIndent=0,
            fontName='Helvetica'
        ))
        
        # Skills style - compact layout
        self.styles.add(ParagraphStyle(
            name='ImprovedSkill',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=2,
            spaceBefore=0,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            fontName='Helvetica'
        ))
    
    def generate_pdf(self, experience_data: Union[str, Dict], output_path: str, 
                     name: str = "Your Name", contact_info: str = "email@example.com | phone | location") -> str:
        """Generate PDF resume with improved formatting"""
        
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
        
        # Create PDF document with optimized margins
        doc = SimpleDocTemplate(output_path, pagesize=self.page_size,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Build story (content)
        story = []
        
        # Header section - optimized spacing
        story.append(Paragraph(name, self.styles['ImprovedTitle']))
        story.append(Paragraph(contact_info, self.styles['ImprovedContact']))
        
        # Professional Summary - only add if there's content
        if experience_data.get('summary') and experience_data['summary'].strip():
            story.append(Paragraph("Professional Summary", self.styles['ImprovedHeading']))
            story.append(Paragraph(experience_data['summary'], self.styles['ImprovedBody']))
        
        # Professional Experience - optimized layout
        if experience_data.get('experience'):
            story.append(Paragraph("Professional Experience", self.styles['ImprovedHeading']))
            
            for i, job in enumerate(experience_data['experience']):
                # Job header with compact formatting
                job_title = job.get('title', '')
                company = job.get('company', '')
                duration = job.get('duration', '')
                
                job_header = f"<b>{job_title}</b>"
                if company:
                    job_header += f" - {company}"
                if duration:
                    job_header += f" | {duration}"
                
                story.append(Paragraph(job_header, self.styles['ImprovedJobTitle']))
                
                # Job description with optimized bullet points
                description = job.get('description', '')
                if description:
                    if isinstance(description, list):
                        for bullet in description:
                            if bullet.strip():
                                story.append(Paragraph(f"• {bullet}", self.styles['ImprovedBullet']))
                    else:
                        story.append(Paragraph(description, self.styles['ImprovedBody']))
                
                # Add spacing between jobs, but not after the last one
                if i < len(experience_data['experience']) - 1:
                    story.append(Spacer(1, 0.05*inch))
        
        # Skills section - compact table layout
        if experience_data.get('skills'):
            story.append(Paragraph("Skills", self.styles['ImprovedHeading']))
            
            skills = experience_data['skills']
            if skills:
                # Calculate optimal columns based on content length
                avg_skill_length = sum(len(skill) for skill in skills) / len(skills)
                if avg_skill_length > 20:
                    cols = 2  # Fewer columns for longer skills
                else:
                    cols = 3  # More columns for shorter skills
                
                # Group skills into rows
                skill_rows = []
                for i in range(0, len(skills), cols):
                    row = skills[i:i+cols]
                    # Pad row to have consistent columns
                    while len(row) < cols:
                        row.append('')
                    skill_rows.append(row)
                
                # Calculate column widths for better distribution
                col_width = (doc.width) / cols
                
                # Create skills table with optimized styling
                skills_table = Table(skill_rows, colWidths=[col_width] * cols)
                skills_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ]))
                
                story.append(skills_table)
        
        # Certifications - compact layout
        if experience_data.get('certifications'):
            story.append(Paragraph("Certifications", self.styles['ImprovedHeading']))
            for cert in experience_data['certifications']:
                if cert.strip():
                    story.append(Paragraph(f"• {cert}", self.styles['ImprovedBullet']))
        
        # Projects - optimized spacing
        if experience_data.get('projects'):
            story.append(Paragraph("Projects", self.styles['ImprovedHeading']))
            for i, project in enumerate(experience_data['projects']):
                project_name = project.get('name', '')
                project_desc = project.get('description', '')
                
                if project_name:
                    story.append(Paragraph(f"<b>{project_name}</b>", self.styles['ImprovedJobTitle']))
                if project_desc:
                    if isinstance(project_desc, list):
                        for desc in project_desc:
                            if desc.strip():
                                story.append(Paragraph(f"• {desc}", self.styles['ImprovedBullet']))
                    else:
                        story.append(Paragraph(project_desc, self.styles['ImprovedBody']))
                
                # Add minimal spacing between projects
                if i < len(experience_data['projects']) - 1:
                    story.append(Spacer(1, 0.03*inch))
        
        # Build PDF
        doc.build(story)
        
        return output_path

def generate_pdf_resume(experience_data: Union[str, Dict], output_path: str, 
                        name: str = "Your Name", contact_info: str = "email@example.com | phone | location") -> str:
    """Convenience function for improved PDF resume generation"""
    generator = ImprovedPDFResumeGenerator()
    return generator.generate_pdf(experience_data, output_path, name, contact_info)
