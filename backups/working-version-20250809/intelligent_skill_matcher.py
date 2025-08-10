import json
import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class IntelligentSkillMatcher:
    """
    Intelligent skill matching system that analyzes job descriptions
    and selects the most relevant skills from a comprehensive database.
    """
    
    def __init__(self, skills_database_path: str = "comprehensive_skills_database.json"):
        """Initialize the skill matcher with the comprehensive skills database."""
        self.skills_database = self._load_skills_database(skills_database_path)
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
    
    def _load_skills_database(self, path: str) -> Dict:
        """Load the comprehensive skills database."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Skills database not found at {path}")
            return {"master_skills_database": {}, "skill_categories": {}, "skill_levels": {}}
    
    def _extract_job_keywords(self, job_description: str) -> Set[str]:
        """Extract relevant keywords from job description."""
        # Convert to lowercase and tokenize
        tokens = word_tokenize(job_description.lower())
        
        # Remove stopwords and lemmatize
        stop_words = set(stopwords.words('english'))
        keywords = set()
        
        for token in tokens:
            if token.isalnum() and token not in stop_words and len(token) > 2:
                lemmatized = self.lemmatizer.lemmatize(token)
                keywords.add(lemmatized)
                keywords.add(token)  # Keep original form too
        
        return keywords
    
    def _calculate_skill_relevance_score(self, skill_info: Dict, job_keywords: Set[str], 
                                       job_description: str) -> float:
        """Calculate how relevant a skill is to the job description."""
        score = 0.0
        
        # Check each variation of the skill
        for variation in skill_info.get('variations', []):
            variation_lower = variation.lower()
            
            # Direct keyword match
            if variation_lower in job_keywords:
                score += 10.0
            
            # Partial keyword match
            for keyword in job_keywords:
                if keyword in variation_lower or variation_lower in keyword:
                    score += 5.0
            
            # Check if skill appears in job description
            if variation.lower() in job_description.lower():
                score += 8.0
            
            # Check for related terms
            skill_words = set(variation_lower.split())
            for word in skill_words:
                if word in job_keywords:
                    score += 3.0
        
        # Bonus for skill level (expert skills get higher scores)
        skill_level = skill_info.get('skill_level', 'intermediate')
        level_bonus = {'expert': 3, 'intermediate': 2, 'beginner': 1}
        score += level_bonus.get(skill_level, 1)
        
        # Bonus for category relevance
        categories = skill_info.get('categories', [])
        for category in categories:
            if category in job_description.lower():
                score += 2.0
        
        return score
    
    def _identify_job_category(self, job_description: str) -> List[str]:
        """Identify the primary job categories based on the description."""
        job_lower = job_description.lower()
        categories = []
        
        # Technical roles
        if any(term in job_lower for term in ['developer', 'engineer', 'programmer', 'coding']):
            categories.append('technical')
        
        if any(term in job_lower for term in ['frontend', 'ui', 'ux', 'react', 'angular', 'vue']):
            categories.append('frontend')
        
        if any(term in job_lower for term in ['backend', 'api', 'server', 'database']):
            categories.append('backend')
        
        if any(term in job_lower for term in ['full stack', 'fullstack', 'full-stack']):
            categories.append('full_stack')
        
        # Data roles
        if any(term in job_lower for term in ['data', 'analytics', 'bi', 'business intelligence']):
            categories.append('data_science')
        
        # Business roles
        if any(term in job_lower for term in ['business', 'analyst', 'operations', 'salesforce', 'crm']):
            categories.append('business')
        
        # DevOps/Cloud roles
        if any(term in job_lower for term in ['devops', 'cloud', 'aws', 'azure', 'infrastructure']):
            categories.append('cloud_infrastructure')
        
        # Enterprise roles
        if any(term in job_lower for term in ['enterprise', 'erp', 'sap', 'oracle']):
            categories.append('enterprise')
        
        return categories if categories else ['technical']
    
    def _get_priority_skills_for_category(self, category: str) -> List[str]:
        """Get priority skills for a specific job category."""
        category_mappings = {
            'technical': ['python', 'javascript', 'sql', 'git', 'agile'],
            'frontend': ['javascript', 'react', 'html_css', 'ui_ux', 'responsive_design'],
            'backend': ['python', 'sql', 'node', 'rest_api', 'databases'],
            'full_stack': ['python', 'javascript', 'react', 'node', 'sql', 'aws'],
            'data_science': ['python', 'sql', 'data_analysis', 'excel', 'dashboards'],
            'business': ['salesforce', 'oracle_cpq', 'business_analysis', 'stakeholder_management'],
            'cloud_infrastructure': ['aws', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'enterprise': ['salesforce', 'oracle_cpq', 'jd_edwards', 'sap', 'business_analysis']
        }
        return category_mappings.get(category, [])
    
    def select_relevant_skills(self, job_description: str, max_skills: int = 15) -> List[str]:
        """
        Select the most relevant skills for a specific job description.
        
        Args:
            job_description: The job description text
            max_skills: Maximum number of skills to return
            
        Returns:
            List of skill names ordered by relevance
        """
        # Extract keywords from job description
        job_keywords = self._extract_job_keywords(job_description)
        
        # Identify job categories
        job_categories = self._identify_job_category(job_description)
        
        # Score all skills
        skill_scores = []
        master_db = self.skills_database.get('master_skills_database', {})
        
        for category, skills in master_db.items():
            for skill_key, skill_info in skills.items():
                score = self._calculate_skill_relevance_score(skill_info, job_keywords, job_description)
                
                # Bonus for skills in relevant job categories
                if any(cat in job_categories for cat in skill_info.get('categories', [])):
                    score += 5.0
                
                # Bonus for priority skills in the identified category
                for job_cat in job_categories:
                    priority_skills = self._get_priority_skills_for_category(job_cat)
                    if skill_key in priority_skills:
                        score += 10.0
                
                # Add all variations with their scores
                for variation in skill_info.get('variations', []):
                    skill_scores.append((variation, score, skill_info.get('skill_level', 'intermediate')))
        
        # Sort by score (highest first) and remove duplicates
        skill_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill, score, level in skill_scores:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        # Return top skills
        return unique_skills[:max_skills]
    
    def get_skill_details(self, skill_name: str) -> Dict:
        """Get detailed information about a specific skill."""
        master_db = self.skills_database.get('master_skills_database', {})
        
        for category, skills in master_db.items():
            for skill_key, skill_info in skills.items():
                if skill_name in skill_info.get('variations', []):
                    return {
                        'name': skill_name,
                        'category': category,
                        'skill_key': skill_key,
                        'skill_level': skill_info.get('skill_level', 'intermediate'),
                        'categories': skill_info.get('categories', []),
                        'all_variations': skill_info.get('variations', [])
                    }
        
        return None
    
    def analyze_job_requirements(self, job_description: str) -> Dict:
        """
        Analyze job requirements and provide insights.
        
        Returns:
            Dictionary with analysis results
        """
        job_keywords = self._extract_job_keywords(job_description)
        job_categories = self._identify_job_category(job_description)
        relevant_skills = self.select_relevant_skills(job_description, max_skills=20)
        
        return {
            'extracted_keywords': list(job_keywords),
            'identified_categories': job_categories,
            'top_relevant_skills': relevant_skills,
            'skill_count': len(relevant_skills),
            'analysis_summary': f"Job requires {len(relevant_skills)} relevant skills across {len(job_categories)} categories"
        }
    
    def get_skill_categories_summary(self) -> Dict:
        """Get a summary of all available skill categories."""
        return self.skills_database.get('skill_categories', {})
    
    def search_skills_by_category(self, category: str) -> List[str]:
        """Get all skills in a specific category."""
        master_db = self.skills_database.get('master_skills_database', {})
        skills = []
        
        for skill_category, skills_dict in master_db.items():
            if category.lower() in skill_category.lower():
                for skill_key, skill_info in skills_dict.items():
                    skills.extend(skill_info.get('variations', []))
        
        return skills
    
    def get_expert_skills(self) -> List[str]:
        """Get all skills marked as expert level."""
        master_db = self.skills_database.get('master_skills_database', {})
        expert_skills = []
        
        for category, skills in master_db.items():
            for skill_key, skill_info in skills.items():
                if skill_info.get('skill_level') == 'expert':
                    expert_skills.extend(skill_info.get('variations', []))
        
        return expert_skills


# Example usage and testing
if __name__ == "__main__":
    # Initialize the skill matcher
    matcher = IntelligentSkillMatcher()
    
    # Example job description
    sample_job = """
    Senior Python Developer
    
    We are looking for a Senior Python Developer to join our dynamic team. 
    You will be responsible for developing and maintaining high-quality software solutions.
    
    Requirements:
    - 5+ years of experience with Python development
    - Strong experience with Django and FastAPI
    - Experience with PostgreSQL and MySQL databases
    - Knowledge of AWS cloud services
    - Experience with Docker and CI/CD pipelines
    - Understanding of REST APIs and microservices architecture
    """
    
    # Get relevant skills
    relevant_skills = matcher.select_relevant_skills(sample_job, max_skills=10)
    print("Top 10 relevant skills for this job:")
    for i, skill in enumerate(relevant_skills, 1):
        print(f"{i}. {skill}")
    
    # Analyze job requirements
    analysis = matcher.analyze_job_requirements(sample_job)
    print(f"\nJob Analysis: {analysis['analysis_summary']}")
    print(f"Identified categories: {analysis['identified_categories']}") 