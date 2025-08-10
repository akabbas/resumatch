"""
ResuMatch - Smart Resume Generation

A Python-based tool that automatically generates ATS-friendly, visually clean resume PDFs
by analyzing job descriptions and matching them with your experience.
"""

from .resume_generator import ResumeGenerator, KeywordExtractor, ExperienceMatcher
from .resume_generator import JobExperience, Project, ResumeData

__version__ = "1.0.0"
__author__ = "ResuMatch"
__all__ = [
    "ResumeGenerator",
    "KeywordExtractor", 
    "ExperienceMatcher",
    "JobExperience",
    "Project",
    "ResumeData"
] 