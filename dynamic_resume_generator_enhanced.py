#!/usr/bin/env python3
"""
Enhanced Dynamic Resume Generator with SkillTransformer Integration
Automatically transforms resume content to fit job description roles
"""

import json
import re
import copy
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from services.skill_transformer import SkillTransformer
from services.role_detector import EnhancedRoleDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDynamicResumeGenerator:
    """
    Enhanced resume generator that automatically transforms content based on target roles
    Integrates SkillTransformer for intelligent skill and experience adaptation
    """
    
    def __init__(self, use_openai: bool = False, max_pages: int = 2, include_projects: bool = True, no_transform: bool = False):
        """Initialize the enhanced resume generator with integrated services and backward compatibility"""
        self.skill_transformer = SkillTransformer()
        self.role_detector = EnhancedRoleDetector()
        self.use_openai = use_openai
        self.max_pages = max_pages
        self.include_projects = include_projects
        self.no_transform = no_transform
        self.html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Harvard-Style Resume - {name} for {target_role}</title>
    <style>
        /* Harvard Resume Best Practices - Clean, Professional, ATS-Friendly */
        @page {{
            margin: 0.75in;
            size: letter;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000;
            margin: 0;
            padding: 0;
            background: white;
        }}
        
        /* Header Section - Harvard Style */
        .header {{
            text-align: center;
            margin-bottom: 1.5em;
            border-bottom: 2pt solid #000;
            padding-bottom: 1em;
        }}
        
        .name {{
            font-size: 18pt;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1pt;
            margin-bottom: 0.5em;
        }}
        
        .contact {{
            font-size: 10pt;
            line-height: 1.6;
        }}
        
        .contact-line {{
            margin-bottom: 0.2em;
        }}
        
        /* Section Headers - Harvard Style */
        .section {{
            margin-bottom: 1.2em;
            page-break-inside: avoid;
        }}
        
        .section-title {{
            font-size: 12pt;
            font-weight: bold;
            text-transform: uppercase;
            border-bottom: 1pt solid #000;
            margin-bottom: 0.8em;
            padding-bottom: 0.2em;
        }}
        
        /* Experience Section - Harvard Style */
        .job {{
            margin-bottom: 1em;
            page-break-inside: avoid;
        }}
        
        .job-header {{
            margin-bottom: 0.5em;
        }}
        
        .job-title {{
            font-weight: bold;
            font-size: 11pt;
        }}
        
        .job-company {{
            font-weight: bold;
            font-size: 11pt;
        }}
        
        .job-duration {{
            font-style: italic;
            font-size: 10pt;
            color: #333;
        }}
        
        .job-description {{
            margin-top: 0.5em;
            margin-left: 0;
            padding-left: 0;
        }}
        
        .job-description ul {{
            margin: 0;
            padding-left: 1.5em;
        }}
        
        .job-description li {{
            margin-bottom: 0.3em;
            line-height: 1.3;
        }}
        
        /* Skills Section - Harvard Style */
        .skills {{
            margin-left: 0;
            padding-left: 0;
        }}
        
        .skills ul {{
            margin: 0;
            padding-left: 1.5em;
            list-style-type: disc;
        }}
        
        .skills li {{
            margin-bottom: 0.2em;
            line-height: 1.3;
        }}
        
        /* Projects Section - Harvard Style */
        .project {{
            margin-bottom: 0.8em;
        }}
        
        .project-name {{
            font-weight: bold;
            font-size: 11pt;
        }}
        
        .project-description {{
            margin-top: 0.3em;
            margin-left: 0;
            padding-left: 0;
        }}
        
        .project-description ul {{
            margin: 0;
            padding-left: 1.5em;
        }}
        
        .project-description li {{
            margin-bottom: 0.2em;
            line-height: 1.3;
        }}
        
        .project-tech {{
            font-style: italic;
            font-size: 10pt;
            color: #666;
            margin-top: 0.2em;
        }}
        
        /* Certifications Section - Harvard Style */
        .certification {{
            margin-bottom: 0.5em;
            line-height: 1.3;
        }}
        
        /* Education Section - Harvard Style */
        .education-item {{
            margin-bottom: 0.8em;
        }}
        
        .education-degree {{
            font-weight: bold;
            font-size: 11pt;
        }}
        
        .education-institution {{
            font-weight: bold;
            font-size: 11pt;
        }}
        
        .education-details {{
            font-size: 10pt;
            color: #333;
            margin-top: 0.2em;
        }}
        
        /* Transformation Info - Subtle Harvard Style */
        .transformation-info {{
            background: #f8f9fa;
            border-left: 3pt solid #000;
            padding: 0.5em;
            margin: 0.8em 0;
            font-size: 9pt;
            color: #333;
            font-style: italic;
        }}
        
        /* Analysis Section - Harvard Style */
        .analysis {{
            background: #f8f9fa;
            border: 1pt solid #ccc;
            padding: 0.8em;
            margin: 1em 0;
            font-size: 9pt;
            color: #333;
        }}
        
        .analysis-title {{
            font-weight: bold;
            margin-bottom: 0.5em;
            text-transform: uppercase;
            font-size: 10pt;
        }}
        
        .analysis-item {{
            margin-bottom: 0.3em;
            line-height: 1.3;
        }}
        
        /* Print Optimization */
        @media print {{
            body {{ margin: 0.5in; }}
            .section {{ page-break-inside: avoid; }}
            .job {{ page-break-inside: avoid; }}
        }}
        
        /* ATS Optimization - No fancy styling */
        .ats-friendly {{
            /* Ensure text is readable by ATS systems */
            color: #000 !important;
            background: transparent !important;
            font-family: 'Times New Roman', Times, serif !important;
        }}
    </style>
