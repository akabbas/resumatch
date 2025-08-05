"""
ResuMatch Job Matcher

A module for analyzing job descriptions and matching them with experience bullets
to generate tailored resumes.
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
from collections import Counter
import spacy
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

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

@dataclass
class JobAnalysis:
    """Results of job description analysis"""
    job_title: str
    required_skills: List[str]
    responsibilities: List[str]
    keywords: List[str]
    experience_level: str
    industry: str

@dataclass
class BulletPoint:
    """Experience bullet point with metadata"""
    text: str
    tags: List[str]
    category: str = "experience"
    impact: str = ""

@dataclass
class MatchedBullet:
    """Bullet point with matching score"""
    bullet: BulletPoint
    score: float
    matched_keywords: List[str]
    relevance_reason: str

class JobDescriptionAnalyzer:
    """Analyzes job descriptions to extract key information"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.kw_model = KeyBERT()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Common job title patterns
        self.job_title_patterns = [
            r'(?:looking for|seeking|hiring)\s+([^,]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:developer|engineer|manager|analyst|specialist)',
            r'(?:position|role|job):\s*([^,]+)',
        ]
        
        # Technical skills dictionary
        self.technical_skills = {
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
        
        # Experience level indicators
        self.experience_levels = {
            'entry': ['entry level', 'junior', '0-2 years', '1-2 years', 'recent graduate'],
            'mid': ['mid level', 'intermediate', '3-5 years', '4-6 years', 'experienced'],
            'senior': ['senior', 'lead', '5+ years', '7+ years', 'expert', 'principal'],
            'management': ['manager', 'director', 'head of', 'vp', 'cto', 'ceo']
        }
    
    def extract_job_title(self, job_description: str) -> str:
        """Extract job title from job description"""
        job_description_lower = job_description.lower()
        
        # Try pattern matching first
        for pattern in self.job_title_patterns:
            matches = re.findall(pattern, job_description_lower)
            if matches:
                return matches[0].strip().title()
        
        # Fallback: look for common job title keywords
        job_keywords = ['developer', 'engineer', 'manager', 'analyst', 'specialist', 'consultant']
        words = job_description_lower.split()
        
        for i, word in enumerate(words):
            if word in job_keywords and i > 0:
                # Get the preceding words as potential title
                title_words = words[max(0, i-2):i+1]
                return ' '.join(title_words).title()
        
        return "Software Developer"  # Default fallback
    
    def extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description"""
        skills = []
        
        # Extract technical skills from dictionary
        for category, skill_list in self.technical_skills.items():
            for skill in skill_list:
                if skill in job_description.lower():
                    skills.append(skill)
        
        # Use KeyBERT for additional keyword extraction
        keywords = self.kw_model.extract_keywords(
            job_description,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            use_maxsum=True,
            nr_candidates=20,
            top_n=10
        )
        
        # Add KeyBERT keywords that look like skills
        for keyword, score in keywords:
            if score > 0.3 and len(keyword) > 2:
                skills.append(keyword.lower())
        
        return list(set(skills))[:15]  # Limit to top 15 skills
    
    def extract_responsibilities(self, job_description: str) -> List[str]:
        """Extract responsibilities from job description"""
        responsibilities = []
        
        # Look for responsibility indicators
        responsibility_patterns = [
            r'responsibilities?[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'you will[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'key duties[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'primary functions?[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by bullet points or newlines
                items = re.split(r'[•\-\*]\s*|\n\s*[•\-\*]\s*', match)
                for item in items:
                    item = item.strip()
                    if len(item) > 10:  # Filter out very short items
                        responsibilities.append(item)
        
        return responsibilities[:10]  # Limit to top 10 responsibilities
    
    def determine_experience_level(self, job_description: str) -> str:
        """Determine the experience level required"""
        job_description_lower = job_description.lower()
        
        for level, indicators in self.experience_levels.items():
            for indicator in indicators:
                if indicator in job_description_lower:
                    return level
        
        return "mid"  # Default to mid-level
    
    def extract_industry(self, job_description: str) -> str:
        """Extract industry from job description"""
        industries = {
            'technology': ['tech', 'software', 'saas', 'startup', 'fintech', 'healthtech'],
            'finance': ['banking', 'financial', 'investment', 'trading', 'insurance'],
            'healthcare': ['healthcare', 'medical', 'pharmaceutical', 'biotech'],
            'retail': ['retail', 'ecommerce', 'consumer', 'shopping'],
            'manufacturing': ['manufacturing', 'industrial', 'production', 'supply chain'],
            'education': ['education', 'learning', 'academic', 'university'],
            'government': ['government', 'public sector', 'federal', 'state'],
        }
        
        job_description_lower = job_description.lower()
        
        for industry, keywords in industries.items():
            for keyword in keywords:
                if keyword in job_description_lower:
                    return industry
        
        return "technology"  # Default to technology
    
    def analyze_job_description(self, job_description: str) -> JobAnalysis:
        """Complete analysis of job description"""
        return JobAnalysis(
            job_title=self.extract_job_title(job_description),
            required_skills=self.extract_required_skills(job_description),
            responsibilities=self.extract_responsibilities(job_description),
            keywords=self.extract_required_skills(job_description),  # Use skills as keywords
            experience_level=self.determine_experience_level(job_description),
            industry=self.extract_industry(job_description)
        )

class BulletPointMatcher:
    """Matches job requirements with experience bullet points"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
    
    def calculate_keyword_match_score(self, bullet_tags: List[str], job_keywords: List[str]) -> float:
        """Calculate score based on keyword matches"""
        if not bullet_tags or not job_keywords:
            return 0.0
        
        # Convert to lowercase for comparison
        bullet_tags_lower = [tag.lower() for tag in bullet_tags]
        job_keywords_lower = [keyword.lower() for keyword in job_keywords]
        
        # Count exact matches
        exact_matches = sum(1 for tag in bullet_tags_lower if tag in job_keywords_lower)
        
        # Count partial matches (substring)
        partial_matches = 0
        for tag in bullet_tags_lower:
            for keyword in job_keywords_lower:
                if tag in keyword or keyword in tag:
                    partial_matches += 1
        
        # Calculate score
        total_possible = len(bullet_tags_lower)
        if total_possible == 0:
            return 0.0
        
        score = (exact_matches * 0.7 + partial_matches * 0.3) / total_possible
        return min(score, 1.0)
    
    def calculate_text_similarity(self, bullet_text: str, job_description: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        try:
            # Vectorize texts
            vectors = self.vectorizer.fit_transform([bullet_text, job_description])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def calculate_fuzzy_match_score(self, bullet_text: str, job_keywords: List[str]) -> float:
        """Calculate fuzzy matching score"""
        if not job_keywords:
            return 0.0
        
        bullet_text_lower = bullet_text.lower()
        scores = []
        
        for keyword in job_keywords:
            # Use SequenceMatcher for fuzzy matching
            similarity = SequenceMatcher(None, keyword.lower(), bullet_text_lower).ratio()
            scores.append(similarity)
        
        return max(scores) if scores else 0.0
    
    def match_bullets_to_job(self, bullets: List[BulletPoint], job_analysis: JobAnalysis) -> List[MatchedBullet]:
        """Match bullet points to job requirements"""
        matched_bullets = []
        
        for bullet in bullets:
            # Calculate different types of scores
            keyword_score = self.calculate_keyword_match_score(bullet.tags, job_analysis.keywords)
            text_similarity = self.calculate_text_similarity(bullet.text, ' '.join(job_analysis.keywords))
            fuzzy_score = self.calculate_fuzzy_match_score(bullet.text, job_analysis.keywords)
            
            # Combine scores (weighted average)
            combined_score = (keyword_score * 0.5 + text_similarity * 0.3 + fuzzy_score * 0.2)
            
            # Find matched keywords
            matched_keywords = []
            bullet_text_lower = bullet.text.lower()
            for keyword in job_analysis.keywords:
                if keyword.lower() in bullet_text_lower or any(tag.lower() == keyword.lower() for tag in bullet.tags):
                    matched_keywords.append(keyword)
            
            # Generate relevance reason
            relevance_reason = self._generate_relevance_reason(bullet, matched_keywords, combined_score)
            
            matched_bullets.append(MatchedBullet(
                bullet=bullet,
                score=combined_score,
                matched_keywords=matched_keywords,
                relevance_reason=relevance_reason
            ))
        
        # Sort by score (highest first)
        matched_bullets.sort(key=lambda x: x.score, reverse=True)
        
        return matched_bullets
    
    def _generate_relevance_reason(self, bullet: BulletPoint, matched_keywords: List[str], score: float) -> str:
        """Generate a human-readable reason for the match"""
        if score > 0.8:
            return f"Excellent match: {', '.join(matched_keywords[:3])}"
        elif score > 0.6:
            return f"Good match: {', '.join(matched_keywords[:2])}"
        elif score > 0.4:
            return f"Partial match: {', '.join(matched_keywords[:1])}"
        else:
            return "Low relevance match"

class ResumeTailor:
    """Main class for tailoring resumes to job descriptions"""
    
    def __init__(self):
        self.analyzer = JobDescriptionAnalyzer()
        self.matcher = BulletPointMatcher()
    
    def tailor_resume(self, job_description: str, bullets: List[BulletPoint], 
                     top_n: int = 8) -> Dict:
        """
        Tailor resume to job description
        
        Args:
            job_description: Raw job description text
            bullets: List of BulletPoint objects
            top_n: Number of top bullets to include
            
        Returns:
            Dictionary with tailored resume components
        """
        # Step 1: Analyze job description
        print("🔍 Analyzing job description...")
        job_analysis = self.analyzer.analyze_job_description(job_description)
        
        print(f"📋 Job Title: {job_analysis.job_title}")
        print(f"🎯 Required Skills: {', '.join(job_analysis.required_skills[:5])}...")
        print(f"📊 Experience Level: {job_analysis.experience_level}")
        print(f"🏭 Industry: {job_analysis.industry}")
        
        # Step 2: Match bullets to job requirements
        print("\n🎯 Matching experience bullets...")
        matched_bullets = self.matcher.match_bullets_to_job(bullets, job_analysis)
        
        # Step 3: Select top bullets
        top_bullets = matched_bullets[:top_n]
        
        print(f"\n✅ Selected {len(top_bullets)} best matching bullets:")
        for i, matched in enumerate(top_bullets, 1):
            print(f"  {i}. Score: {matched.score:.2f} - {matched.bullet.text[:60]}...")
            print(f"     Matched keywords: {', '.join(matched.matched_keywords)}")
        
        # Step 4: Generate tailored resume components
        tailored_resume = self._generate_tailored_resume(job_analysis, top_bullets)
        
        return tailored_resume
    
    def _generate_tailored_resume(self, job_analysis: JobAnalysis, 
                                matched_bullets: List[MatchedBullet]) -> Dict:
        """Generate tailored resume components"""
        
        # Generate job-specific summary
        summary = self._generate_summary(job_analysis, matched_bullets)
        
        # Organize bullets by category
        experience_bullets = [mb for mb in matched_bullets if mb.bullet.category == "experience"]
        project_bullets = [mb for mb in matched_bullets if mb.bullet.category == "project"]
        
        # Extract skills from matched bullets
        all_skills = set()
        for matched in matched_bullets:
            all_skills.update(matched.bullet.tags)
        
        # Combine with job requirements
        combined_skills = list(set(job_analysis.required_skills + list(all_skills)))
        
        return {
            "job_title": job_analysis.job_title,
            "summary": summary,
            "experience_bullets": [mb.bullet.text for mb in experience_bullets],
            "project_bullets": [mb.bullet.text for mb in project_bullets],
            "skills": combined_skills[:15],  # Top 15 skills
            "matched_keywords": job_analysis.keywords,
            "experience_level": job_analysis.experience_level,
            "industry": job_analysis.industry,
            "matching_scores": [mb.score for mb in matched_bullets]
        }
    
    def _generate_summary(self, job_analysis: JobAnalysis, 
                         matched_bullets: List[MatchedBullet]) -> str:
        """Generate a tailored professional summary"""
        
        # Count skills by frequency
        skill_counts = Counter()
        for matched in matched_bullets:
            for tag in matched.bullet.tags:
                skill_counts[tag] += 1
        
        # Get top skills
        top_skills = [skill for skill, count in skill_counts.most_common(5)]
        
        # Generate summary based on experience level and industry
        level_descriptions = {
            "entry": "entry-level",
            "mid": "experienced",
            "senior": "senior",
            "management": "leadership"
        }
        
        level_desc = level_descriptions.get(job_analysis.experience_level, "experienced")
        
        summary = f"{level_desc.title()} {job_analysis.job_title.lower()} with expertise in {', '.join(top_skills[:3])}. "
        summary += f"Demonstrated experience in {job_analysis.industry} with strong focus on {', '.join(job_analysis.keywords[:3])}. "
        summary += f"Proven track record of delivering high-quality solutions and driving results."
        
        return summary

# Example usage and testing
def create_sample_bullets() -> List[BulletPoint]:
    """Create sample bullet points for testing"""
    return [
        BulletPoint(
            text="Developed REST APIs using Django and FastAPI serving 1M+ requests daily",
            tags=["Python", "Django", "FastAPI", "REST APIs", "Backend"],
            category="experience"
        ),
        BulletPoint(
            text="Implemented microservices architecture with Docker and Kubernetes on AWS",
            tags=["Microservices", "Docker", "Kubernetes", "AWS", "DevOps"],
            category="experience"
        ),
        BulletPoint(
            text="Managed PostgreSQL databases and Redis caching layer for high performance",
            tags=["PostgreSQL", "Redis", "Database", "Performance"],
            category="experience"
        ),
        BulletPoint(
            text="Built full-stack e-commerce platform using React and Node.js",
            tags=["React", "Node.js", "JavaScript", "Full-stack", "E-commerce"],
            category="project"
        ),
        BulletPoint(
            text="Integrated payment processing with Stripe API and implemented security best practices",
            tags=["Stripe", "API", "Security", "Payment Processing"],
            category="experience"
        ),
        BulletPoint(
            text="Led development team of 5 engineers and conducted code reviews",
            tags=["Leadership", "Team Management", "Code Review", "Mentoring"],
            category="experience"
        ),
        BulletPoint(
            text="Implemented CI/CD pipelines using GitHub Actions and automated testing",
            tags=["CI/CD", "GitHub Actions", "Testing", "Automation"],
            category="experience"
        ),
        BulletPoint(
            text="Created data analytics dashboard using Python and Chart.js",
            tags=["Python", "Data Analytics", "Chart.js", "Dashboard"],
            category="project"
        )
    ]

def main():
    """Test the job matcher functionality"""
    
    # Sample job description
    job_description = """
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
    
    Responsibilities:
    - Design and implement scalable backend services
    - Collaborate with frontend developers to integrate APIs
    - Optimize database queries and application performance
    - Deploy applications using Docker and Kubernetes
    - Write clean, maintainable code with proper documentation
    - Participate in code reviews and technical discussions
    - Mentor junior developers and share best practices
    """
    
    # Create sample bullets
    bullets = create_sample_bullets()
    
    # Initialize tailor
    tailor = ResumeTailor()
    
    # Tailor resume
    print("🎯 ResuMatch Job Tailor")
    print("=" * 50)
    
    tailored_resume = tailor.tailor_resume(job_description, bullets)
    
    # Display results
    print("\n📄 Tailored Resume Components:")
    print("=" * 50)
    print(f"Job Title: {tailored_resume['job_title']}")
    print(f"Experience Level: {tailored_resume['experience_level']}")
    print(f"Industry: {tailored_resume['industry']}")
    print(f"\nSummary: {tailored_resume['summary']}")
    print(f"\nTop Skills: {', '.join(tailored_resume['skills'][:8])}")
    print(f"\nExperience Bullets ({len(tailored_resume['experience_bullets'])}):")
    for i, bullet in enumerate(tailored_resume['experience_bullets'], 1):
        print(f"  {i}. {bullet}")
    
    if tailored_resume['project_bullets']:
        print(f"\nProject Bullets ({len(tailored_resume['project_bullets'])}):")
        for i, bullet in enumerate(tailored_resume['project_bullets'], 1):
            print(f"  {i}. {bullet}")

if __name__ == "__main__":
    main() 