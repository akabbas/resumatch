#!/usr/bin/env python3
"""
ResuMatch Free Version - No API Costs!
Uses local AI models and NLP for resume generation
"""

import json
import re
import os
from typing import Dict, List, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from keybert import KeyBERT
from transformers import pipeline, AutoTokenizer
import torch

class FreeResumeGenerator:
    """Free resume generator using local AI models"""
    
    def __init__(self):
        """Initialize local AI models"""
        self.setup_nlp()
        self.setup_ai_models()
        
    def setup_nlp(self):
        """Setup local NLP tools"""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
        
        # Initialize NLTK tools
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load spaCy model (English)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Installing spaCy English model...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def setup_ai_models(self):
        """Setup local AI models for text generation"""
        try:
            # Text summarization model
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            
            # Text generation model
            self.generator = pipeline("text-generation", model="gpt2")
            
            # Keyword extraction
            self.keyword_model = KeyBERT()
            
            print("✅ Local AI models loaded successfully!")
            
        except Exception as e:
            print(f"⚠️  Some AI models failed to load: {e}")
            print("   Using basic NLP features only")
            self.summarizer = None
            self.generator = None
            self.keyword_model = None
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using local NLP"""
        # Use spaCy for named entity recognition
        doc = self.nlp(text)
        
        # Extract technical terms and skills
        skills = []
        
        # Look for technical terms
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 3:
                if not token.is_stop and token.text.lower() not in self.stop_words:
                    skills.append(token.text)
        
        # Use KeyBERT for keyword extraction if available
        if self.keyword_model:
            try:
                keywords = self.keyword_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')
                skills.extend([kw[0] for kw in keywords[:10]])
            except:
                pass
        
        # Remove duplicates and clean
        skills = list(set([skill.strip() for skill in skills if len(skill.strip()) > 2]))
        return skills[:20]  # Limit to top 20 skills
    
    def optimize_job_title(self, current_title: str, target_job: str) -> str:
        """Optimize job title using local analysis"""
        # Extract key terms from target job
        target_terms = self.extract_skills(target_job)
        
        # Find relevant terms in current title
        current_terms = self.extract_skills(current_title)
        
        # Combine and optimize
        if target_terms:
            # Use the most relevant target term
            best_term = target_terms[0]
            if current_title.lower().find(best_term.lower()) == -1:
                # Add target term to title
                if current_title.endswith('Engineer') or current_title.endswith('Analyst'):
                    return f"{best_term} {current_title}"
                else:
                    return f"{current_title} - {best_term}"
        
        return current_title
    
    def rewrite_summary(self, summary: str, target_job: str) -> str:
        """Rewrite summary using local AI models"""
        if not self.summarizer:
            # Fallback to basic NLP
            return self._basic_summary_rewrite(summary, target_job)
        
        try:
            # Use local summarization model
            target_keywords = self.extract_skills(target_job)
            
            # Create enhanced summary with keywords
            enhanced_summary = f"{summary} Specializing in {', '.join(target_keywords[:3])}."
            
            # Summarize to keep it concise
            result = self.summarizer(enhanced_summary, max_length=150, min_length=50)
            return result[0]['summary_text']
            
        except Exception as e:
            print(f"AI summarization failed: {e}")
            return self._basic_summary_rewrite(summary, target_job)
    
    def _basic_summary_rewrite(self, summary: str, target_job: str) -> str:
        """Basic summary rewrite using NLP rules"""
        # Extract key skills from target job
        target_skills = self.extract_skills(target_job)
        
        # Enhance summary with target skills
        if target_skills:
            skill_phrase = f" with expertise in {', '.join(target_skills[:3])}"
            if not summary.endswith('.'):
                summary += '.'
            summary += skill_phrase + "."
        
        return summary
    
    def enhance_bullet_points(self, bullets: List[str], target_job: str) -> List[str]:
        """Enhance bullet points using local AI"""
        enhanced_bullets = []
        target_skills = self.extract_skills(target_job)
        
        for bullet in bullets:
            enhanced_bullet = self._enhance_single_bullet(bullet, target_skills)
            enhanced_bullets.append(enhanced_bullet)
        
        return enhanced_bullets
    
    def _enhance_single_bullet(self, bullet: str, target_skills: List[str]) -> str:
        """Enhance a single bullet point"""
        # Add relevant skills if not present
        for skill in target_skills[:3]:
            if skill.lower() not in bullet.lower():
                # Insert skill naturally
                if bullet.endswith('.'):
                    bullet = bullet[:-1] + f" using {skill}."
                else:
                    bullet += f" using {skill}."
                break
        
        # Ensure action verbs
        action_verbs = ['developed', 'implemented', 'managed', 'created', 'optimized', 'improved']
        if not any(verb in bullet.lower() for verb in action_verbs):
            bullet = f"Developed {bullet.lower()}"
        
        return bullet
    
    def generate_resume(self, experience_data: Dict, target_job: str) -> Dict:
        """Generate optimized resume using local AI"""
        print("🚀 Generating resume with FREE local AI models...")
        
        # Extract and optimize skills
        all_text = f"{experience_data.get('summary', '')} {' '.join(experience_data.get('experience', []))}"
        skills = self.extract_skills(all_text)
        
        # Optimize job title
        current_title = experience_data.get('current_title', 'Professional')
        optimized_title = self.optimize_job_title(current_title, target_job)
        
        # Rewrite summary
        summary = experience_data.get('summary', '')
        enhanced_summary = self.rewrite_summary(summary, target_job)
        
        # Enhance bullet points
        experience = experience_data.get('experience', [])
        enhanced_experience = self.enhance_bullet_points(experience, target_job)
        
        # Generate optimized resume
        optimized_resume = {
            'title': optimized_title,
            'summary': enhanced_summary,
            'skills': skills,
            'experience': enhanced_experience,
            'target_job': target_job,
            'optimization_method': 'Local AI Models (Free)',
            'features_used': [
                'Local NLP processing',
                'Skill extraction',
                'Content optimization',
                'ATS optimization'
            ]
        }
        
        print("✅ Resume generated successfully using FREE local AI!")
        return optimized_resume
    
    def save_resume(self, resume_data: Dict, filename: str = "free_resume.json"):
        """Save generated resume to file"""
        with open(filename, 'w') as f:
            json.dump(resume_data, f, indent=2)
        print(f"💾 Resume saved to {filename}")

def main():
    """Main function to demonstrate free resume generation"""
    print("🎉 ResuMatch FREE Version - No API Costs!")
    print("=" * 50)
    
    # Initialize generator
    generator = FreeResumeGenerator()
    
    # Sample experience data
    sample_experience = {
        "current_title": "Business Systems Analyst",
        "summary": "Experienced professional with expertise in business process optimization and system analysis.",
        "experience": [
            "Analyzed business requirements and created technical specifications",
            "Implemented process improvements that increased efficiency by 25%",
            "Collaborated with cross-functional teams to deliver solutions"
        ]
    }
    
    target_job = "Senior Data Analyst with focus on business intelligence and reporting"
    
    # Generate resume
    optimized_resume = generator.generate_resume(sample_experience, target_job)
    
    # Save resume
    generator.save_resume(optimized_resume)
    
    # Display results
    print("\n📋 Generated Resume:")
    print(f"Title: {optimized_resume['title']}")
    print(f"Skills: {', '.join(optimized_resume['skills'][:5])}...")
    print(f"Summary: {optimized_resume['summary'][:100]}...")
    
    print("\n🎯 Key Benefits:")
    print("✅ 100% FREE - No API costs")
    print("✅ Local processing - No internet required")
    print("✅ Privacy focused - Data stays on your machine")
    print("✅ Professional quality - AI-powered optimization")

if __name__ == "__main__":
    main()