</head>
<body class="ats-friendly">
    <!-- Header Section - Harvard Style -->
    <div class="header">
        <div class="name">{name}</div>
        <div class="contact">
            <div class="contact-line">{email}</div>
            <div class="contact-line">{phone}</div>
            <div class="contact-line">{location}</div>
            <div class="contact-line">{linkedin} • {github}</div>
        </div>
    </div>

    <!-- Professional Summary Section - Harvard Style -->
    <div class="section">
        <div class="section-title">PROFESSIONAL SUMMARY</div>
        <div>{summary}</div>
        <div class="transformation-info">
            <strong>AI-Enhanced Resume:</strong> This resume has been intelligently tailored for {target_role} roles using Harvard-style best practices. All content is based on your real experience, presented through relevant professional lenses for optimal ATS matching.
        </div>
    </div>

    <!-- Professional Experience Section - Harvard Style -->
    <div class="section">
        <div class="section-title">PROFESSIONAL EXPERIENCE</div>
        {experience_html}
    </div>

    <!-- Technical Skills Section - Harvard Style -->
    <div class="section">
        <div class="section-title">TECHNICAL SKILLS & EXPERTISE</div>
        <div class="skills">
            {skills_html}
        </div>
    </div>

    <!-- Projects Section - Harvard Style -->
    <div class="section">
        <div class="section-title">PROJECTS & ACHIEVEMENTS</div>
        {projects_html}
    </div>

    <!-- Certifications Section - Harvard Style -->
    <div class="section">
        <div class="section-title">CERTIFICATIONS & TRAINING</div>
        {certifications_html}
    </div>

    <!-- Education Section - Harvard Style -->
    <div class="section">
        <div class="section-title">EDUCATION</div>
        {education_html}
    </div>

    <!-- AI Analysis Section - Harvard Style -->
    <div class="analysis">
        <div class="analysis-title">AI RESUME ANALYSIS</div>
        <div class="analysis-item"><strong>Target Role:</strong> {target_role} (Confidence: {role_confidence:.1%})</div>
        <div class="analysis-item"><strong>Transformation Strategy:</strong> {transformation_strategy}</div>
        <div class="analysis-item"><strong>Skills Enhanced:</strong> {skills_enhanced}</div>
        <div class="analysis-item"><strong>Experience Tailored:</strong> {experience_tailored}</div>
        <div class="analysis-item"><strong>ATS Optimization:</strong> {ats_optimization}</div>
    </div>
