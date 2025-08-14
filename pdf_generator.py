#!/usr/bin/env python3
"""
PDF Resume Generator using ReportLab
Lightweight alternative to WeasyPrint for Heroku deployment
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from typing import Dict, List, Union

class PDFResumeGenerator:
    """Generate PDF resumes using ReportLab"""
    
    def __init__(self, page_size='letter'):
        self.page_size = letter if page_size == 'letter' else A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Custom styles for better formatting
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=5,
            backColor=colors.lightgrey
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomContact',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.darkgrey
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSkill',
            parent=self.styles['Normal'],
            fontSize=10,
            backColor=colors.lightblue,
            borderWidth=0.5,
            borderColor=colors.blue,
            borderPadding=3,
            leftIndent=0,
            rightIndent=0
        ))
    
    def generate_pdf(self, experience_data: Union[str, Dict], output_path: str, 
                     name: str = "Your Name", contact_info: str = "email@example.com | phone | location") -> str:
        """Generate PDF resume from experience data"""
        
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
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=self.page_size,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Build story (content)
        story = []
        
        # Header
        story.append(Paragraph(name, self.styles['CustomTitle']))
        story.append(Paragraph(contact_info, self.styles['CustomContact']))
        story.append(Spacer(1, 0.2*inch))
        
        # Professional Summary
        if experience_data.get('summary'):
            story.append(Paragraph("Professional Summary", self.styles['CustomHeading']))
            story.append(Paragraph(experience_data['summary'], self.styles['CustomBody']))
            story.append(Spacer(1, 0.1*inch))
        
        # Professional Experience
        if experience_data.get('experience'):
            story.append(Paragraph("Professional Experience", self.styles['CustomHeading']))
            
            for job in experience_data['experience']:
                # Job header
                job_title = job.get('title', '')
                company = job.get('company', '')
                duration = job.get('duration', '')
                
                job_header = f"<b>{job_title}</b> - {company}"
                if duration:
                    job_header += f" | {duration}"
                
                story.append(Paragraph(job_header, self.styles['CustomBody']))
                
                # Job description
                description = job.get('description', '')
                if description:
                    if isinstance(description, list):
                        for bullet in description:
                            if bullet.strip():
                                story.append(Paragraph(f"• {bullet}", self.styles['CustomBody']))
                    else:
                        story.append(Paragraph(description, self.styles['CustomBody']))
                
                story.append(Spacer(1, 0.1*inch))
        
        # Skills
        if experience_data.get('skills'):
            story.append(Paragraph("Skills", self.styles['CustomHeading']))
            
            # Create skills table for better layout
            skills = experience_data['skills']
            if skills:
                # Group skills into rows of 3
                skill_rows = []
                for i in range(0, len(skills), 3):
                    row = skills[i:i+3]
                    # Pad row to have 3 elements
                    while len(row) < 3:
                        row.append('')
                    skill_rows.append(row)
                
                # Create skills table
                skills_table = Table(skill_rows, colWidths=[2*inch, 2*inch, 2*inch])
                skills_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ]))
                
                story.append(skills_table)
                story.append(Spacer(1, 0.1*inch))
        
        # Certifications
        if experience_data.get('certifications'):
            story.append(Paragraph("Certifications", self.styles['CustomHeading']))
            for cert in experience_data['certifications']:
                if cert.strip():
                    story.append(Paragraph(f"• {cert}", self.styles['CustomBody']))
            story.append(Spacer(1, 0.1*inch))
        
        # Projects
        if experience_data.get('projects'):
            story.append(Paragraph("Projects", self.styles['CustomHeading']))
            for project in experience_data['projects']:
                project_name = project.get('name', '')
                project_desc = project.get('description', '')
                
                if project_name:
                    story.append(Paragraph(f"<b>{project_name}</b>", self.styles['CustomBody']))
                if project_desc:
                    story.append(Paragraph(project_desc, self.styles['CustomBody']))
                story.append(Spacer(1, 0.05*inch))
        
        # Build PDF
        doc.build(story)
        
        return output_path

def generate_pdf_resume(experience_data: Union[str, Dict], output_path: str, 
                        name: str = "Your Name", contact_info: str = "email@example.com | phone | location") -> str:
    """Convenience function for PDF resume generation"""
    generator = PDFResumeGenerator()
    return generator.generate_pdf(experience_data, output_path, name, contact_info)
