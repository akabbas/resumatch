#!/usr/bin/env python3
"""
Setup script for ATS Resume Generator
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "ATS-Friendly Resume Generator"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="resumatch",
    version="1.0.0",
    author="ResuMatch",
    author_email="your.email@example.com",
    description="Smart resume generation that matches your experience to job descriptions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/resumatch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ats-resume=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="resume, ats, pdf, job, application, nlp, keyword-extraction, matching",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/resumatch/issues",
        "Source": "https://github.com/yourusername/resumatch",
        "Documentation": "https://github.com/yourusername/resumatch#readme",
    },
) 