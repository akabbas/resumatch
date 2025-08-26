"""
ResuMatch Job Matcher - Lightweight Version

A simplified module for analyzing job descriptions and matching them with experience bullets
to generate tailored resumes. This version removes heavy dependencies for Railway deployment.
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
from collections import Counter

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

class SimpleJobDescriptionAnalyzer:
    """Simplified job description analyzer without heavy dependencies"""
    
    def __init__(self):
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
                'maria', 'cassandra', 'elasticsearch'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'linode'
            ],
            'tools': [
                'git', 'docker', 'kubernetes', 'jenkins', 'jira', 'confluence',
                'slack', 'teams', 'zoom', 'figma', 'sketch', 'adobe'
            ]
        }
        
        # Common stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more',
            'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call',
            'who', 'its', 'now', 'find', 'down', 'day', 'did', 'get', 'come',
            'made', 'may', 'part'
        }
    
    def analyze_job_description(self, job_description: str) -> JobAnalysis:
        """Analyze job description to extract key information"""
        job_description_lower = job_description.lower()
        
        # Extract job title
        job_title = self._extract_job_title(job_description)
        
        # Extract skills
        required_skills = self._extract_skills(job_description_lower)
        
        # Extract responsibilities
        responsibilities = self._extract_responsibilities(job_description)
        
        # Extract keywords
        keywords = self._extract_keywords(job_description_lower)
        
        # Determine experience level
        experience_level = self._determine_experience_level(job_description_lower)
        
        # Determine industry
        industry = self._determine_industry(job_description_lower)
        
        return JobAnalysis(
            job_title=job_title,
            required_skills=required_skills,
            responsibilities=responsibilities,
            keywords=keywords,
            experience_level=experience_level,
            industry=industry
        )
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from text"""
        for pattern in self.job_title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Software Engineer"  # Default fallback
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        skills = []
        for category, skill_list in self.technical_skills.items():
            for skill in skill_list:
                if skill in text:
                    skills.append(skill)
        return list(set(skills))  # Remove duplicates
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibilities from text"""
        responsibilities = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['responsible', 'duties', 'tasks', 'will', 'must']):
                if len(line) > 10:  # Filter out very short lines
                    responsibilities.append(line)
        return responsibilities[:5]  # Limit to 5
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction based on frequency and importance
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        word_freq = Counter(words)
        
        # Filter out stop words and short words
        keywords = []
        for word, freq in word_freq.most_common(50):
            if word not in self.stop_words and len(word) > 3 and freq > 1:
                keywords.append(word)
        
        return keywords[:20]  # Limit to 20 keywords
    
    def _determine_experience_level(self, text: str) -> str:
        """Determine required experience level"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['senior', 'lead', 'principal', 'architect']):
            return "senior"
        elif any(word in text_lower for word in ['junior', 'entry', 'graduate', 'intern']):
            return "junior"
        else:
            return "mid-level"
    
    def _determine_industry(self, text: str) -> str:
        """Determine industry from text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['fintech', 'banking', 'finance']):
            return "Finance"
        elif any(word in text_lower for word in ['healthcare', 'medical', 'pharma']):
            return "Healthcare"
        elif any(word in text_lower for word in ['ecommerce', 'retail', 'shopping']):
            return "E-commerce"
        else:
            return "Technology"

class SimpleResumeTailor:
    """Simplified resume tailor without heavy dependencies"""
    
    def __init__(self):
        self.analyzer = SimpleJobDescriptionAnalyzer()
    
    def tailor_bullets(self, bullets: List[BulletPoint], job_description: str) -> List[MatchedBullet]:
        """Tailor bullet points to job description"""
        analysis = self.analyzer.analyze_job_description(job_description)
        
        matched_bullets = []
        for bullet in bullets:
            score, matched_keywords, reason = self._calculate_relevance(bullet, analysis)
            matched_bullets.append(MatchedBullet(
                bullet=bullet,
                score=score,
                matched_keywords=matched_keywords,
                relevance_reason=reason
            ))
        
        # Sort by relevance score
        matched_bullets.sort(key=lambda x: x.score, reverse=True)
        return matched_bullets
    
    def _calculate_relevance(self, bullet: BulletPoint, analysis: JobAnalysis) -> Tuple[float, List[str], str]:
        """Calculate relevance score for a bullet point"""
        bullet_text_lower = bullet.text.lower()
        score = 0.0
        matched_keywords = []
        
        # Check for skill matches
        for skill in analysis.required_skills:
            if skill in bullet_text_lower:
                score += 2.0
                matched_keywords.append(skill)
        
        # Check for keyword matches
        for keyword in analysis.keywords:
            if keyword in bullet_text_lower:
                score += 1.0
                matched_keywords.append(keyword)
        
        # Check for responsibility matches
        for resp in analysis.responsibilities:
            resp_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resp.lower()))
            bullet_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', bullet_text_lower))
            common_words = resp_words.intersection(bullet_words)
            if len(common_words) > 0:
                score += 0.5 * len(common_words)
                matched_keywords.extend(list(common_words)[:3])
        
        # Normalize score
        score = min(score, 10.0)
        
        # Generate reason
        if matched_keywords:
            reason = f"Matches: {', '.join(set(matched_keywords)[:5])}"
        else:
            reason = "No direct keyword matches found"
        
        return score, list(set(matched_keywords)), reason

# Export the main classes
ResumeTailor = SimpleResumeTailor
BulletPoint = BulletPoint

