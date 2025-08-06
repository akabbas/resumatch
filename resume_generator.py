import os
import json
import re
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from urllib.parse import urlparse
import spacy
from keybert import KeyBERT
from jinja2 import Template
from weasyprint import HTML
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textstat
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

@dataclass
class JobExperience:
    title: str
    company: str
    duration: str
    description: Union[str, List[str]]
    skills_used: List[str] = None

@dataclass
class Project:
    name: str
    description: Union[str, List[str]]
    technologies: List[str] = None

@dataclass
class ResumeData:
    summary: str
    experience: List[JobExperience]
    skills: List[str]
    certifications: List[str] = None
    projects: List[Project] = None
    education: List[Dict] = None

class KeywordExtractor:
    """Extracts keywords and skills from job descriptions using NLP"""
    
    def __init__(self, use_openai: bool = False):
        self.use_openai = use_openai
        self.nlp = spacy.load("en_core_web_sm")
        self.kw_model = KeyBERT()
        self.lemmatizer = WordNetLemmatizer()
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Common technical skills and tools
        self.technical_terms = {
            'programming_languages': [
                'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
                'laravel', 'rails', 'asp.net', 'node.js', 'jquery', 'bootstrap'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite',
                'mariadb', 'cassandra', 'elasticsearch'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'linode'
            ],
            'tools': [
                'git', 'docker', 'kubernetes', 'jenkins', 'jira', 'confluence',
                'slack', 'trello', 'figma', 'postman', 'swagger'
            ]
        }
        
        if use_openai and os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def extract_from_url(self, url: str) -> str:
        """Extract job description from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract content from URL: {e}")
    
    def extract_keywords_openai(self, text: str) -> List[str]:
        """Extract keywords using OpenAI API"""
        try:
            prompt = f"""
            Extract technical skills, tools, technologies, and requirements from this job description.
            Return only the most relevant technical terms as a comma-separated list.
            
            Job Description:
            {text[:2000]}
            
            Technical Skills and Tools:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical recruiter extracting skills from job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            keywords = response.choices[0].message.content.strip()
            return [kw.strip().lower() for kw in keywords.split(',')]
        
        except Exception as e:
            print(f"OpenAI extraction failed: {e}")
            return self.extract_keywords_nlp(text)
    
    def extract_keywords_nlp(self, text: str) -> List[str]:
        """Extract keywords using NLP techniques"""
        # Preprocess text
        doc = self.nlp(text.lower())
        
        # Extract technical terms
        technical_keywords = []
        
        # Check for technical terms from our dictionary
        for category, terms in self.technical_terms.items():
            for term in terms:
                if term in text.lower():
                    technical_keywords.append(term)
        
        # Use KeyBERT for additional keyword extraction
        keywords = self.kw_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            use_maxsum=True,
            nr_candidates=20,
            top_n=10
        )
        
        # Extract noun phrases and named entities
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        entities = [ent.text.lower() for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'GPE']]
        
        # Combine all keywords
        all_keywords = technical_keywords + [kw[0] for kw in keywords] + noun_phrases + entities
        
        # Clean and filter keywords
        cleaned_keywords = []
        for keyword in all_keywords:
            # Remove stop words and short terms
            if (len(keyword) > 2 and 
                keyword not in self.stop_words and
                not keyword.isdigit()):
                cleaned_keywords.append(keyword)
        
        return list(set(cleaned_keywords))[:20]  # Return top 20 unique keywords
    
    def extract_keywords(self, text: str) -> List[str]:
        """Main method to extract keywords"""
        if self.use_openai and os.getenv('OPENAI_API_KEY'):
            return self.extract_keywords_openai(text)
        else:
            return self.extract_keywords_nlp(text)

