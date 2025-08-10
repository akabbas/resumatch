#!/usr/bin/env python3
"""
Dynamic Resume Generator - Analyzes any job description and customizes resume automatically
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any

class DynamicResumeGenerator:
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
        .analysis {{ background: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #007bff; }}
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

    <div class="analysis">
        <strong>Job Analysis:</strong><br>
        <strong>Job Title:</strong> {job_title}<br>
        <strong>Key Skills Required:</strong> {required_skills}<br>
        <strong>Experience Level:</strong> {experience_level}<br>
        <strong>Industry Focus:</strong> {industry_focus}<br>
        <strong>Skills Matched:</strong> {skills_matched}
    </div>
</body>
</html>
        """

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Analyze any job description to extract key information"""
        
        job_lower = job_description.lower()
        analysis = {
            'job_title': self.extract_job_title(job_description),
            'required_skills': self.extract_required_skills(job_lower),
            'experience_level': self.determine_experience_level(job_lower),
            'industry_focus': self.determine_industry_focus(job_lower),
            'responsibilities': self.extract_responsibilities(job_lower),
            'technologies': self.extract_technologies(job_lower),
            'soft_skills': self.extract_soft_skills(job_lower)
        }
        
        return analysis

    def extract_job_title(self, job_description: str) -> str:
        """Extract the most likely job title from the description"""
        
        # Common job title patterns
        title_patterns = [
            r'(?:seeking|looking for|hiring|position|role|job)\s+(?:a\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:position|role|job|opportunity)',
            r'(?:title|position):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return match.group(1).title()
        
        # Fallback: look for common job titles
        common_titles = [
            'developer', 'engineer', 'analyst', 'administrator', 'manager',
            'specialist', 'consultant', 'coordinator', 'lead', 'architect'
        ]
        
        for title in common_titles:
            if title in job_description.lower():
                # Try to get the full title
                words = job_description.split()
                for i, word in enumerate(words):
                    if title.lower() in word.lower():
                        # Get 2-3 words before the title
                        start = max(0, i-2)
                        end = min(len(words), i+1)
                        return ' '.join(words[start:end]).title()
        
        return "Professional"

    def extract_required_skills(self, job_lower: str) -> List[str]:
        """Extract required skills from job description"""
        
        # Technical skills dictionary
        tech_skills = {
            'programming': ['python', 'java', 'javascript', 'sql', 'c++', 'c#', 'php', 'ruby', 'go', 'rust'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'redis', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'crm_erp': ['salesforce', 'oracle crm', 'sap', 'dynamics', 'hubspot', 'pipedrive'],
            'analytics': ['tableau', 'power bi', 'excel', 'r', 'sas', 'spss', 'matlab'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask'],
            'automation': ['selenium', 'puppet', 'ansible', 'chef', 'jenkins', 'gitlab'],
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'devops', 'lean']
        }
        
        found_skills = []
        
        for category, skills in tech_skills.items():
            for skill in skills:
                if skill in job_lower:
                    found_skills.append(skill.title())
        
        # Also look for general technical terms
        general_tech = [
            'api', 'rest', 'graphql', 'microservices', 'machine learning', 'ai',
            'data analysis', 'reporting', 'integration', 'automation', 'workflow',
            'configuration', 'administration', 'support', 'training', 'documentation'
        ]
        
        for term in general_tech:
            if term in job_lower:
                found_skills.append(term.title())
        
        return list(set(found_skills))[:15]  # Limit to top 15

    def determine_experience_level(self, job_lower: str) -> str:
        """Determine the experience level required"""
        
        if any(word in job_lower for word in ['senior', 'lead', 'principal', 'architect', 'manager']):
            return "Senior Level"
        elif any(word in job_lower for word in ['junior', 'entry', 'graduate', 'intern']):
            return "Entry Level"
        elif any(word in job_lower for word in ['mid', 'intermediate', '3-5 years']):
            return "Mid Level"
        else:
            return "Mid to Senior Level"

    def determine_industry_focus(self, job_lower: str) -> str:
        """Determine the industry focus"""
        
        industry_keywords = {
            'technology': ['tech', 'software', 'saas', 'startup', 'digital'],
            'finance': ['banking', 'financial', 'investment', 'fintech', 'trading'],
            'healthcare': ['medical', 'healthcare', 'pharmaceutical', 'clinical'],
            'retail': ['ecommerce', 'retail', 'consumer', 'shopping'],
            'manufacturing': ['manufacturing', 'industrial', 'production', 'supply chain'],
            'consulting': ['consulting', 'advisory', 'professional services'],
            'government': ['government', 'public sector', 'federal', 'state']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in job_lower for keyword in keywords):
                return industry.title()
        
        return "General Business"

    def extract_responsibilities(self, job_lower: str) -> List[str]:
        """Extract key responsibilities"""
        
        responsibilities = []
        
        # Look for responsibility indicators
        responsibility_patterns = [
            r'responsible for (.+?)(?:\.|,|;)',
            r'will (.+?)(?:\.|,|;)',
            r'must (.+?)(?:\.|,|;)',
            r'required to (.+?)(?:\.|,|;)',
            r'primary duties (.+?)(?:\.|,|;)'
        ]
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, job_lower)
            responsibilities.extend(matches)
        
        return responsibilities[:5]  # Limit to top 5

    def extract_technologies(self, job_lower: str) -> List[str]:
        """Extract mentioned technologies"""
        
        technologies = []
        
        # Technology patterns
        tech_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:CRM|ERP|CPQ|API|SDK|SDLC)',
            r'(?:experience with|knowledge of|proficient in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:development|administration|analysis)'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, job_lower)
            technologies.extend(matches)
        
        return list(set(technologies))[:10]

    def extract_soft_skills(self, job_lower: str) -> List[str]:
        """Extract soft skills mentioned"""
        
        soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical thinking', 'project management', 'stakeholder management',
            'collaboration', 'time management', 'attention to detail'
        ]
        
        found_skills = []
        for skill in soft_skills:
            if skill in job_lower:
                found_skills.append(skill.title())
        
        return found_skills

    def match_skills_to_job(self, job_analysis: Dict, user_skills: List[str]) -> List[str]:
        """Match user skills to job requirements"""
        
        required_skills = job_analysis['required_skills']
        technologies = job_analysis['technologies']
        all_requirements = required_skills + technologies
        
        matched_skills = []
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        for skill in user_skills:
            skill_lower = skill.lower()
            
            # Check for exact matches
            if skill_lower in [req.lower() for req in all_requirements]:
                matched_skills.append(skill)
                continue
            
            # Check for partial matches
            for requirement in all_requirements:
                req_lower = requirement.lower()
                if (skill_lower in req_lower or req_lower in skill_lower or
                    any(word in skill_lower for word in req_lower.split())):
                    matched_skills.append(skill)
                    break
        
        return matched_skills[:15]  # Limit to top 15

    def generate_tailored_summary(self, job_analysis: Dict, base_summary: str) -> str:
        """Generate a tailored summary based on job analysis"""
        
        job_title = job_analysis['job_title']
        experience_level = job_analysis['experience_level']
        industry_focus = job_analysis['industry_focus']
        key_skills = job_analysis['required_skills'][:3]  # Top 3 skills
        
        # Start with base summary
        summary = base_summary
        
        # Add job-specific focus
        focus_areas = []
        
        if any(skill.lower() in job_title.lower() for skill in ['developer', 'engineer']):
            focus_areas.append('technical development')
        if any(skill.lower() in job_title.lower() for skill in ['analyst', 'analytics']):
            focus_areas.append('data analysis')
        if any(skill.lower() in job_title.lower() for skill in ['administrator', 'admin']):
            focus_areas.append('system administration')
        if any(skill.lower() in job_title.lower() for skill in ['manager', 'lead']):
            focus_areas.append('leadership')
        
        # Add industry focus
        if industry_focus != "General Business":
            focus_areas.append(f'{industry_focus.lower()} industry')
        
        # Add key skills focus
        if key_skills:
            focus_areas.append(f"{', '.join(key_skills).lower()} expertise")
        
        if focus_areas:
            focus_text = f" with expertise in {', '.join(focus_areas)}"
            # Insert focus into summary
            if 'with' in summary:
                summary = summary.replace('with', focus_text + ' and')
            else:
                summary += focus_text
        
        return summary

    def rank_experience_by_relevance(self, experience_data: Dict, job_analysis: Dict) -> List[Dict]:
        """Rank experience entries by relevance to job requirements"""
        
        experiences = experience_data.get('experience', [])
        ranked_experiences = []
        
        for exp in experiences:
            score = 0
            exp_text = exp['title'].lower() + ' ' + exp['description'].lower()
            
            # Score based on required skills
            for skill in job_analysis['required_skills']:
                if skill.lower() in exp_text:
                    score += 2
            
            # Score based on technologies
            for tech in job_analysis['technologies']:
                if tech.lower() in exp_text:
                    score += 1
            
            # Score based on job title relevance
            job_title_lower = job_analysis['job_title'].lower()
            if any(word in exp_text for word in job_title_lower.split()):
                score += 3
            
            ranked_experiences.append((score, exp))
        
        # Sort by score (highest first) and return experiences
        ranked_experiences.sort(key=lambda x: x[0], reverse=True)
        return [exp for score, exp in ranked_experiences]

    def generate_resume_html(self, experience_data: Dict, job_description: str) -> str:
        """Generate dynamically tailored resume HTML"""
        
        # Analyze the job description
        job_analysis = self.analyze_job_description(job_description)
        
        # Generate tailored summary
        base_summary = experience_data.get('summary', '')
        summary = self.generate_tailored_summary(job_analysis, base_summary)
        
        # Rank experience by relevance
        ranked_experience = self.rank_experience_by_relevance(experience_data, job_analysis)
        
        # Generate experience HTML
        experience_html = ""
        for job in ranked_experience:
            experience_html += f"""
            <div class="job">
                <div class="job-title">{job['title']}</div>
                <div class="job-company">{job['company']} • <span class="job-duration">{job['duration']}</span></div>
                <div class="job-description">{job['description']}</div>
            </div>
            """
        
        # Match skills to job requirements
        user_skills = experience_data.get('skills', [])
        matched_skills = self.match_skills_to_job(job_analysis, user_skills)
        
        # Generate skills HTML
        skills_html = ""
        for skill in matched_skills:
            skills_html += f'<span class="skill">{skill}</span>'
        
        # Generate projects HTML (rank by relevance)
        projects_html = ""
        projects = experience_data.get('projects', [])
        
        # Simple project ranking (could be enhanced)
        for project in projects[:3]:  # Show top 3 projects
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
        
        # Prepare analysis display
        required_skills_str = ', '.join(job_analysis['required_skills'][:5])
        skills_matched_str = ', '.join(matched_skills[:5])
        
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
            education_html=education_html,
            job_title=job_analysis['job_title'],
            required_skills=required_skills_str,
            experience_level=job_analysis['experience_level'],
            industry_focus=job_analysis['industry_focus'],
            skills_matched=skills_matched_str
        )
        
        return html

    def save_html(self, html: str, filename: str):
        """Save HTML to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Resume saved as: {filename}")

