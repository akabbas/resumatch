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
                    padding: 0.5in;
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
                    margin-bottom: 0.1in;
                }
                .single-page .job {
                    margin-bottom: 0.08in;
                }
                .single-page .job-description li {
                    margin-bottom: 0.01in;
                }
                .single-page .skills {
                    margin-bottom: 0.05in;
                }
                .single-page .skill {
                    margin-bottom: 0.02in;
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
                    margin-bottom: 0.15in;
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
                    margin-bottom: 0.1in;
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
                    line-height: 1.2;
                    text-align: left;
                    padding-left: 0.2in;
                }
                .job-description ul {
                    margin: 0;
                    padding-left: 0.2in;
                }
                .job-description li {
                    margin-bottom: 0.02in;
                }
                .skills {
                    display: block;
                    margin-top: 0.05in;
                }
                .skill {
                    display: inline-block;
                    margin-right: 0.1in;
                    margin-bottom: 0.02in;
                    font-size: 10pt;
                    color: #000;
                }
                .project {
                    margin-bottom: 0.1in;
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
                    line-height: 1.2;
                    padding-left: 0.2in;
                }
                .certification {
                    margin-bottom: 0.02in;
                    font-size: 10pt;
                    padding-left: 0.2in;
                }
                .summary {
                    font-size: 10pt;
                    line-height: 1.3;
                    text-align: left;
                    padding-left: 0.2in;
                }
                .education-item {
                    margin-bottom: 0.08in;
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
                    line-height: 1.2;
                    padding-left: 0.2in;
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
        max_skills = 8 if self.max_pages == 1 else 15
        
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
            resume_data.skills = relevant_skills[:8]  # Limit skills
            
            # Limit experience to top 3 most relevant
            if len(resume_data.experience) > 3:
                resume_data.experience = resume_data.experience[:3]
            
            # Limit projects to top 2
            if resume_data.projects and len(resume_data.projects) > 2:
                resume_data.projects = resume_data.projects[:2]
            
            # Limit certifications to top 3
            if resume_data.certifications and len(resume_data.certifications) > 3:
                resume_data.certifications = resume_data.certifications[:3]
            
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
            resume_data.skills = relevant_skills[:15]
            
            # Limit experience to top 5
            if len(resume_data.experience) > 5:
                resume_data.experience = resume_data.experience[:5]
            
            # Limit projects to top 4
            if resume_data.projects and len(resume_data.projects) > 4:
                resume_data.projects = resume_data.projects[:4]
        
        return resume_data

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