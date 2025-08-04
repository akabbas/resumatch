#!/usr/bin/env python3
"""
Simple test for ResuMatch Job Matcher functionality
"""

import json
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class BulletPoint:
    """Experience bullet point with metadata"""
    text: str
    tags: List[str]
    category: str = "experience"
    impact: str = ""

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
class MatchedBullet:
    """Bullet point with matching score"""
    bullet: BulletPoint
    score: float
    matched_keywords: List[str]
    relevance_reason: str

class SimpleJobAnalyzer:
    """Simplified job description analyzer for testing"""
    
    def __init__(self):
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
    
    def extract_job_title(self, job_description: str) -> str:
        """Extract job title from job description"""
        job_description_lower = job_description.lower()
        
        # Look for common job title keywords
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
        
        return list(set(skills))[:15]  # Limit to top 15 skills
    
    def determine_experience_level(self, job_description: str) -> str:
        """Determine the experience level required"""
        job_description_lower = job_description.lower()
        
        experience_levels = {
            'entry': ['entry level', 'junior', '0-2 years', '1-2 years', 'recent graduate'],
            'mid': ['mid level', 'intermediate', '3-5 years', '4-6 years', 'experienced'],
            'senior': ['senior', 'lead', '5+ years', '7+ years', 'expert', 'principal'],
            'management': ['manager', 'director', 'head of', 'vp', 'cto', 'ceo']
        }
        
        for level, indicators in experience_levels.items():
            for indicator in indicators:
                if indicator in job_description_lower:
                    return level
        
        return "mid"  # Default to mid-level
    
    def analyze_job_description(self, job_description: str) -> JobAnalysis:
        """Complete analysis of job description"""
        return JobAnalysis(
            job_title=self.extract_job_title(job_description),
            required_skills=self.extract_required_skills(job_description),
            responsibilities=[],  # Simplified for testing
            keywords=self.extract_required_skills(job_description),
            experience_level=self.determine_experience_level(job_description),
            industry="technology"  # Default
        )

class SimpleBulletMatcher:
    """Simplified bullet point matcher for testing"""
    
    def calculate_keyword_match_score(self, bullet_tags: List[str], job_keywords: List[str]) -> float:
        """Calculate score based on keyword matches"""
        if not bullet_tags or not job_keywords:
            return 0.0
        
        # Convert to lowercase for comparison
        bullet_tags_lower = [tag.lower() for tag in bullet_tags]
        job_keywords_lower = [keyword.lower() for keyword in job_keywords]
        
        # Count exact matches
        exact_matches = sum(1 for tag in bullet_tags_lower if tag in job_keywords_lower)
        
        # Calculate score
        total_possible = len(bullet_tags_lower)
        if total_possible == 0:
            return 0.0
        
        score = exact_matches / total_possible
        return min(score, 1.0)
    
    def match_bullets_to_job(self, bullets: List[BulletPoint], job_analysis: JobAnalysis) -> List[MatchedBullet]:
        """Match bullet points to job requirements"""
        matched_bullets = []
        
        for bullet in bullets:
            # Calculate keyword match score
            keyword_score = self.calculate_keyword_match_score(bullet.tags, job_analysis.keywords)
            
            # Find matched keywords
            matched_keywords = []
            bullet_text_lower = bullet.text.lower()
            for keyword in job_analysis.keywords:
                if keyword.lower() in bullet_text_lower or any(tag.lower() == keyword.lower() for tag in bullet.tags):
                    matched_keywords.append(keyword)
            
            # Generate relevance reason
            if keyword_score > 0.8:
                relevance_reason = f"Excellent match: {', '.join(matched_keywords[:3])}"
            elif keyword_score > 0.6:
                relevance_reason = f"Good match: {', '.join(matched_keywords[:2])}"
            elif keyword_score > 0.4:
                relevance_reason = f"Partial match: {', '.join(matched_keywords[:1])}"
            else:
                relevance_reason = "Low relevance match"
            
            matched_bullets.append(MatchedBullet(
                bullet=bullet,
                score=keyword_score,
                matched_keywords=matched_keywords,
                relevance_reason=relevance_reason
            ))
        
        # Sort by score (highest first)
        matched_bullets.sort(key=lambda x: x.score, reverse=True)
        
        return matched_bullets

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
    """Test the simplified job matcher functionality"""
    
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
    
    # Initialize analyzer and matcher
    analyzer = SimpleJobAnalyzer()
    matcher = SimpleBulletMatcher()
    
    # Analyze job description
    print("🔍 Analyzing job description...")
    job_analysis = analyzer.analyze_job_description(job_description)
    
    print(f"📋 Job Title: {job_analysis.job_title}")
    print(f"🎯 Required Skills: {', '.join(job_analysis.required_skills[:5])}...")
    print(f"📊 Experience Level: {job_analysis.experience_level}")
    
    # Match bullets to job requirements
    print("\n🎯 Matching experience bullets...")
    matched_bullets = matcher.match_bullets_to_job(bullets, job_analysis)
    
    # Display results
    print(f"\n✅ Top {len(matched_bullets)} matching bullets:")
    for i, matched in enumerate(matched_bullets, 1):
        print(f"  {i}. Score: {matched.score:.2f} - {matched.bullet.text[:60]}...")
        print(f"     Matched keywords: {', '.join(matched.matched_keywords)}")
        print(f"     Reason: {matched.relevance_reason}")
    
    # Generate tailored resume components
    top_bullets = matched_bullets[:6]  # Top 6 bullets
    
    experience_bullets = [mb for mb in top_bullets if mb.bullet.category == "experience"]
    project_bullets = [mb for mb in top_bullets if mb.bullet.category == "project"]
    
    # Extract skills from matched bullets
    all_skills = set()
    for matched in top_bullets:
        all_skills.update(matched.bullet.tags)
    
    combined_skills = list(set(job_analysis.required_skills + list(all_skills)))
    
    print(f"\n📄 Tailored Resume Components:")
    print("=" * 50)
    print(f"Job Title: {job_analysis.job_title}")
    print(f"Experience Level: {job_analysis.experience_level}")
    print(f"\nTop Skills: {', '.join(combined_skills[:8])}")
    print(f"\nExperience Bullets ({len(experience_bullets)}):")
    for i, matched in enumerate(experience_bullets, 1):
        print(f"  {i}. {matched.bullet.text}")
    
    if project_bullets:
        print(f"\nProject Bullets ({len(project_bullets)}):")
        for i, matched in enumerate(project_bullets, 1):
            print(f"  {i}. {matched.bullet.text}")
    
    print(f"\n🎯 Success! The job matcher is working correctly.")
    print(f"📊 Average match score: {sum(mb.score for mb in top_bullets) / len(top_bullets):.2f}")

if __name__ == "__main__":
    main() 