</body>
</html>
        """

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Enhanced job description analysis with role detection
        
        Args:
            job_description (str): Job description text
            
        Returns:
            Dict[str, Any]: Comprehensive job analysis including detected role
        """
        # Detect the target role
        role_info = self.role_detector.detect_role(job_description)
        target_role = role_info['target_role']
        confidence = role_info['role_confidence']
        
        # Get role alternatives for context
        alternatives = self.role_detector.get_role_alternatives(job_description, top_n=3)
        
        # Basic job analysis (keeping existing functionality)
        job_lower = job_description.lower()
        analysis = {
            'target_role': target_role,
            'role_confidence': confidence,
            'role_alternatives': alternatives,
            'job_title': self.extract_job_title(job_description),
            'required_skills': self.extract_required_skills(job_lower),
            'experience_level': self.determine_experience_level(job_lower),
            'industry_focus': self.determine_industry_focus(job_lower),
            'responsibilities': self.extract_responsibilities(job_lower),
            'technologies': self.extract_technologies(job_lower),
            'soft_skills': self.extract_soft_skills(job_lower)
        }
        
        logger.info(f"Detected target role: {target_role} (confidence: {confidence:.2f})")
        return analysis

    def transform_experience_data(self, experience_data: Dict, target_role: str) -> Dict:
        """
        Transform experience data to match the target role
        Creates a deep copy to preserve original data integrity
        
        Args:
            experience_data (Dict): Original experience data
            target_role (str): Target role for transformation
            
        Returns:
            Dict: Transformed experience data
        """
        # Create deep copy to preserve original data
        transformed_data = copy.deepcopy(experience_data)
        
        try:
            # Transform job titles
            if 'experience' in transformed_data:
                for job in transformed_data['experience']:
                    if 'title' in job:
                        original_title = job['title']
                        transformed_title = self.skill_transformer.transform_skill(original_title, target_role)
                        if transformed_title != original_title:
                            job['title'] = transformed_title
                            job['original_title'] = original_title  # Preserve original
                            logger.info(f"Transformed job title: '{original_title}' -> '{transformed_title}' for {target_role}")
            
            # Transform job descriptions (bullet points)
            if 'experience' in transformed_data:
                for job in transformed_data['experience']:
                    if 'description' in job:
                        original_desc = job['description']
                        transformed_desc = self.transform_description(original_desc, target_role)
                        if transformed_desc != original_desc:
                            job['description'] = transformed_desc
                            job['original_description'] = original_desc  # Preserve original
                            logger.info(f"Transformed job description for {target_role}")
            
            # Enhance skills section (reorder and categorize, don't transform)
            if 'skills' in transformed_data:
                enhanced_skills = self.enhance_skills_for_role(transformed_data['skills'], target_role)
                transformed_data['skills'] = enhanced_skills
            
            # Transform project descriptions
            if 'projects' in transformed_data:
                for project in transformed_data['projects']:
                    if 'description' in project:
                        original_desc = project['description']
                        transformed_desc = self.transform_description(original_desc, target_role)
                        if transformed_desc != original_desc:
                            project['description'] = transformed_desc
                            project['original_description'] = original_desc  # Preserve original
            
            # Transform summary to emphasize role-relevant aspects
            if 'summary' in transformed_data:
                original_summary = transformed_data['summary']
                transformed_summary = self.transform_summary(original_summary, target_role)
                if transformed_summary != original_summary:
                    transformed_data['summary'] = transformed_summary
                    transformed_data['original_summary'] = original_summary  # Preserve original
            
            logger.info(f"Successfully transformed experience data for {target_role}")
            
        except Exception as e:
            logger.warning(f"Error during experience transformation: {e}. Falling back to original data.")
            # Return original data if transformation fails
            return experience_data
        
        return transformed_data

    def transform_description(self, description: str, target_role: str) -> str:
        """
        Transform job/project descriptions to be more relevant to target role
        
        Args:
            description (str): Original description
            target_role (str): Target role
            
        Returns:
            str: Transformed description
        """
        if not description:
            return description
        
        # Split description into sentences or bullet points
        if isinstance(description, list):
            # Handle list of bullet points
            transformed_bullets = []
            for bullet in description:
                transformed_bullet = self.transform_single_bullet(bullet, target_role)
                transformed_bullets.append(transformed_bullet)
            return transformed_bullets
        else:
            # Handle single description string
            return self.transform_single_bullet(description, target_role)

    def transform_single_bullet(self, bullet: str, target_role: str) -> str:
        """
        Transform a single bullet point or sentence for role relevance
        
        Args:
            bullet (str): Original bullet point
            target_role (str): Target role
            
        Returns:
            str: Transformed bullet point
        """
        if not bullet:
            return bullet
        
        # Look for skills in the bullet point that can be transformed
        transformed_bullet = bullet
        
        # Get all available skills from the transformer
        available_skills = self.skill_transformer.get_available_skills()
        
        # Transform skills found in the bullet point
        for skill in available_skills:
            if skill.lower() in bullet.lower():
                transformed_skill = self.skill_transformer.transform_skill(skill, target_role)
                if transformed_skill != skill:
                    # Use regex replacement with word boundaries to avoid partial matches
                    # This prevents replacing parts of words and handles case variations
                    transformed_bullet = re.sub(
                        r'\b' + re.escape(skill) + r'\b', 
                        transformed_skill, 
                        transformed_bullet, 
                        flags=re.IGNORECASE
                    )
        
        return transformed_bullet

    def enhance_skills_for_role(self, skills: List[str], target_role: str) -> List[Dict]:
        """
        Enhance skills section by categorizing and reordering for role relevance
        Does not transform skills, just reorders and categorizes them
        
        Args:
            skills (List[str]): List of skills
            target_role (str): Target role
            
        Returns:
            List[Dict]: Enhanced skills with categories and relevance scores
        """
        enhanced_skills = []
        
        for skill in skills:
            # Check if skill can be transformed for this role
            transformed_skill = self.skill_transformer.transform_skill(skill, target_role)
            
            # Determine skill relevance and category
            relevance_score = self.calculate_skill_relevance(skill, target_role)
            
            skill_info = {
                'name': skill,
                'transformed': transformed_skill,
                'relevance_score': relevance_score,
                'category': self.categorize_skill(skill, target_role)
            }
            
            enhanced_skills.append(skill_info)
        
        # Sort by relevance score (highest first)
        enhanced_skills.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return enhanced_skills

    def calculate_skill_relevance(self, skill: str, target_role: str) -> float:
        """
        Calculate how relevant a skill is to the target role
        
        Args:
            skill (str): Skill name
            target_role (str): Target role
            
        Returns:
            float: Relevance score (0.0 to 1.0)
        """
        # Check if skill can be transformed for this role
        transformed = self.skill_transformer.transform_skill(skill, target_role)
        
        if transformed != skill:
            # Skill can be transformed, so it's highly relevant
            return 1.0
        
        # Check if skill appears in role keywords
        role_keywords = self.role_detector.role_keywords.get(target_role, [])
        skill_lower = skill.lower()
        
        relevance = 0.0
        for keyword in role_keywords:
            if keyword.lower() in skill_lower or skill_lower in keyword.lower():
                relevance += 0.3
        
        return min(1.0, relevance)

    def categorize_skill(self, skill: str, target_role: str) -> str:
        """
        Categorize a skill based on its relevance to the target role
        
        Args:
            skill (str): Skill name
            target_role (str): Target role
            
        Returns:
            str: Skill category ('primary', 'secondary', or 'general')
        """
        relevance = self.calculate_skill_relevance(skill, target_role)
        
        if relevance >= 0.8:
            return 'primary'
        elif relevance >= 0.4:
            return 'secondary'
        else:
            return 'general'

    def transform_summary(self, summary: str, target_role: str) -> str:
        """
        Transform professional summary to emphasize role-relevant aspects
        
        Args:
            summary (str): Original summary
            target_role (str): Target role
            
        Returns:
            str: Transformed summary
        """
        if not summary:
            return summary
        
        # Get role description for context
        role_desc = self.role_detector.get_role_description(target_role)
        
        # Basic transformation: emphasize role-relevant keywords
        transformed_summary = summary
        
        # Look for role-specific keywords to emphasize
        role_lower = target_role.lower()
        if 'engineer' in role_lower:
            # Emphasize technical and engineering aspects
            if 'development' not in summary.lower():
                transformed_summary = summary.replace('.', ', with strong development and technical expertise.')
        elif 'analyst' in role_lower:
            # Emphasize analysis and business aspects
            if 'analysis' not in summary.lower():
                transformed_summary = summary.replace('.', ', specializing in data analysis and business process optimization.')
        elif 'manager' in role_lower:
            # Emphasize leadership and strategy aspects
            if 'leadership' not in summary.lower():
                transformed_summary = summary.replace('.', ', with proven leadership and strategic planning capabilities.')
        
        return transformed_summary

    def generate_enhanced_resume_html(self, experience_data: Dict, job_description: str) -> str:
        """
        Generate enhanced resume HTML with automatic role-based transformations
        
        Args:
            experience_data (Dict): User's experience data
            job_description (str): Target job description
            
        Returns:
            str: Generated HTML resume
        """
        try:
            # Analyze job description and detect role
            job_analysis = self.analyze_job_description(job_description)
            target_role = job_analysis['target_role']
            role_confidence = job_analysis['role_confidence']
            
            # Transform experience data for the target role
            transformed_data = self.transform_experience_data(experience_data, target_role)
            
            # Generate transformation metrics
            transformation_metrics = self.calculate_transformation_metrics(
                experience_data, transformed_data, target_role
            )
            
            # Generate HTML content
            html_content = self._generate_html_content(
                transformed_data, job_analysis, transformation_metrics
            )
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating enhanced resume: {e}")
            # Fallback to basic resume generation
            return self._generate_fallback_html(experience_data, job_description)

    def generate_resume(self, job_description: str, experience_data, output_path: str, 
                       name: str = "Your Name", contact_info: str = "email@example.com | phone | location") -> str:
        """
        Backward compatibility method that matches the original ResumeGenerator interface
        
        Args:
            job_description (str): Target job description
            experience_data: User's experience data (dict or str)
            output_path (str): Output file path
            name (str): User's name
            contact_info (str): Contact information
            
        Returns:
            str: Path to generated file (HTML or PDF)
        """
        try:
            # Handle different experience data formats
            if isinstance(experience_data, str):
                try:
                    experience_data = json.loads(experience_data)
                except json.JSONDecodeError:
                    # Treat as plain text
                    experience_data = {"summary": experience_data, "experience": [], "skills": []}
            
            # Ensure experience_data has required structure
            if not isinstance(experience_data, dict):
                experience_data = {"summary": str(experience_data), "experience": [], "skills": []}
            
            # Add name and contact if not present
            if 'name' not in experience_data:
                experience_data['name'] = name
            if 'contact' not in experience_data:
                experience_data['contact'] = {
                    'email': contact_info.split('|')[0].strip() if '|' in contact_info else contact_info,
                    'phone': contact_info.split('|')[1].strip() if '|' in contact_info and len(contact_info.split('|')) > 1 else '',
                    'location': contact_info.split('|')[2].strip() if '|' in contact_info and len(contact_info.split('|')) > 2 else ''
                }
            
            # Generate enhanced resume HTML
            if self.no_transform:
                # Use backward compatibility mode (no transformation)
                html_content = self._generate_fallback_html(experience_data, job_description)
            else:
                # Use enhanced AI transformation
                html_content = self.generate_enhanced_resume_html(experience_data, job_description)
            
            # Determine output format based on file extension
            if output_path.lower().endswith('.pdf'):
                # Use Harvard-style PDF generator
                try:
                    from harvard_pdf_generator import generate_harvard_pdf_resume
                    
                    # Extract name and contact info
                    name = experience_data.get('name', 'Your Name')
                    contact_info = ""
                    if 'contact' in experience_data:
                        contact = experience_data['contact']
                        contact_parts = []
                        if contact.get('email'):
                            contact_parts.append(contact['email'])
                        if contact.get('phone'):
                            contact_parts.append(contact['phone'])
                        if contact.get('location'):
                            contact_parts.append(contact['location'])
                        if contact.get('linkedin'):
                            contact_parts.append(f"LinkedIn: {contact['linkedin']}")
                        if contact.get('github'):
                            contact_parts.append(f"GitHub: {contact['github']}")
                        contact_info = ' | '.join(contact_parts)
                    else:
                        contact_info = "email@example.com | phone | location"
                    
                    # Generate Harvard-style PDF
                    result_path = generate_harvard_pdf_resume(
                        experience_data, output_path, name, contact_info
                    )
                    return result_path
                    
                except ImportError:
                    logger.warning("Harvard PDF generator not available, falling back to HTML")
                    # Fallback to HTML
                    html_path = output_path.replace('.pdf', '.html')
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    return html_path
                except Exception as e:
                    logger.warning(f"PDF generation failed: {e}, falling back to HTML")
                    # Fallback to HTML
                    html_path = output_path.replace('.pdf', '.html')
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    return html_path
            else:
                # Save as HTML
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                return output_path
                
        except Exception as e:
            logger.error(f"Error in backward compatibility method: {e}")
            # Fallback to basic HTML generation
            return self._generate_fallback_html(experience_data, job_description)

    def calculate_transformation_metrics(self, original_data: Dict, transformed_data: Dict, target_role: str) -> Dict:
        """
        Calculate metrics about the transformation process
        
        Args:
            original_data (Dict): Original experience data
            transformed_data (Dict): Transformed experience data
            target_role (str): Target role
            
        Returns:
            Dict: Transformation metrics
        """
        metrics = {
            'skills_enhanced': 0,
            'experience_tailored': 0,
            'ats_optimization': 'High',
            'transformation_strategy': f"Role-specific adaptation for {target_role}"
        }
        
        # Count enhanced skills
        if 'skills' in transformed_data:
            enhanced_skills = [s for s in transformed_data['skills'] if s.get('relevance_score', 0) > 0.5]
            metrics['skills_enhanced'] = len(enhanced_skills)
        
        # Count tailored experience items
        if 'experience' in transformed_data:
            tailored_experience = [e for e in transformed_data['experience'] if 'original_title' in e or 'original_description' in e]
            metrics['experience_tailored'] = len(tailored_experience)
        
        # Determine ATS optimization level
        if metrics['skills_enhanced'] >= 5 and metrics['experience_tailored'] >= 2:
            metrics['ats_optimization'] = 'Excellent'
        elif metrics['skills_enhanced'] >= 3 and metrics['experience_tailored'] >= 1:
            metrics['ats_optimization'] = 'High'
        else:
            metrics['ats_optimization'] = 'Moderate'
        
        return metrics

    def _generate_html_content(self, transformed_data: Dict, job_analysis: Dict, metrics: Dict) -> str:
        """
        Generate the actual HTML content from transformed data
        
        Args:
            transformed_data (Dict): Transformed experience data
            job_analysis (Dict): Job analysis results
            metrics (Dict): Transformation metrics
            
        Returns:
            str: Generated HTML content
        """
        # Generate experience HTML - Harvard Style
        experience_html = ""
        if 'experience' in transformed_data:
            for job in transformed_data['experience']:
                title = job.get('title', '')
                company = job.get('company', '')
                duration = job.get('duration', '')
                description = job.get('description', '')
                
                # Format description as bullet points if it's a list
                if isinstance(description, list):
                    desc_html = "<ul>"
                    for bullet in description:
                        desc_html += f"<li>{bullet}</li>"
                    desc_html += "</ul>"
                else:
                    desc_html = f"<p>{description}</p>"
                
                experience_html += f"""
                <div class="job">
                    <div class="job-header">
                        <div class="job-title">{title}</div>
                        <div class="job-company">{company}</div>
                        <div class="job-duration">{duration}</div>
                    </div>
                    <div class="job-description">{desc_html}</div>
                </div>
                """
        
        # Generate skills HTML - Harvard Style
        skills_html = ""
        if 'skills' in transformed_data:
            skills_html = "<ul>"
            for skill_info in transformed_data['skills']:
                skill_name = skill_info.get('name', '')
                skills_html += f"<li>{skill_name}</li>"
            skills_html += "</ul>"
        
        # Generate other sections
        projects_html = self._generate_projects_html(transformed_data)
        certifications_html = self._generate_certifications_html(transformed_data)
        education_html = self._generate_education_html(transformed_data)
        
        # Get contact info
        contact = transformed_data.get('contact', {})
        name = contact.get('name', 'Your Name')
        email = contact.get('email', 'email@example.com')
        phone = contact.get('phone', 'Phone')
        location = contact.get('location', 'Location')
        linkedin = contact.get('linkedin', 'LinkedIn')
        github = contact.get('github', 'GitHub')
        
        # Fill template
        html_content = self.html_template.format(
            name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github,
            summary=transformed_data.get('summary', ''),
            experience_html=experience_html,
            skills_html=skills_html,
            projects_html=projects_html,
            certifications_html=certifications_html,
            education_html=education_html,
            target_role=job_analysis['target_role'],
            role_confidence=job_analysis['role_confidence'],
            transformation_strategy=metrics['transformation_strategy'],
            skills_enhanced=metrics['skills_enhanced'],
            experience_tailored=metrics['experience_tailored'],
            ats_optimization=metrics['ats_optimization']
        )
        
        return html_content

    def _generate_projects_html(self, data: Dict) -> str:
        """Generate projects HTML section - Harvard Style"""
        if 'projects' not in data:
            return ""
        
        projects_html = ""
        for project in data['projects']:
            name = project.get('name', '')
            description = project.get('description', '')
            tech_list = ', '.join(project.get('technologies', []))
            
            # Format description as bullet points if it's a list
            if isinstance(description, list):
                desc_html = "<ul>"
                for bullet in description:
                    desc_html += f"<li>{bullet}</li>"
                desc_html += "</ul>"
            else:
                desc_html = f"<p>{description}</p>"
            
            projects_html += f"""
            <div class="project">
                <div class="project-name">{name}</div>
                <div class="project-description">{desc_html}</div>
                <div class="project-tech">Technologies: {tech_list}</div>
            </div>
            """
        
        return projects_html

    def _generate_certifications_html(self, data: Dict) -> str:
        """Generate certifications HTML section"""
        if 'certifications' not in data:
            return ""
        
        certifications_html = ""
        for cert in data['certifications']:
            certifications_html += f"<div>• {cert}</div>"
        
        return certifications_html

    def _generate_education_html(self, data: Dict) -> str:
        """Generate education HTML section"""
        if 'education' not in data:
            return ""
        
        education_html = ""
        for edu in data['education']:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            year = edu.get('year', '')
            gpa = edu.get('gpa', '')
            
            education_html += f"""
            <div>
                <strong>{degree}</strong><br>
                {institution} • {year}
                {f" • GPA: {gpa}" if gpa else ''}
            </div>
            """
        
        return education_html

    def _generate_fallback_html(self, experience_data: Dict, job_description: str) -> str:
        """
        Generate fallback HTML when transformation fails
        
        Args:
            experience_data (Dict): Original experience data
            job_description (str): Job description
            
        Returns:
            str: Basic HTML resume
        """
        logger.warning("Using fallback HTML generation due to transformation failure")
        
        # Simple fallback HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resume - Fallback</title>
        </head>
        <body>
            <h1>Resume</h1>
            <p>Original resume content (transformation failed)</p>
            <p>Job Description: {job_description[:100]}...</p>
        </body>
        </html>
        """
        
        return html

    def _generate_experience_html(self, experience_list: List) -> str:
        """Generate HTML for experience section"""
        if not experience_list:
            return "<p>No experience data available</p>"
        
        html = ""
        for job in experience_list:
            title = job.get('title', '')
            company = job.get('company', '')
            duration = job.get('duration', '')
            description = job.get('description', '')
            
            if isinstance(description, list):
                description_html = "".join([f"<li>{desc}</li>" for desc in description])
                description_html = f"<ul>{description_html}</ul>"
            else:
                description_html = f"<p>{description}</p>"
            
            html += f"""
            <div class="job">
                <div class="job-title">{title}</div>
                <div class="job-company">{company}</div>
                <div class="job-duration">{duration}</div>
                <div class="job-description">{description_html}</div>
            </div>
            """
        return html

    def _generate_skills_html(self, skills_list: List) -> str:
        """Generate HTML for skills section"""
        if not skills_list:
            return "<p>No skills data available</p>"
        
        skills_html = ""
        for skill in skills_list:
            if isinstance(skill, dict):
                skill_name = skill.get('name', str(skill))
            else:
                skill_name = str(skill)
            skills_html += f'<span class="skill">{skill_name}</span>'
        return skills_html

    # Keep existing helper methods for backward compatibility
    def extract_job_title(self, job_description: str) -> str:
        """Extract job title from description"""
        # Implementation for extracting job title
        return "Professional"

    def extract_required_skills(self, job_lower: str) -> List[str]:
        """Extract required skills from job description"""
        # Implementation for extracting required skills
        return []

    def determine_experience_level(self, job_lower: str) -> str:
        """Determine experience level required"""
        # Implementation for determining experience level
        return "Mid to Senior Level"

    def determine_industry_focus(self, job_lower: str) -> str:
        """Determine industry focus"""
        # Implementation for determining industry focus
        return "General Business"

    def extract_responsibilities(self, job_lower: str) -> List[str]:
        """Extract responsibilities from job description"""
        # Implementation for extracting responsibilities
        return []

    def extract_technologies(self, job_lower: str) -> List[str]:
        """Extract technologies from job description"""
        # Implementation for extracting technologies
        return []

    def extract_soft_skills(self, job_lower: str) -> List[str]:
        """Extract soft skills from job description"""
        # Implementation for extracting soft skills
        return []

    def save_html(self, html: str, filename: str):
        """Save HTML to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Enhanced Resume saved as: {filename}")