class ExperienceMatcher:
    """Matches extracted keywords with job experience"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
    
    def calculate_similarity(self, job_desc: str, experience_desc: str) -> float:
        """Calculate similarity between job description and experience"""
        try:
            # Vectorize texts
            vectors = self.vectorizer.fit_transform([job_desc, experience_desc])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def match_experience(self, keywords: List[str], experience: List[JobExperience]) -> List[JobExperience]:
        """Match experience with keywords and return relevant experiences"""
        matched_experiences = []
        
        for exp in experience:
            # Check if any keywords are mentioned in the experience
            exp_text = f"{exp.title} {exp.description}".lower()
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in exp_text)
            
            # Calculate similarity score
            similarity = self.calculate_similarity(
                ' '.join(keywords),
                exp.description
            )
            
            # Score based on keyword matches and similarity
            score = keyword_matches * 0.6 + similarity * 0.4
            
            if score > 0.1:  # Threshold for relevance
                exp.skills_used = [kw for kw in keywords if kw.lower() in exp_text.lower()]
                matched_experiences.append(exp)
        
        # Sort by relevance score
        matched_experiences.sort(key=lambda x: len(x.skills_used), reverse=True)
        return matched_experiences

class ResumeGenerator:
    """Main class for generating ATS-friendly resumes"""
    
    def __init__(self, use_openai: bool = False, max_pages: int = 2, include_projects: bool = True):
        self.keyword_extractor = KeywordExtractor(use_openai)
        self.experience_matcher = ExperienceMatcher()
        self.max_pages = max_pages
        self.include_projects = include_projects
        
        # Load HTML template
        self.template = self._load_template()
    
    def _load_template(self) -> Template:
        """Load the HTML template for resume generation"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Professional Resume</title>
            <style>
                body {
                    font-family: 'Times New Roman', Times, serif;
                    line-height: 1.2;
                    margin: 0;
                    padding: 0.3in;
                    color: #000;
                    max-width: 11in;
                    margin: 0 auto;
                    font-size: 11pt;
                    background: white;
                }
                
                /* Compact styling for single page */
                .single-page {
                    font-size: 10pt;
                    line-height: 1.1;
                }
                .single-page .section {
                    margin-bottom: 0.08in;
                }
                .single-page .job {
                    margin-bottom: 0.06in;
                }
                .single-page .job-description li {
                    margin-bottom: 0.008in;
                }
                .single-page .skills {
                    margin-bottom: 0.04in;
                }
                .single-page .skill {
                    margin-bottom: 0.015in;
                }
                .single-page .project {
                    margin-bottom: 0.06in;
                }
                .single-page .certification {
                    margin-bottom: 0.012in;
                }
                .single-page .education-item {
                    margin-bottom: 0.05in;
                }
                .header {
                    text-align: center;
                    border-bottom: 2pt solid #000;
                    padding-bottom: 0.1in;
                    margin-bottom: 0.2in;
                }
                .name {
                    font-size: 18pt;
                    font-weight: bold;
                    color: #000;
                    margin-bottom: 0.05in;
                    text-transform: uppercase;
                    letter-spacing: 1pt;
                }
                .contact {
                    font-size: 10pt;
                    color: #000;
                    margin-bottom: 0.05in;
                    line-height: 1.3;
                }
                .section {
                    margin-bottom: 0.12in;
                }
                .section-title {
                    font-size: 12pt;
                    font-weight: bold;
                    color: #000;
                    text-transform: uppercase;
                    border-bottom: 1pt solid #000;
                    padding-bottom: 0.02in;
                    margin-bottom: 0.08in;
                    letter-spacing: 0.5pt;
                }
                .job {
                    margin-bottom: 0.08in;
                }
                .job-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    margin-bottom: 0.03in;
                }
                .job-title {
                    font-weight: bold;
                    font-size: 11pt;
                    color: #000;
                    text-transform: uppercase;
                }
                .job-company {
                    font-weight: bold;
                    color: #000;
                    font-size: 11pt;
                }
                .job-duration {
                    color: #000;
                    font-size: 10pt;
                    font-style: italic;
                }
                .job-description {
                    margin-top: 0.02in;
                    font-size: 10pt;
                    line-height: 1.15;
                    text-align: left;
                    padding-left: 0.15in;
                }
                .job-description ul {
                    margin: 0;
                    padding-left: 0.15in;
                }
                .job-description li {
                    margin-bottom: 0.01in;
                }
                .skills {
                    display: block;
                    margin-top: 0.03in;
                }
                .skill {
                    display: inline-block;
                    margin-right: 0.08in;
                    margin-bottom: 0.015in;
                    font-size: 10pt;
                    color: #000;
                }
                .project {
                    margin-bottom: 0.08in;
                }
                .project-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    margin-bottom: 0.03in;
                }
                .project-name {
                    font-weight: bold;
                    color: #000;
                    font-size: 11pt;
                    text-transform: uppercase;
                }
                .project-description {
                    margin-top: 0.02in;
                    font-size: 10pt;
                    line-height: 1.15;
                    padding-left: 0.15in;
                }
                .certification {
                    margin-bottom: 0.015in;
                    font-size: 10pt;
                    padding-left: 0.15in;
                }
                .summary {
                    font-size: 10pt;
                    line-height: 1.25;
                    text-align: left;
                    padding-left: 0.15in;
                }
                .education-item {
                    margin-bottom: 0.06in;
                }
                .education-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    margin-bottom: 0.03in;
                }
                .education-degree {
                    font-weight: bold;
                    font-size: 11pt;
                    color: #000;
                    text-transform: uppercase;
                }
                .education-school {
                    font-weight: bold;
                    color: #000;
                    font-size: 11pt;
                }
                .education-date {
                    color: #000;
                    font-size: 10pt;
                    font-style: italic;
                }
                .education-details {
                    font-size: 10pt;
                    line-height: 1.15;
                    padding-left: 0.15in;
                }
                @media print {
                    body {
                        padding: 0.5in;
                        margin: 0;
                        font-size: 11pt;
                        background: white;
                    }
                    .section {
                        page-break-inside: avoid;
                    }
                    .name {
                        font-size: 18pt;
                    }
                    .section-title {
                        font-size: 12pt;
                    }
                    .job-title, .project-name, .education-degree {
                        font-size: 11pt;
                    }
                    .job-description, .project-description, .education-details {
                        font-size: 10pt;
                    }
                }
            </style>
        </head>
        <body class="{% if single_page %}single-page{% endif %}">
            <div class="header">
                <div class="name">{{ name }}</div>
                <div class="contact">
                    {{ contact_info }}
                </div>
            </div>
            
            {% if summary %}
            <div class="section">
                <div class="section-title">Summary</div>
                <div class="summary">{{ summary }}</div>
            </div>
            {% endif %}
            
            {% if experience %}
            <div class="section">
                <div class="section-title">Experience</div>
                {% for job in experience %}
                <div class="job">
                    <div class="job-header">
                        <div class="job-title">{{ job.title }}</div>
                        <div class="job-duration">{{ job.duration }}</div>
                    </div>
                    <div class="job-company">{{ job.company }}</div>
                    <div class="job-description">
                        <ul>
                            {% if job.description is string %}
                                {% for bullet in job.description.split('. ') %}
                                {% if bullet.strip() %}
                                <li>{{ bullet.strip() }}{% if not bullet.endswith('.') %}.{% endif %}</li>
                                {% endif %}
                                {% endfor %}
                            {% else %}
                                {% for bullet in job.description %}
                                <li>{{ bullet }}</li>
                                {% endfor %}
                            {% endif %}
                        </ul>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if skills %}
            <div class="section">
                <div class="section-title">Skills</div>
                <div class="skills">
                    {% for skill in skills %}
                    <span class="skill">{{ skill }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if projects and include_projects %}
            <div class="section">
                <div class="section-title">Projects</div>
                {% for project in projects %}
                <div class="project">
                    <div class="project-header">
                        <div class="project-name">{{ project.name }}</div>
                    </div>
                    <div class="project-description">
                        <ul>
                            {% if project.description is string %}
                                {% for bullet in project.description.split('. ') %}
                                {% if bullet.strip() %}
                                <li>{{ bullet.strip() }}{% if not bullet.endswith('.') %}.{% endif %}</li>
                                {% endif %}
                                {% endfor %}
                            {% else %}
                                {% for bullet in project.description %}
                                <li>{{ bullet }}</li>
                                {% endfor %}
                            {% endif %}
                        </ul>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if education %}
            <div class="section">
                <div class="section-title">Education</div>
                {% for edu in education %}
                <div class="education-item">
                    <div class="education-header">
                        <div class="education-degree">{{ edu.get('degree', 'Bachelor of Science') }}</div>
                        <div class="education-date">{{ edu.get('year', '2020') }}</div>
                    </div>
                    <div class="education-school">{{ edu.get('institution', 'University') }}</div>
                    {% if edu.get('gpa') %}
                    <div class="education-details">GPA: {{ edu.get('gpa', '') }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if certifications %}
            <div class="section">
                <div class="section-title">Certifications</div>
                {% for cert in certifications %}
                <div class="certification">{{ cert }}</div>
                {% endfor %}
            </div>
            {% endif %}
        </body>
        </html>
        """
        return Template(template_str)
    
    def parse_experience_data(self, experience_data: Union[str, Dict]) -> ResumeData:
        """Parse experience data from various formats"""
        if isinstance(experience_data, str):
            # Try to parse as JSON first
            try:
                import json
                parsed_data = json.loads(experience_data)
                return self.parse_experience_data(parsed_data)
            except (json.JSONDecodeError, TypeError):
                # Simple text format - create basic structure
                return ResumeData(
                    summary=experience_data[:200] + "..." if len(experience_data) > 200 else experience_data,
                    experience=[],
                    skills=[],
                    certifications=[],
                    projects=[]
                )
        
        elif isinstance(experience_data, dict):
            # JSON format
            experience_list = []
            for exp in experience_data.get('experience', []):
                # Handle both string and list descriptions
                description = exp.get('description', '')
                if isinstance(description, list):
                    # Keep as list for template processing
                    description = description
                else:
                    # Convert string to list for consistency
                    description = [description] if description else []
                
                experience_list.append(JobExperience(
                    title=exp.get('title', ''),
                    company=exp.get('company', ''),
                    duration=exp.get('duration', ''),
                    description=description
                ))
            
            projects_list = []
            for proj in experience_data.get('projects', []):
                # Handle both string and list descriptions
                description = proj.get('description', '')
                if isinstance(description, list):
                    # Keep as list for template processing
                    description = description
                else:
                    # Convert string to list for consistency
                    description = [description] if description else []
                
                projects_list.append(Project(
                    name=proj.get('name', ''),
                    description=description,
                    technologies=proj.get('technologies', [])
                ))
            
            # Handle nested skills structure
            skills_data = experience_data.get('skills', [])
            if isinstance(skills_data, dict):
                # Flatten nested skills structure
                flattened_skills = []
                for category, skill_list in skills_data.items():
                    if isinstance(skill_list, list):
                        flattened_skills.extend(skill_list)
                skills_list = flattened_skills
            else:
                skills_list = skills_data if isinstance(skills_data, list) else []
            
            # Handle education format
            education_data = experience_data.get('education', [])
            if isinstance(education_data, dict):
                # Convert single education object to list
                education_list = [education_data]
            else:
                education_list = education_data if isinstance(education_data, list) else []
            
            return ResumeData(
                summary=experience_data.get('summary', ''),
                experience=experience_list,
                skills=skills_list,
                certifications=experience_data.get('certifications', []),
                projects=projects_list,
                education=education_list
            )
        
        else:
            raise ValueError("Experience data must be string or dictionary")
    
    def generate_resume(self, job_description: str, experience_data: Union[str, Dict], 
                       output_path: str, name: str = "Your Name", 
                       contact_info: str = "email@example.com | phone | location") -> str:
        """Generate ATS-friendly resume PDF"""
        
        # Parse job description
        if job_description.startswith('http'):
            job_text = self.keyword_extractor.extract_from_url(job_description)
        else:
            job_text = job_description
        
        # Extract keywords from job description
        keywords = self.keyword_extractor.extract_keywords(job_text)
        print(f"Extracted keywords: {keywords[:10]}...")
        
        # Handle contact info from experience data if available
        if isinstance(experience_data, dict) and 'contact' in experience_data:
            contact = experience_data['contact']
            contact_parts = []
            if contact.get('email'):
                contact_parts.append(contact['email'])
            if contact.get('phone'):
                contact_parts.append(contact['phone'])
            if contact.get('location'):
                contact_parts.append(contact['location'])
            contact_info = ' | '.join(contact_parts) if contact_parts else contact_info
        
        # Get name from experience data if available
        if isinstance(experience_data, dict) and 'name' in experience_data:
            name = experience_data['name']
        
        # Parse experience data
        resume_data = self.parse_experience_data(experience_data)
        
        # Match experience with keywords
        if resume_data.experience:
            matched_experience = self.experience_matcher.match_experience(keywords, resume_data.experience)
            resume_data.experience = matched_experience
        
        # Intelligent skill selection based on job requirements and max pages
        relevant_skills = self._select_relevant_skills(resume_data.skills, keywords)
        print(f"Selected {len(relevant_skills)} relevant skills: {relevant_skills}")
        
        # Optimize job titles to better match target position
        resume_data = self._optimize_job_titles(resume_data, job_text, keywords)
        
        # Optimize summary to better match target job
        resume_data = self._optimize_summary(resume_data, job_text, keywords)
        
        # Optimize experience bullet points with action verbs
        resume_data = self._optimize_experience_bullets(resume_data, keywords)
        
        # Adjust content based on max pages
        resume_data = self._adjust_content_for_pages(resume_data, relevant_skills)
        print(f"Max pages: {self.max_pages}, Experience items: {len(resume_data.experience)}, Projects: {len(resume_data.projects) if resume_data.projects else 0}")
        
        # Generate HTML
        html_content = self.template.render(
            name=name,
            contact_info=contact_info,
            summary=resume_data.summary,
            experience=resume_data.experience,
            skills=resume_data.skills,
            projects=resume_data.projects,
            certifications=resume_data.certifications,
            include_projects=self.include_projects,
            single_page=self.max_pages == 1
        )
        
        # Convert to PDF
        HTML(string=html_content).write_pdf(output_path)
        
        print(f"Resume generated successfully: {output_path}")
        return output_path
    
    def _select_relevant_skills(self, all_skills: List[str], keywords: List[str]) -> List[str]:
        """Intelligently select the most relevant skills based on job keywords"""
        if not all_skills:
            return []
        
        # Score each skill based on keyword relevance
        skill_scores = []
        for skill in all_skills:
            score = 0
            skill_lower = skill.lower()
            
            # Direct keyword matches (highest priority)
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in skill_lower:
                    score += 5  # Very high score for exact matches
                elif any(word in skill_lower for word in keyword_lower.split()):
                    score += 3  # High score for partial matches
            
            # Technical skill bonuses
            tech_keywords = {
                'python': 4, 'javascript': 4, 'java': 4, 'react': 4, 'node': 4, 
                'aws': 4, 'docker': 4, 'kubernetes': 4, 'sql': 4, 'api': 4, 
                'git': 3, 'ci/cd': 3, 'postgresql': 4, 'mysql': 4, 'mongodb': 4,
                'express': 4, 'django': 4, 'flask': 4, 'fastapi': 4, 'typescript': 4,
                'redux': 3, 'tailwind': 3, 'material-ui': 3, 'jwt': 3, 'graphql': 4,
                'terraform': 3, 'jenkins': 3, 'jest': 3, 'tdd': 3, 'agile': 2
            }
            
            for tech, bonus in tech_keywords.items():
                if tech in skill_lower:
                    score += bonus
            
            # Bonus for skills that appear in job description
            job_desc_lower = ' '.join(keywords).lower()
            if any(word in job_desc_lower for word in skill_lower.split()):
                score += 2
            
            skill_scores.append((skill, score))
        
        # Sort by score and return top skills
        skill_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Adjust number of skills based on max pages
        max_skills = 10 if self.max_pages == 1 else 18
        
        # Return skills with scores > 0, prioritizing highest scores
        relevant_skills = [skill for skill, score in skill_scores[:max_skills] if score > 0]
        
        # If we don't have enough relevant skills, include some high-value technical skills
        if len(relevant_skills) < max_skills // 2:
            high_value_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'SQL', 'Git', 'Docker']
            for skill in high_value_skills:
                if skill not in relevant_skills and any(s.lower() == skill.lower() for s in all_skills):
                    relevant_skills.append(skill)
                    if len(relevant_skills) >= max_skills:
                        break
        
        return relevant_skills[:max_skills]
    
    def _adjust_content_for_pages(self, resume_data: ResumeData, relevant_skills: List[str]) -> ResumeData:
        """Adjust content to fit within max pages"""
        if self.max_pages == 1:
            # For single page, be more aggressive with content reduction
            resume_data.skills = relevant_skills[:10]  # Increased from 8 to 10
            
            # Limit experience to top 4 most relevant (increased from 3)
            if len(resume_data.experience) > 4:
                resume_data.experience = resume_data.experience[:4]
            
            # Limit projects to top 3 (increased from 2)
            if resume_data.projects and len(resume_data.projects) > 3:
                resume_data.projects = resume_data.projects[:3]
            
            # Limit certifications to top 4 (increased from 3)
            if resume_data.certifications and len(resume_data.certifications) > 4:
                resume_data.certifications = resume_data.certifications[:4]
            
            # Truncate summary if too long - cut at sentence boundary
            if len(resume_data.summary) > 250:
                truncated = resume_data.summary[:250]
                # Try to find the last complete sentence
                last_period = truncated.rfind('.')
                last_exclamation = truncated.rfind('!')
                last_question = truncated.rfind('?')
                
                # Find the last sentence ending
                last_sentence_end = max(last_period, last_exclamation, last_question)
                
                if last_sentence_end > 200:  # If we have a sentence ending in the last 50 chars
                    resume_data.summary = truncated[:last_sentence_end + 1]
                else:
                    # If no sentence ending found, try to cut at word boundary
                    last_space = truncated.rfind(' ')
                    if last_space > 200:
                        resume_data.summary = truncated[:last_space] + "..."
                    else:
                        resume_data.summary = truncated + "..."
        else:
            # For multiple pages, be more generous
            resume_data.skills = relevant_skills[:18]  # Increased from 15
            
            # Limit experience to top 6 (increased from 5)
            if len(resume_data.experience) > 6:
                resume_data.experience = resume_data.experience[:6]
            
            # Limit projects to top 5 (increased from 4)
            if resume_data.projects and len(resume_data.projects) > 5:
                resume_data.projects = resume_data.projects[:5]
        
        return resume_data
    
    def _optimize_job_titles(self, resume_data: ResumeData, job_description: str, keywords: List[str]) -> ResumeData:
        """Intelligently optimize job titles to better match target position while staying truthful"""
        if not resume_data.experience:
            return resume_data
        
        # Extract target job title from job description
        target_title = self._extract_target_job_title(job_description)
        
        for experience in resume_data.experience:
            # Only optimize if the current title is significantly different from target
            if target_title and self._should_optimize_title(experience.title, target_title):
                optimized_title = self._optimize_single_title(
                    experience.title, 
                    target_title, 
                    experience.description,
                    keywords
                )
                if optimized_title:
                    print(f"Optimized job title: '{experience.title}' → '{optimized_title}'")
                    experience.title = optimized_title
        
        return resume_data
    
    def _extract_target_job_title(self, job_description: str) -> str:
        """Extract the target job title from the job description"""
        # Common job title patterns
        title_patterns = [
            r'(?:looking for|seeking|hiring)\s+(?:a\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Developer|Engineer|Analyst|Manager|Specialist|Consultant|Lead|Architect))',
            r'(?:position|role|job)\s+(?:of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Developer|Engineer|Analyst|Manager|Specialist|Consultant|Lead|Architect))',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Developer|Engineer|Analyst|Manager|Specialist|Consultant|Lead|Architect))\s+(?:position|role|job)',
        ]
        
        import re
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _should_optimize_title(self, current_title: str, target_title: str) -> bool:
        """Determine if a title should be optimized based on similarity"""
        if not target_title:
            return False
        
        current_lower = current_title.lower()
        target_lower = target_title.lower()
        
        # Don't optimize if titles are already similar
        if current_lower == target_lower:
            return False
        
        # Check if current title contains key words from target
        target_words = target_lower.split()
        current_words = current_lower.split()
        
        # If more than 50% of target words are in current title, don't optimize
        matches = sum(1 for word in target_words if word in current_words)
        if matches / len(target_words) > 0.5:
            return False
        
        return True
    
    def _optimize_single_title(self, current_title: str, target_title: str, description: Union[str, List[str]], keywords: List[str]) -> str:
        """Optimize a single job title to better match target while staying truthful"""
        
        # Convert description to string for analysis
        if isinstance(description, list):
            desc_text = " ".join(description)
        else:
            desc_text = description
        
        # Define title optimization rules based on experience level and skills
        optimization_rules = {
            # Senior level indicators
            'senior': ['lead', 'senior', 'principal', 'staff', 'architect'],
            'lead': ['senior', 'lead', 'principal', 'staff'],
            'principal': ['senior', 'lead', 'principal', 'staff', 'architect'],
            
            # Developer variations
            'developer': ['developer', 'engineer', 'programmer', 'software engineer'],
            'engineer': ['engineer', 'developer', 'software engineer'],
            'programmer': ['developer', 'engineer', 'software engineer'],
            
            # Specialization variations
            'full stack': ['full stack', 'full-stack', 'fullstack', 'web developer'],
            'frontend': ['frontend', 'front-end', 'ui developer', 'web developer'],
            'backend': ['backend', 'back-end', 'api developer', 'server developer'],
            'software': ['software', 'application', 'systems'],
            
            # Technology-specific variations
            'python': ['python', 'software', 'application'],
            'javascript': ['javascript', 'web', 'frontend'],
            'react': ['react', 'frontend', 'web'],
            'node': ['node', 'backend', 'server'],
            'aws': ['cloud', 'devops', 'infrastructure'],
            'data': ['data', 'analytics', 'business intelligence'],
        }
        
        # Analyze current title and description
        current_lower = current_title.lower()
        desc_lower = desc_text.lower()
        
        # Find the best optimization based on target title and experience
        best_title = current_title
        
        # Check if we can add seniority level
        if 'senior' in target_title.lower() and 'senior' not in current_lower:
            if any(word in desc_lower for word in ['lead', 'mentor', 'architect', 'design', 'senior', 'principal']):
                best_title = f"Senior {current_title}"
        
        # Check if we can match the target role type
        target_role_type = self._extract_role_type(target_title)
        current_role_type = self._extract_role_type(current_title)
        
        if target_role_type and target_role_type != current_role_type:
            # Only change if the description supports it
            if self._description_supports_role_type(desc_lower, target_role_type):
                best_title = best_title.replace(current_role_type, target_role_type)
        
        # Check if we can add technology specialization
        tech_keywords = ['python', 'javascript', 'react', 'node', 'aws', 'data', 'full stack']
        for tech in tech_keywords:
            if tech in target_title.lower() and tech not in current_lower:
                if tech in desc_lower or any(tech_word in desc_lower for tech_word in [tech, 'api', 'web', 'cloud']):
                    # Add technology to title
                    if 'developer' in best_title.lower():
                        best_title = best_title.replace('Developer', f'{tech.title()} Developer')
                    elif 'engineer' in best_title.lower():
                        best_title = best_title.replace('Engineer', f'{tech.title()} Engineer')
        
        return best_title if best_title != current_title else current_title
    
    def _extract_role_type(self, title: str) -> str:
        """Extract the role type from a job title"""
        role_types = ['Developer', 'Engineer', 'Analyst', 'Manager', 'Specialist', 'Consultant', 'Lead', 'Architect']
        title_lower = title.lower()
        
        for role_type in role_types:
            if role_type.lower() in title_lower:
                return role_type
        
        return ""
    
    def _description_supports_role_type(self, description: str, role_type: str) -> bool:
        """Check if the job description supports a specific role type"""
        role_indicators = {
            'Developer': ['develop', 'code', 'program', 'build', 'create', 'implement'],
            'Engineer': ['engineer', 'design', 'architect', 'system', 'infrastructure'],
            'Analyst': ['analyze', 'data', 'report', 'insight', 'business', 'metrics'],
            'Manager': ['manage', 'lead', 'team', 'supervise', 'coordinate', 'direct'],
            'Specialist': ['specialize', 'expert', 'focus', 'domain', 'subject matter'],
            'Consultant': ['consult', 'advise', 'recommend', 'strategy', 'solution'],
            'Lead': ['lead', 'mentor', 'guide', 'senior', 'principal'],
            'Architect': ['architect', 'design', 'system', 'infrastructure', 'platform']
        }
        
        if role_type in role_indicators:
            indicators = role_indicators[role_type]
            return any(indicator in description for indicator in indicators)
        
        return False
    
    def _optimize_summary(self, resume_data: ResumeData, job_description: str, keywords: List[str]) -> ResumeData:
        """Completely rewrite the summary to match job requirements while following professional resume principles"""
        if not resume_data.summary:
            return resume_data
        
        # Extract comprehensive job requirements
        job_requirements = self._extract_job_requirements(job_description)
        
        # Analyze experience for quantifiable achievements
        achievements = self._extract_achievements(resume_data.experience)
        
        # Generate new summary based on job requirements and achievements
        new_summary = self._generate_tailored_summary(job_requirements, achievements, keywords)
        
        if new_summary and new_summary != resume_data.summary:
            print(f"Rewrote summary to better match job requirements")
            resume_data.summary = new_summary
        
        return resume_data
    
    def _extract_job_themes(self, job_description: str) -> List[str]:
        """Extract key themes from job description"""
        themes = []
        
        # Technology themes
        tech_keywords = ['python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes', 'sql', 'api', 'microservices']
        for tech in tech_keywords:
            if tech in job_description.lower():
                themes.append(tech.title())
        
        # Role themes
        role_keywords = ['senior', 'lead', 'architect', 'full stack', 'frontend', 'backend', 'devops', 'data']
        for role in role_keywords:
            if role in job_description.lower():
                themes.append(role.title())
        
        # Industry themes
        industry_keywords = ['startup', 'enterprise', 'saas', 'e-commerce', 'fintech', 'healthcare', 'ai', 'ml']
        for industry in industry_keywords:
            if industry in job_description.lower():
                themes.append(industry.title())
        
        return themes[:5]  # Limit to top 5 themes
    
    def _enhance_summary_with_themes(self, current_summary: str, themes: List[str], keywords: List[str]) -> str:
        """Enhance summary with missing themes if supported by keywords"""
        if not themes:
            return current_summary
        
        # Find themes that are supported by keywords
        supported_themes = []
        for theme in themes:
            if any(theme.lower() in keyword.lower() for keyword in keywords):
                supported_themes.append(theme)
        
        if not supported_themes:
            return current_summary
        
        # Add supported themes to summary
        theme_phrases = {
            'Python': 'Python development',
            'React': 'React applications',
            'AWS': 'AWS cloud services',
            'Docker': 'containerization with Docker',
            'Microservices': 'microservices architecture',
            'Senior': 'senior-level',
            'Lead': 'leadership',
            'Full Stack': 'full-stack development',
            'DevOps': 'DevOps practices',
            'Data': 'data-driven solutions'
        }
        
        enhancement = []
        for theme in supported_themes[:2]:  # Limit to 2 themes to avoid over-optimization
            if theme in theme_phrases:
                enhancement.append(theme_phrases[theme])
        
        if enhancement:
            # Add enhancement to summary
            if current_summary.endswith('.'):
                enhanced = current_summary[:-1] + f" with expertise in {', '.join(enhancement)}."
            else:
                enhanced = current_summary + f" with expertise in {', '.join(enhancement)}."
            
            return enhanced
        
        return current_summary
    
    def _extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract comprehensive job requirements from job description"""
        requirements = {
            'technologies': [],
            'skills': [],
            'experience_level': '',
            'responsibilities': [],
            'qualifications': []
        }
        
        # Technology extraction
        tech_keywords = [
            'python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes', 'sql', 'postgresql', 'mysql', 'mongodb',
            'django', 'flask', 'fastapi', 'express', 'vue', 'angular', 'typescript', 'java', 'c#', 'php', 'ruby',
            'git', 'jenkins', 'terraform', 'ansible', 'kubernetes', 'docker', 'microservices', 'api', 'rest', 'graphql'
        ]
        
        desc_lower = job_description.lower()
        for tech in tech_keywords:
            if tech in desc_lower:
                requirements['technologies'].append(tech.title())
        
        # Experience level extraction
        level_patterns = [
            (r'senior|lead|principal|staff', 'Senior'),
            (r'junior|entry|associate', 'Junior'),
            (r'mid|intermediate', 'Mid-level')
        ]
        
        for pattern, level in level_patterns:
            if re.search(pattern, desc_lower):
                requirements['experience_level'] = level
                break
        
        # Skills extraction
        skill_patterns = [
            'full stack', 'frontend', 'backend', 'devops', 'data', 'analytics', 'machine learning', 'ai',
            'cloud', 'microservices', 'api development', 'database design', 'testing', 'agile', 'scrum'
        ]
        
        for skill in skill_patterns:
            if skill in desc_lower:
                requirements['skills'].append(skill.title())
        
        # Responsibilities extraction (looking for action verbs)
        action_verbs = [
            'develop', 'design', 'build', 'implement', 'manage', 'lead', 'architect', 'optimize',
            'deploy', 'maintain', 'test', 'debug', 'integrate', 'configure', 'monitor', 'scale'
        ]
        
        sentences = re.split(r'[.!?]', job_description)
        for sentence in sentences:
            for verb in action_verbs:
                if verb in sentence.lower():
                    requirements['responsibilities'].append(sentence.strip())
                    break
        
        return requirements
    
    def _extract_achievements(self, experience: List[JobExperience]) -> List[Dict[str, str]]:
        """Extract quantifiable achievements from experience"""
        achievements = []
        
        for exp in experience:
            if isinstance(exp.description, list):
                desc_text = " ".join(exp.description)
            else:
                desc_text = exp.description
            
            # Look for quantifiable metrics
            metrics_patterns = [
                r'(\d+)%',  # Percentage improvements
                r'(\d+)x',  # Multipliers
                r'(\d+)\+',  # Plus indicators
                r'reduced by (\d+)',  # Reductions
                r'increased by (\d+)',  # Increases
                r'(\d+) million',  # Large numbers
                r'(\d+)k',  # Thousands
                r'(\d+)M\+',  # Millions
            ]
            
            for pattern in metrics_patterns:
                matches = re.findall(pattern, desc_text, re.IGNORECASE)
                for match in matches:
                    achievements.append({
                        'metric': match,
                        'context': exp.title,
                        'description': desc_text
                    })
        
        return achievements
    
    def _generate_tailored_summary(self, job_requirements: Dict[str, List[str]], achievements: List[Dict[str, str]], keywords: List[str]) -> str:
        """Generate a tailored summary following professional resume principles"""
        
        # Action verbs for different categories
        action_verbs = {
            'leadership': ['Led', 'Directed', 'Managed', 'Oversaw', 'Spearheaded', 'Orchestrated'],
            'technical': ['Developed', 'Built', 'Designed', 'Implemented', 'Optimized', 'Engineered'],
            'communication': ['Collaborated', 'Coordinated', 'Presented', 'Documented', 'Liaised'],
            'quantitative': ['Increased', 'Reduced', 'Improved', 'Achieved', 'Delivered', 'Generated'],
            'creative': ['Created', 'Designed', 'Innovated', 'Established', 'Pioneered']
        }
        
        # Build summary components
        components = []
        
        # 1. Professional identity (experience level + role)
        if job_requirements['experience_level']:
            level = job_requirements['experience_level']
            role_type = self._determine_role_type(job_requirements)
            components.append(f"{level} {role_type}")
        else:
            components.append("Experienced professional")
        
        # 2. Core competencies (top 3 technologies/skills)
        core_skills = job_requirements['technologies'][:3] + job_requirements['skills'][:2]
        if core_skills:
            skill_phrase = ", ".join(core_skills[:3])
            components.append(f"specializing in {skill_phrase}")
        
        # 3. Key achievement (if available)
        if achievements:
            best_achievement = self._select_best_achievement(achievements, keywords)
            if best_achievement:
                components.append(f"with proven track record of {best_achievement}")
        
        # 4. Value proposition
        value_props = self._generate_value_propositions(job_requirements, keywords)
        if value_props:
            components.append(f"demonstrating expertise in {', '.join(value_props[:2])}")
        
        # Combine components into coherent summary
        summary = self._combine_summary_components(components)
        
        # Ensure it follows professional guidelines
        summary = self._polish_summary(summary)
        
        return summary
    
    def _determine_role_type(self, job_requirements: Dict[str, List[str]]) -> str:
        """Determine the appropriate role type based on job requirements"""
        if 'Full Stack' in job_requirements['skills']:
            return "Full Stack Developer"
        elif 'Frontend' in job_requirements['skills']:
            return "Frontend Developer"
        elif 'Backend' in job_requirements['skills']:
            return "Backend Developer"
        elif 'DevOps' in job_requirements['skills']:
            return "DevOps Engineer"
        elif 'Data' in job_requirements['skills'] or 'Analytics' in job_requirements['skills']:
            return "Data Engineer"
        else:
            return "Software Developer"
    
    def _select_best_achievement(self, achievements: List[Dict[str, str]], keywords: List[str]) -> str:
        """Select the most relevant achievement based on job keywords"""
        if not achievements:
            return ""
        
        # Score achievements based on keyword relevance
        scored_achievements = []
        for achievement in achievements:
            score = 0
            desc_lower = achievement['description'].lower()
            
            for keyword in keywords:
                if keyword.lower() in desc_lower:
                    score += 1
            
            scored_achievements.append((achievement, score))
        
        # Sort by score and return the best
        scored_achievements.sort(key=lambda x: x[1], reverse=True)
        
        if scored_achievements:
            best_achievement = scored_achievements[0][0]
            # Extract a concise achievement phrase
            metric = best_achievement['metric']
            return f"delivering {metric} improvements"
        
        return ""
    
    def _generate_value_propositions(self, job_requirements: Dict[str, List[str]], keywords: List[str]) -> List[str]:
        """Generate value propositions based on job requirements"""
        value_props = []
        
        # Map requirements to value propositions
        value_mapping = {
            'Python': 'scalable backend development',
            'React': 'modern frontend applications',
            'AWS': 'cloud infrastructure',
            'Docker': 'containerized deployments',
            'Microservices': 'distributed systems',
            'API': 'RESTful API development',
            'Database': 'database optimization',
            'Testing': 'quality assurance',
            'Agile': 'agile development practices'
        }
        
        for tech in job_requirements['technologies']:
            if tech in value_mapping:
                value_props.append(value_mapping[tech])
        
        for skill in job_requirements['skills']:
            if skill in value_mapping:
                value_props.append(value_mapping[skill])
        
        return value_props[:3]  # Limit to top 3
    
    def _combine_summary_components(self, components: List[str]) -> str:
        """Combine summary components into a coherent paragraph"""
        if not components:
            return ""
        
        # Start with the first component
        summary = components[0]
        
        # Add remaining components with appropriate connectors
        for i, component in enumerate(components[1:], 1):
            if i == 1:
                summary += f" {component}"
            elif i == 2:
                summary += f" and {component}"
            else:
                summary += f", {component}"
        
        # Ensure it ends with a period
        if not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _polish_summary(self, summary: str) -> str:
        """Polish the summary to follow professional guidelines"""
        # Remove personal pronouns
        summary = re.sub(r'\b(I|We|My|Our)\b', '', summary, flags=re.IGNORECASE)
        
        # Ensure active voice
        summary = re.sub(r'\bis\b', 'demonstrates', summary, flags=re.IGNORECASE)
        summary = re.sub(r'\bare\b', 'demonstrate', summary, flags=re.IGNORECASE)
        
        # Remove unnecessary words
        summary = re.sub(r'\b(very|really|quite|extremely)\b', '', summary, flags=re.IGNORECASE)
        
        # Ensure proper capitalization
        summary = summary.capitalize()
        
        # Limit length (2-5 sentences, approximately 150-250 characters)
        if len(summary) > 250:
            # Truncate at sentence boundary
            sentences = re.split(r'[.!?]', summary)
            if len(sentences) > 2:
                summary = '. '.join(sentences[:2]) + '.'
        
        return summary
    
    def _optimize_experience_bullets(self, resume_data: ResumeData, keywords: List[str]) -> ResumeData:
        """Optimize experience bullet points with action verbs and professional language"""
        if not resume_data.experience:
            return resume_data
        
        # Action verbs categorized by type
        action_verbs = {
            'leadership': ['Led', 'Directed', 'Managed', 'Oversaw', 'Spearheaded', 'Orchestrated', 'Coordinated', 'Supervised'],
            'technical': ['Developed', 'Built', 'Designed', 'Implemented', 'Optimized', 'Engineered', 'Architected', 'Programmed'],
            'communication': ['Collaborated', 'Presented', 'Documented', 'Liaised', 'Negotiated', 'Facilitated', 'Mentored'],
            'quantitative': ['Increased', 'Reduced', 'Improved', 'Achieved', 'Delivered', 'Generated', 'Enhanced', 'Streamlined'],
            'creative': ['Created', 'Designed', 'Innovated', 'Established', 'Pioneered', 'Conceptualized', 'Redesigned'],
            'organizational': ['Organized', 'Structured', 'Systematized', 'Standardized', 'Centralized', 'Streamlined'],
            'research': ['Analyzed', 'Researched', 'Evaluated', 'Investigated', 'Diagnosed', 'Assessed', 'Reviewed']
        }
        
        for experience in resume_data.experience:
            if isinstance(experience.description, list):
                optimized_bullets = []
                for bullet in experience.description:
                    optimized_bullet = self._optimize_single_bullet(bullet, keywords, action_verbs)
                    optimized_bullets.append(optimized_bullet)
                experience.description = optimized_bullets
            else:
                # Convert string to list and optimize
                bullets = [experience.description]
                optimized_bullets = []
                for bullet in bullets:
                    optimized_bullet = self._optimize_single_bullet(bullet, keywords, action_verbs)
                    optimized_bullets.append(optimized_bullet)
                experience.description = optimized_bullets
        
        return resume_data
    
    def _optimize_single_bullet(self, bullet: str, keywords: List[str], action_verbs: Dict[str, List[str]]) -> str:
        """Optimize a single bullet point with action verbs and professional language"""
        
        # Remove personal pronouns
        bullet = re.sub(r'\b(I|We|My|Our)\b', '', bullet, flags=re.IGNORECASE)
        
        # Ensure it starts with an action verb
        bullet_lower = bullet.lower().strip()
        
        # Check if it already starts with a strong action verb
        starts_with_action = False
        for category, verbs in action_verbs.items():
            for verb in verbs:
                if bullet_lower.startswith(verb.lower()):
                    starts_with_action = True
                    break
            if starts_with_action:
                break
        
        if not starts_with_action:
            # Find the most appropriate action verb based on content and keywords
            best_verb = self._select_best_action_verb(bullet, keywords, action_verbs)
            if best_verb:
                # Replace weak verbs with strong action verbs
                weak_verbs = ['did', 'worked on', 'was responsible for', 'handled', 'dealt with']
                for weak_verb in weak_verbs:
                    if weak_verb in bullet_lower:
                        bullet = re.sub(rf'\b{weak_verb}\b', best_verb, bullet, flags=re.IGNORECASE)
                        break
                else:
                    # If no weak verb found, prepend the action verb
                    bullet = f"{best_verb} {bullet}"
        
        # Ensure active voice
        bullet = re.sub(r'\bis\b', 'demonstrates', bullet, flags=re.IGNORECASE)
        bullet = re.sub(r'\bare\b', 'demonstrate', bullet, flags=re.IGNORECASE)
        
        # Remove unnecessary words
        bullet = re.sub(r'\b(very|really|quite|extremely)\b', '', bullet, flags=re.IGNORECASE)
        
        # Ensure proper capitalization
        bullet = bullet.capitalize()
        
        # Ensure it ends with a period
        if not bullet.endswith('.'):
            bullet += '.'
        
        return bullet
    
    def _select_best_action_verb(self, bullet: str, keywords: List[str], action_verbs: Dict[str, List[str]]) -> str:
        """Select the best action verb based on bullet content and job keywords"""
        bullet_lower = bullet.lower()
        
        # Score action verbs based on relevance
        verb_scores = {}
        
        for category, verbs in action_verbs.items():
            for verb in verbs:
                score = 0
                verb_lower = verb.lower()
                
                # Check if verb matches job keywords
                for keyword in keywords:
                    if keyword.lower() in verb_lower or verb_lower in keyword.lower():
                        score += 2
                
                # Check if verb matches bullet content
                if verb_lower in bullet_lower:
                    score += 1
                
                # Bonus for technical verbs if bullet contains technical content
                if category == 'technical' and any(tech in bullet_lower for tech in ['python', 'javascript', 'api', 'database', 'system']):
                    score += 1
                
                # Bonus for quantitative verbs if bullet contains metrics
                if category == 'quantitative' and re.search(r'\d+%|\d+x|\d+\+', bullet_lower):
                    score += 1
                
                verb_scores[verb] = score
        
        # Return the highest scoring verb
        if verb_scores:
            best_verb = max(verb_scores.items(), key=lambda x: x[1])
            return best_verb[0] if best_verb[1] > 0 else "Developed"
        
        return "Developed"  # Default fallback

