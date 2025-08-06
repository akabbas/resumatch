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
    description: str
    skills_used: List[str] = None

@dataclass
class Project:
    name: str
    description: str
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
                    font-family: Arial, sans-serif;
                    line-height: 1.4;
                    margin: 0;
                    padding: 15px;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    font-size: 12px;
                }
                .header {
                    text-align: center;
                    border-bottom: 2px solid #2c3e50;
                    padding-bottom: 15px;
                    margin-bottom: 15px;
                }
                .name {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 3px;
                }
                .contact {
                    font-size: 12px;
                    color: #7f8c8d;
                    margin-bottom: 8px;
                }
                .section {
                    margin-bottom: 15px;
                }
                .section-title {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                    border-bottom: 1px solid #bdc3c7;
                    padding-bottom: 3px;
                    margin-bottom: 10px;
                }
                .job {
                    margin-bottom: 10px;
                }
                .job-title {
                    font-weight: bold;
                    font-size: 14px;
                    color: #34495e;
                }
                .job-company {
                    font-weight: bold;
                    color: #7f8c8d;
                    font-size: 12px;
                }
                .job-duration {
                    color: #7f8c8d;
                    font-style: italic;
                    font-size: 12px;
                }
                .job-description {
                    margin-top: 3px;
                    text-align: justify;
                    font-size: 11px;
                    line-height: 1.3;
                }
                .skills {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 6px;
                }
                .skill {
                    background-color: #ecf0f1;
                    padding: 3px 8px;
                    border-radius: 12px;
                    font-size: 10px;
                    color: #2c3e50;
                }
                .project {
                    margin-bottom: 10px;
                }
                .project-name {
                    font-weight: bold;
                    color: #34495e;
                    font-size: 13px;
                }
                .project-description {
                    margin-top: 3px;
                    font-size: 11px;
                    line-height: 1.3;
                }
                .certification {
                    margin-bottom: 3px;
                    font-size: 11px;
                }
                .summary {
                    text-align: justify;
                    font-size: 12px;
                    line-height: 1.5;
                }
                @media print {
                    body {
                        padding: 0;
                        margin: 0;
                        font-size: 10px;
                    }
                    .section {
                        page-break-inside: avoid;
                    }
                    .name {
                        font-size: 20px;
                    }
                    .section-title {
                        font-size: 14px;
                    }
                    .job-title {
                        font-size: 12px;
                    }
                    .job-description {
                        font-size: 10px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">{{ name }}</div>
                <div class="contact">
                    {{ contact_info }}
                </div>
            </div>
            
            {% if summary %}
            <div class="section">
                <div class="section-title">Professional Summary</div>
                <div class="summary">{{ summary }}</div>
            </div>
            {% endif %}
            
            {% if experience %}
            <div class="section">
                <div class="section-title">Professional Experience</div>
                {% for job in experience %}
                <div class="job">
                    <div class="job-title">{{ job.title }}</div>
                    <div class="job-company">{{ job.company }} | <span class="job-duration">{{ job.duration }}</span></div>
                    <div class="job-description">{{ job.description }}</div>
                    {% if job.skills_used %}
                    <div class="skills">
                        {% for skill in job.skills_used[:5] %}
                        <span class="skill">{{ skill }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if skills %}
            <div class="section">
                <div class="section-title">Technical Skills</div>
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
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-description">{{ project.description }}</div>
                    {% if project.technologies %}
                    <div class="skills">
                        {% for tech in project.technologies[:5] %}
                        <span class="skill">{{ tech }}</span>
                        {% endfor %}
                    </div>
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
                experience_list.append(JobExperience(
                    title=exp.get('title', ''),
                    company=exp.get('company', ''),
                    duration=exp.get('duration', ''),
                    description=exp.get('description', '')
                ))
            
            projects_list = []
            for proj in experience_data.get('projects', []):
                projects_list.append(Project(
                    name=proj.get('name', ''),
                    description=proj.get('description', ''),
                    technologies=proj.get('technologies', [])
                ))
            
            return ResumeData(
                summary=experience_data.get('summary', ''),
                experience=experience_list,
                skills=experience_data.get('skills', []),
                certifications=experience_data.get('certifications', []),
                projects=projects_list,
                education=experience_data.get('education', [])
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
        
        # Parse experience data
        resume_data = self.parse_experience_data(experience_data)
        
        # Match experience with keywords
        if resume_data.experience:
            matched_experience = self.experience_matcher.match_experience(keywords, resume_data.experience)
            resume_data.experience = matched_experience
        
        # Filter skills based on job requirements
        relevant_skills = [skill for skill in resume_data.skills 
                          if any(keyword in skill.lower() for keyword in keywords)]
        resume_data.skills = relevant_skills[:15]  # Limit to top 15 skills
        
        # Generate HTML
        html_content = self.template.render(
            name=name,
            contact_info=contact_info,
            summary=resume_data.summary,
            experience=resume_data.experience,
            skills=resume_data.skills,
            projects=resume_data.projects,
            certifications=resume_data.certifications,
            include_projects=self.include_projects
        )
        
        # Convert to PDF
        HTML(string=html_content).write_pdf(output_path)
        
        print(f"Resume generated successfully: {output_path}")
        return output_path

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