def main():
    """Main function for testing the enhanced resume generator"""
    
    # Initialize the enhanced generator
    generator = EnhancedDynamicResumeGenerator()
    
    # Load experience data
    try:
        with open('my_experience.json', 'r', encoding='utf-8') as f:
            experience_data = json.load(f)
    except FileNotFoundError:
        print("❌ my_experience.json not found. Please create it first.")
        return
    
    # Test job descriptions
    test_jobs = [
        {
            'title': 'Data Scientist',
            'description': 'We are seeking a Data Scientist with Python, SQL, and machine learning experience. Must have strong analytical skills and experience with data visualization.'
        },
        {
            'title': 'DevOps Engineer',
            'description': 'Looking for a DevOps Engineer with Docker, Kubernetes, and AWS experience. Must have automation skills and CI/CD pipeline experience.'
        },
        {
            'title': 'Product Manager',
            'description': 'Seeking a Product Manager to lead product strategy and user experience design. Experience with business analysis and stakeholder management required.'
        }
    ]
    
    for i, job in enumerate(test_jobs):
        print(f"\n🎯 Testing {job['title']} role...")
        
        # Generate enhanced resume
        html = generator.generate_enhanced_resume_html(experience_data, job['description'])
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ammr_enhanced_{job['title'].lower().replace(' ', '_')}_{timestamp}.html"
        generator.save_html(html, filename)
        
        # Show analysis
        analysis = generator.analyze_job_description(job['description'])
        print(f"   Target Role: {analysis['target_role']}")
        print(f"   Confidence: {analysis['role_confidence']:.2f}")
        print(f"   Experience Level: {analysis['experience_level']}")
        print(f"   Industry Focus: {analysis['industry_focus']}")


if __name__ == "__main__":
    main()