def main():
    """Main function for testing"""
    generator = DynamicResumeGenerator()
    
    # Load experience data
    try:
        with open('my_experience.json', 'r', encoding='utf-8') as f:
            experience_data = json.load(f)
    except FileNotFoundError:
        print("❌ my_experience.json not found. Please create it first.")
        return
    
    # Example job description (you can replace this with any job posting)
    job_description = """
    We are seeking a Senior Revenue Operations Engineer to join our growing team. 
    The ideal candidate will have experience with Salesforce CRM, Oracle CPQ, 
    Python automation, REST API development, and workflow optimization. 
    Responsibilities include developing integrations between CRM and ERP systems, 
    automating quote-to-cash processes, and providing technical support to sales teams.
    Required skills: Python, SQL, Salesforce, Oracle CPQ, REST APIs, 
    workflow automation, and experience with revenue operations.
    """
    
    # Generate resume
    html = generator.generate_resume_html(experience_data, job_description)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ammr_dynamic_resume_{timestamp}.html"
    generator.save_html(html, filename)
    
    # Show analysis
    analysis = generator.analyze_job_description(job_description)
    print(f"\n🎯 Job Analysis:")
    print(f"   Job Title: {analysis['job_title']}")
    print(f"   Experience Level: {analysis['experience_level']}")
    print(f"   Industry Focus: {analysis['industry_focus']}")
    print(f"   Key Skills: {', '.join(analysis['required_skills'][:5])}")

if __name__ == "__main__":
    main() 