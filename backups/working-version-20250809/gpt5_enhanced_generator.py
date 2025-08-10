#!/usr/bin/env python3
"""
GPT-5 Enhanced Resume Generator
Advanced AI-powered resume generation with GPT-5 features
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import openai
import anthropic
import cohere
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: transformers not available: {e}")
    TRANSFORMERS_AVAILABLE = False
    pipeline = None
import torch
from resume_generator import ResumeGenerator, JobExperience, Project, ResumeData

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class GPT5Config:
    """Configuration for GPT-5 enhanced features"""
    openai_api_key: str
    anthropic_api_key: str = None
    cohere_api_key: str = None
    model: str = "gpt-5"
    max_tokens: int = 4000
    temperature: float = 0.7
    enable_multi_model: bool = True
    enable_langchain: bool = True

class GPT5EnhancedGenerator(ResumeGenerator):
    """Enhanced resume generator with GPT-5 features"""
    
    def __init__(self, gpt5_config: GPT5Config, **kwargs):
        super().__init__(**kwargs)
        self.gpt5_config = gpt5_config
        self.setup_ai_models()
        
    def setup_ai_models(self):
        """Initialize AI models for GPT-5 features"""
        try:
            # OpenAI setup
            openai.api_key = self.gpt5_config.openai_api_key
            
            # LangChain setup
            if self.gpt5_config.enable_langchain:
                self.llm = OpenAI(
                    api_key=self.gpt5_config.openai_api_key,
                    model_name=self.gpt5_config.model,
                    temperature=self.gpt5_config.temperature,
                    max_tokens=self.gpt5_config.max_tokens
                )
            
            # Multi-model setup
            if self.gpt5_config.enable_multi_model:
                if self.gpt5_config.anthropic_api_key:
                    self.anthropic_client = anthropic.Anthropic(
                        api_key=self.gpt5_config.anthropic_api_key
                    )
                
                if self.gpt5_config.cohere_api_key:
                    self.cohere_client = cohere.Client(self.gpt5_config.cohere_api_key)
            
            # Local models for specific tasks - lazy loading to avoid PyTorch meta tensor issues
            self.sentiment_analyzer = None
            self.text_classifier = None
            
            logger.info("GPT-5 enhanced features initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPT-5 features: {e}")
            raise
    
    def _get_sentiment_analyzer(self):
        """Lazily load sentiment analyzer to avoid PyTorch meta tensor issues"""
        if not TRANSFORMERS_AVAILABLE or pipeline is None:
            return None
        if self.sentiment_analyzer is None:
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis", device=-1)  # Force CPU
            except Exception as e:
                logger.warning(f"Failed to load sentiment analyzer: {e}")
                self.sentiment_analyzer = None
        return self.sentiment_analyzer
    
    def _get_text_classifier(self):
        """Lazily load text classifier to avoid PyTorch meta tensor issues"""
        if not TRANSFORMERS_AVAILABLE or pipeline is None:
            return None
        if self.text_classifier is None:
            try:
                self.text_classifier = pipeline("text-classification", device=-1)  # Force CPU
            except Exception as e:
                logger.warning(f"Failed to load text classifier: {e}")
                self.text_classifier = None
        return self.text_classifier
    
    def generate_advanced_summary(self, job_description: str, experience: List[JobExperience]) -> str:
        """Generate advanced summary using GPT-5"""
        try:
            prompt = f"""
            Create a compelling professional summary for a resume targeting this job:
            
            Job Description:
            {job_description}
            
            Experience:
            {self._format_experience_for_prompt(experience)}
            
            Requirements:
            - 3-4 sentences maximum
            - Quantify achievements where possible
            - Match job requirements precisely
            - Professional tone
            - ATS-friendly
            - Include specific metrics and results
            - Use industry-specific terminology
            - Highlight transferable skills
            """
            
            response = openai.ChatCompletion.create(
                model=self.gpt5_config.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer with deep knowledge of ATS optimization and professional writing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.gpt5_config.max_tokens,
                temperature=self.gpt5_config.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating advanced summary: {e}")
            return self._fallback_summary_generation(job_description, experience)
    
    def enhance_bullet_points_gpt5(self, bullets: List[str], job_description: str) -> List[str]:
        """Enhance bullet points using GPT-5 with advanced analysis"""
        try:
            # Analyze job requirements first
            job_analysis = self._analyze_job_requirements_gpt5(job_description)
            
            enhanced_bullets = []
            for bullet in bullets:
                enhanced_bullet = self._enhance_single_bullet_gpt5(bullet, job_analysis)
                enhanced_bullets.append(enhanced_bullet)
            
            return enhanced_bullets
            
        except Exception as e:
            logger.error(f"Error enhancing bullet points: {e}")
            return bullets
    
    def _analyze_job_requirements_gpt5(self, job_description: str) -> Dict:
        """Advanced job analysis using GPT-5"""
        try:
            prompt = f"""
            Analyze this job description and extract:
            1. Required technical skills (programming languages, tools, frameworks)
            2. Required soft skills (leadership, communication, etc.)
            3. Experience level needed
            4. Industry context
            5. Key responsibilities
            6. Growth opportunities
            7. Company culture indicators
            8. Salary range indicators
            9. Remote/hybrid preferences
            10. Required certifications
            
            Job Description:
            {job_description}
            
            Return as JSON format.
            """
            
            response = openai.ChatCompletion.create(
                model=self.gpt5_config.model,
                messages=[
                    {"role": "system", "content": "You are an expert job analyst and career advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing job requirements: {e}")
            return {}
    
    def _enhance_single_bullet_gpt5(self, bullet: str, job_analysis: Dict) -> str:
        """Enhance a single bullet point using GPT-5"""
        try:
            prompt = f"""
            Transform this resume bullet point to be more compelling and job-specific:
            
            Original Bullet: {bullet}
            
            Job Analysis: {json.dumps(job_analysis, indent=2)}
            
            Requirements:
            - Add quantifiable metrics where possible
            - Use strong action verbs
            - Match job requirements
            - Keep under 2 lines
            - ATS-optimized
            - Include specific technologies if relevant
            - Show impact and results
            """
            
            response = openai.ChatCompletion.create(
                model=self.gpt5_config.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer specializing in ATS optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error enhancing bullet point: {e}")
            return bullet
    
    def generate_intelligent_career_advice(self, resume_data: ResumeData, job_description: str) -> Dict:
        """Generate intelligent career advice using GPT-5"""
        try:
            prompt = f"""
            Based on this resume and job description, provide comprehensive career advice:
            
            Resume Summary: {resume_data.summary}
            Experience: {self._format_experience_for_prompt(resume_data.experience)}
            Skills: {', '.join(resume_data.skills)}
            
            Job Description: {job_description}
            
            Provide advice on:
            1. Skill gaps to address
            2. Experience highlights to emphasize
            3. Interview preparation tips
            4. Career trajectory suggestions
            5. Networking opportunities
            6. Salary negotiation tips
            7. Professional development recommendations
            8. Industry trends to consider
            
            Return as JSON format.
            """
            
            response = openai.ChatCompletion.create(
                model=self.gpt5_config.model,
                messages=[
                    {"role": "system", "content": "You are an expert career advisor and resume consultant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating career advice: {e}")
            return {"error": "Unable to generate career advice"}
    
    def optimize_job_titles_gpt5(self, resume_data: ResumeData, job_description: str) -> ResumeData:
        """Advanced job title optimization using GPT-5"""
        try:
            job_analysis = self._analyze_job_requirements_gpt5(job_description)
            
            optimized_experience = []
            for exp in resume_data.experience:
                optimized_title = self._optimize_job_title_gpt5(exp.title, exp.description, job_analysis)
                optimized_experience.append(JobExperience(
                    title=optimized_title,
                    company=exp.company,
                    duration=exp.duration,
                    description=exp.description,
                    skills_used=exp.skills_used
                ))
            
            resume_data.experience = optimized_experience
            return resume_data
            
        except Exception as e:
            logger.error(f"Error optimizing job titles: {e}")
            return resume_data
    
    def _optimize_job_title_gpt5(self, current_title: str, description: Union[str, List[str]], job_analysis: Dict) -> str:
        """Optimize a single job title using GPT-5"""
        try:
            desc_text = description if isinstance(description, str) else ' '.join(description)
            
            prompt = f"""
            Optimize this job title to better match the target job requirements:
            
            Current Title: {current_title}
            Job Description: {desc_text}
            
            Job Analysis: {json.dumps(job_analysis, indent=2)}
            
            Requirements:
            - Keep it truthful and accurate
            - Use industry-standard terminology
            - Match job requirements
            - Maintain professional level
            - Be specific but not misleading
            """
            
            response = openai.ChatCompletion.create(
                model=self.gpt5_config.model,
                messages=[
                    {"role": "system", "content": "You are an expert in job title optimization and career branding."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error optimizing job title: {e}")
            return current_title
    
    def _format_experience_for_prompt(self, experience: List[JobExperience]) -> str:
        """Format experience for GPT-5 prompts"""
        formatted = []
        for exp in experience:
            desc = exp.description if isinstance(exp.description, str) else ' '.join(exp.description)
            formatted.append(f"{exp.title} at {exp.company} ({exp.duration}): {desc}")
        return '\n'.join(formatted)
    
    def _fallback_summary_generation(self, job_description: str, experience: List[JobExperience]) -> str:
        """Fallback summary generation if GPT-5 fails"""
        return super()._optimize_summary(ResumeData(
            summary="Experienced professional with strong technical skills.",
            experience=experience,
            skills=[]
        ), job_description, []).summary
    
    def generate_resume_with_gpt5(self, job_description: str, experience_data: Union[str, Dict], 
                                 output_path: str, name: str = "Your Name", 
                                 contact_info: str = "email@example.com | phone | location") -> str:
        """Generate resume with GPT-5 enhanced features"""
        try:
            # Parse experience data
            resume_data = self.parse_experience_data(experience_data)
            
            # Apply GPT-5 enhancements
            if self.gpt5_config.enable_multi_model:
                # Advanced summary generation
                resume_data.summary = self.generate_advanced_summary(job_description, resume_data.experience)
                
                # Enhanced bullet points
                for exp in resume_data.experience:
                    if isinstance(exp.description, list):
                        exp.description = self.enhance_bullet_points_gpt5(exp.description, job_description)
                
                # Optimize job titles
                resume_data = self.optimize_job_titles_gpt5(resume_data, job_description)
            
            # Generate the resume
            return super().generate_resume(job_description, experience_data, output_path, name, contact_info)
            
        except Exception as e:
            logger.error(f"Error in GPT-5 enhanced resume generation: {e}")
            # Fallback to standard generation
            return super().generate_resume(job_description, experience_data, output_path, name, contact_info)

def create_gpt5_config() -> GPT5Config:
    """Create GPT-5 configuration from environment variables"""
    return GPT5Config(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
        cohere_api_key=os.getenv('COHERE_API_KEY'),
        model=os.getenv('OPENAI_MODEL', 'gpt-5'),
        max_tokens=int(os.getenv('MAX_TOKENS', '4000')),
        temperature=float(os.getenv('TEMPERATURE', '0.7')),
        enable_multi_model=os.getenv('ENABLE_MULTI_MODEL_AI', 'True').lower() == 'true',
        enable_langchain=os.getenv('ENABLE_LANGCHAIN_INTEGRATION', 'True').lower() == 'true'
    )