def main():
    """Example usage"""
    # Example job description
    job_desc = """
    Senior Python Developer
    
    We are looking for a Senior Python Developer to join our team. 
    The ideal candidate should have:
    - 5+ years of experience with Python
    - Experience with Django, Flask, or FastAPI
    - Knowledge of PostgreSQL, MySQL, or MongoDB
    - Experience with AWS, Docker, and Kubernetes
    - Familiarity with React, JavaScript, and HTML/CSS
    - Experience with Git and CI/CD pipelines
    - Knowledge of REST APIs and microservices architecture
    """
    
    # Example experience data
    experience_data = {
        "summary": "Experienced software developer with 5+ years in Python development, specializing in web applications and API development.",
        "experience": [
            {
                "title": "Senior Python Developer",
                "company": "Tech Solutions Inc.",
                "duration": "2020-2023",
                "description": "Led development of REST APIs using Django and FastAPI. Implemented microservices architecture with Docker and Kubernetes. Managed PostgreSQL databases and integrated with React frontend."
            },
            {
                "title": "Python Developer",
                "company": "StartupXYZ",
                "duration": "2018-2020",
                "description": "Developed web applications using Flask and SQLAlchemy. Deployed applications on AWS using Docker containers. Worked with MongoDB and Redis for data storage."
            }
        ],
        "skills": ["Python", "Django", "Flask", "FastAPI", "PostgreSQL", "MongoDB", "AWS", "Docker", "Kubernetes", "React", "JavaScript", "Git", "REST APIs"],
        "certifications": ["AWS Certified Developer", "Docker Certified Associate"],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built a full-stack e-commerce platform using Django, React, and PostgreSQL. Implemented payment processing with Stripe API.",
                "technologies": ["Django", "React", "PostgreSQL", "Stripe", "Docker"]
            }
        ]
    }
    
    # Generate resume
    generator = ResumeGenerator(use_openai=False, max_pages=2, include_projects=True)
    generator.generate_resume(
        job_description=job_desc,
        experience_data=experience_data,
        output_path="generated_resume.pdf",
        name="John Doe",
        contact_info="john.doe@email.com | (555) 123-4567 | San Francisco, CA"
    )

if __name__ == "__main__":
    main() 