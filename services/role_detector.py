#!/usr/bin/env python3
"""
Enhanced Role Detector Utility
Implements a two-tier detection system for accurate role identification
"""

import re
import json
import os
from typing import Dict, List, Optional, Tuple, Any

class EnhancedRoleDetector:
    """
    Enhanced role detector with two-tier detection system:
    1. Strong job title pattern matching
    2. Fallback to skill-based matching
    """
    
    def __init__(self, skills_mapping_path: str = "data/skills_mapping.json"):
        """
        Initialize the EnhancedRoleDetector with skills mapping data
        
        Args:
            skills_mapping_path (str): Path to the skills mapping JSON file
        """
        self.skills_mapping_path = skills_mapping_path
        self.role_keywords = self._build_role_keywords()
        self.role_priority = self._build_role_priority()
        self.job_title_patterns = self._build_job_title_patterns()
        
    def _build_job_title_patterns(self) -> Dict[str, List[Tuple[str, float]]]:
        """
        Build strong job title patterns with confidence scores
        
        Returns:
            Dict[str, List[Tuple[str, float]]]: Role to (pattern, confidence) mappings
        """
        patterns = {
            # Software Engineering Roles
            "Software Engineer": [
                (r"\b(?:senior\s+)?software\s+engineer\b", 0.95),
                (r"\b(?:senior\s+)?(?:python|java|javascript|typescript|go|rust|c\+\+|c#)\s+(?:developer|engineer|programmer)\b", 0.95),
                (r"\b(?:senior\s+)?(?:full\s+stack|fullstack)\s+(?:developer|engineer)\b", 0.95),
                (r"\b(?:senior\s+)?(?:backend|frontend|web)\s+(?:developer|engineer)\b", 0.90),
                (r"\b(?:senior\s+)?(?:software|application)\s+(?:developer|engineer|programmer)\b", 0.85),
                (r"\b(?:senior\s+)?(?:mobile|ios|android)\s+(?:developer|engineer)\b", 0.90),
                (r"\b(?:senior\s+)?(?:game|gaming)\s+(?:developer|engineer|programmer)\b", 0.90),
            ],
            
            # Data Science Roles
            "Data Scientist": [
                (r"\b(?:senior\s+)?(?:data\s+)?scientist\b", 0.95),
                (r"\b(?:senior\s+)?(?:research)\s+(?:scientist|engineer)\b", 0.85),
                (r"\b(?:senior\s+)?(?:machine\s+learning|ml)\s+(?:scientist|researcher)\b", 0.90),
                (r"\b(?:senior\s+)?(?:ai|artificial\s+intelligence)\s+(?:scientist|researcher)\b", 0.90),
                (r"\b(?:senior\s+)?(?:statistical)\s+(?:scientist|analyst)\b", 0.85),
                (r"\b(?:senior\s+)?(?:quantitative)\s+(?:scientist|analyst)\b", 0.85),
                (r"\b(?:senior\s+)?(?:predictive)\s+(?:analytics|modeling)\s+(?:scientist|specialist)\b", 0.90),
                (r"\b(?:senior\s+)?(?:data\s+)?science\s+(?:specialist|professional)\b", 0.85),
            ],
            
            # Machine Learning Engineering Roles
            "Machine Learning Engineer": [
                (r"\b(?:senior\s+)?(?:machine\s+learning|ml)\s+(?:engineer|specialist)\b", 0.95),
                (r"\b(?:senior\s+)?(?:ai|artificial\s+intelligence)\s+(?:engineer|specialist)\b", 0.95),
                (r"\b(?:senior\s+)?(?:mlops|machine\s+learning\s+operations)\s+(?:engineer|specialist)\b", 0.95),
            ],
            
            # DevOps/Infrastructure Roles
            "DevOps Engineer": [
                (r"\b(?:senior\s+)?devops\s+engineer\b", 0.95),
                (r"\b(?:senior\s+)?(?:devops|dev\s+ops)\s+(?:engineer|specialist)\b", 0.95),
                (r"\b(?:senior\s+)?(?:site\s+reliability|sre)\s+(?:engineer|specialist)\b", 0.95),
                (r"\b(?:senior\s+)?(?:platform)\s+(?:engineer|specialist)\b", 0.90),
                (r"\b(?:senior\s+)?(?:infrastructure)\s+(?:engineer|specialist)\b", 0.90),
            ],
            
            # Cloud Engineering Roles
            "Cloud Engineer": [
                (r"\b(?:senior\s+)?(?:cloud)\s+(?:engineer|architect|specialist)\b", 0.95),
                (r"\b(?:senior\s+)?(?:aws|azure|gcp)\s+(?:engineer|architect|specialist)\b", 0.95),
                (r"\b(?:senior\s+)?(?:kubernetes|k8s)\s+(?:engineer|specialist)\b", 0.90),
            ],
            
            # Data Engineering Roles
            "Data Engineer": [
                (r"\b(?:senior\s+)?(?:data)\s+(?:engineer|architect)\b", 0.95),
                (r"\b(?:senior\s+)?(?:etl|data\s+pipeline)\s+(?:engineer|specialist)\b", 0.90),
                (r"\b(?:senior\s+)?(?:data\s+warehouse|analytics)\s+(?:engineer|specialist)\b", 0.90),
            ],
            
            # Business/Product Roles
            "Product Manager": [
                (r"\b(?:senior\s+)?product\s+manager\b", 0.95),
                (r"\b(?:senior\s+)?(?:product)\s+(?:manager|owner|lead)\b", 0.95),
                (r"\b(?:senior\s+)?(?:technical\s+product)\s+(?:manager|owner)\b", 0.95),
                (r"\b(?:senior\s+)?(?:program)\s+(?:manager|lead)\b", 0.85),
            ],
            
            "Business Analyst": [
                (r"\b(?:senior\s+)?(?:business)\s+(?:analyst|consultant)\b", 0.95),
                (r"\b(?:senior\s+)?(?:systems)\s+(?:analyst|consultant)\b", 0.90),
                (r"\b(?:senior\s+)?(?:process)\s+(?:analyst|consultant)\b", 0.85),
            ],
            
            # Project Management Roles
            "Project Manager": [
                (r"\b(?:senior\s+)?(?:project)\s+(?:manager|lead|coordinator)\b", 0.95),
                (r"\b(?:senior\s+)?(?:scrum)\s+(?:master|lead)\b", 0.90),
                (r"\b(?:senior\s+)?(?:agile)\s+(?:coach|lead)\b", 0.85),
            ],
            
            # Security Roles
            "Security Engineer": [
                (r"\b(?:senior\s+)?(?:security|cybersecurity)\s+(?:engineer|specialist|analyst)\b", 0.95),
                (r"\b(?:senior\s+)?(?:information\s+security|infosec)\s+(?:engineer|specialist)\b", 0.95),
                (r"\b(?:senior\s+)?(?:application\s+security)\s+(?:engineer|specialist)\b", 0.90),
            ],
            
            # Salesforce/CRM Roles
            "Salesforce Administrator": [
                (r"\b(?:senior\s+)?(?:salesforce)\s+(?:administrator|admin|developer)\b", 0.95),
                (r"\b(?:senior\s+)?(?:crm)\s+(?:administrator|admin|specialist)\b", 0.90),
                (r"\b(?:senior\s+)?(?:cpq)\s+(?:developer|specialist)\b", 0.90),
            ],
            
            # QA/Testing Roles
            "QA Engineer": [
                (r"\b(?:senior\s+)?(?:qa|quality\s+assurance)\s+(?:engineer|specialist|tester)\b", 0.95),
                (r"\b(?:senior\s+)?(?:test)\s+(?:engineer|specialist|automation)\b", 0.95),
                (r"\b(?:senior\s+)?(?:automation)\s+(?:engineer|specialist)\b", 0.90),
            ],
        }
        
        return patterns
    
    def _build_role_keywords(self) -> Dict[str, List[str]]:
        """
        Build a mapping of roles to their identifying keywords
        
        Returns:
            Dict[str, List[str]]: Role to keywords mapping
        """
        try:
            # Get the absolute path relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            full_path = os.path.join(project_root, self.skills_mapping_path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                skills_mapping = json.load(f)
            
            # Extract all unique roles from the skills mapping
            all_roles = set()
            for skill_mappings in skills_mapping.values():
                all_roles.update(skill_mappings.keys())
            
            # Build keyword mappings for each role
            role_keywords = {}
            
            for role in all_roles:
                role_lower = role.lower()
                keywords = []
                
                # Extract key words from role name
                words = role_lower.split()
                keywords.extend(words)
                
                # Add common variations and abbreviations
                if 'engineer' in role_lower:
                    keywords.extend(['engineering', 'technical', 'development'])
                if 'developer' in role_lower:
                    keywords.extend(['development', 'coding', 'programming'])
                if 'analyst' in role_lower:
                    keywords.extend(['analysis', 'analytics', 'business'])
                if 'manager' in role_lower:
                    keywords.extend(['management', 'leadership', 'strategy'])
                if 'scientist' in role_lower:
                    keywords.extend(['science', 'research', 'data'])
                    # Add specific Data Scientist keywords
                    if 'data' in role_lower:
                        keywords.extend(['machine learning', 'ml', 'ai', 'artificial intelligence', 'statistics', 'python', 'r', 'matlab', 'predictive analytics', 'data visualization', 'sql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'])
                if 'administrator' in role_lower:
                    keywords.extend(['administration', 'admin', 'management'])
                if 'devops' in role_lower:
                    keywords.extend(['devops', 'operations', 'infrastructure'])
                if 'cloud' in role_lower:
                    keywords.extend(['cloud', 'aws', 'azure', 'gcp'])
                if 'security' in role_lower:
                    keywords.extend(['security', 'cybersecurity', 'infosec'])
                if 'ai' in role_lower or 'ml' in role_lower:
                    keywords.extend(['ai', 'ml', 'machine learning', 'artificial intelligence'])
                if 'data' in role_lower:
                    keywords.extend(['data', 'analytics', 'database'])
                if 'frontend' in role_lower:
                    keywords.extend(['frontend', 'ui', 'ux', 'user interface'])
                if 'backend' in role_lower:
                    keywords.extend(['backend', 'api', 'server'])
                if 'full stack' in role_lower:
                    keywords.extend(['full stack', 'fullstack', 'end-to-end'])
                
                role_keywords[role] = list(set(keywords))  # Remove duplicates
            
            return role_keywords
            
        except Exception as e:
            print(f"Warning: Could not load skills mapping for role detection: {e}")
            return {}
    
    def _build_role_priority(self) -> Dict[str, int]:
        """
        Build role priority scores for better role selection
        
        Returns:
            Dict[str, int]: Role to priority score mapping
        """
        priority_scores = {}
        
        for role in self.role_keywords.keys():
            role_lower = role.lower()
            score = 0
            
            # Higher priority for more specific roles
            if 'senior' in role_lower or 'lead' in role_lower or 'principal' in role_lower:
                score += 10
            if 'architect' in role_lower:
                score += 8
            if 'engineer' in role_lower:
                score += 6
            if 'developer' in role_lower:
                score += 5
            if 'analyst' in role_lower:
                score += 4
            if 'manager' in role_lower:
                score += 3
            if 'specialist' in role_lower:
                score += 2
            
            # Priority for emerging/trending roles
            if any(word in role_lower for word in ['ai', 'ml', 'machine learning', 'data science']):
                score += 5
            if any(word in role_lower for word in ['devops', 'cloud', 'security']):
                score += 4
            
            priority_scores[role] = score
        
        return priority_scores
    
    def detect_role(self, job_description: str) -> Dict[str, Any]:
        """
        Enhanced role detection using two-tier system
        
        Args:
            job_description (str): Job description text to analyze
            
        Returns:
            Dict[str, Any]: Dictionary with detected role and confidence
        """
        if not self.job_title_patterns:
            return {
                'target_role': 'Software Engineer',
                'role_confidence': 0.0,
                'detection_method': 'fallback'
            }
        
        # Extract job title from the beginning of the description
        job_title = self._extract_job_title(job_description)
        
        # Tier 1: Strong job title pattern matching
        title_match = self._match_job_title_patterns(job_title, job_description)
        if title_match:
            role, confidence = title_match
            print(f"🎯 Strong title match detected: {role} (confidence: {confidence:.2f})")
            return {
                'target_role': role,
                'role_confidence': confidence,
                'detection_method': 'title_pattern'
            }
        
        # Tier 2: Fallback to skill-based matching
        print(f"🔄 No strong title match, falling back to skill-based detection")
        role, confidence = self._fallback_skill_based_detection(job_description)
        return {
            'target_role': role,
            'role_confidence': confidence,
            'detection_method': 'skill_based'
        }
    
    def _extract_job_title(self, job_description: str) -> str:
        """
        Extract job title from the beginning of the job description
        
        Args:
            job_description (str): Full job description
            
        Returns:
            str: Extracted job title
        """
        # Look for job title in the first sentence/line
        lines = job_description.strip().split('\n')
        
        # Check first line specifically
        first_line = lines[0].strip() if lines else ""
        
        if first_line:
            # Remove common prefixes
            cleaned_title = re.sub(r'^(?:We are seeking|Looking for|Seeking|Hiring|Position:?|Role:?|Title:?)\s*', '', first_line, flags=re.IGNORECASE)
            cleaned_title = cleaned_title.strip()
            
            # If the first line looks like a job title (not too long, contains role keywords)
            if cleaned_title and len(cleaned_title) < 100:
                # Check if it contains common role keywords
                role_keywords = ['engineer', 'developer', 'manager', 'analyst', 'scientist', 'administrator', 'lead', 'director', 'specialist']
                if any(keyword in cleaned_title.lower() for keyword in role_keywords):
                    return cleaned_title
        
        # Fallback: look for patterns in the first few sentences
        full_text = ' '.join(lines[:3])
        
        # Look for explicit role patterns in first few sentences
        role_patterns = [
            r'\b(senior\s+)?(software|data|machine learning|devops|cloud|security)\s+(engineer|scientist|developer|analyst)\b',
            r'\b(senior\s+)?(product|project|program)\s+manager\b',
            r'\b(senior\s+)?(business|systems|data)\s+analyst\b',
            r'\b(senior\s+)?salesforce\s+administrator\b',
            r'\b(senior\s+)?(full\s+stack|frontend|backend)\s+(developer|engineer)\b'
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return first_line if first_line and len(first_line) < 100 else ""
    
    def _match_job_title_patterns(self, job_title: str, full_description: str) -> Optional[Tuple[str, float]]:
        """
        Match job title against strong patterns
        
        Args:
            job_title (str): Extracted job title
            full_description (str): Full job description for context
            
        Returns:
            Optional[Tuple[str, float]]: (role, confidence) if strong match found
        """
        if not job_title:
            return None
        
        # Combine job title and first few lines for pattern matching
        search_text = f"{job_title}\n{full_description[:500]}"
        search_text_lower = search_text.lower()
        
        best_match = None
        best_confidence = 0.0
        
        for role, patterns in self.job_title_patterns.items():
            for pattern, base_confidence in patterns:
                matches = re.findall(pattern, search_text_lower, re.IGNORECASE)
                if matches:
                    # Calculate confidence based on pattern strength and context
                    confidence = base_confidence
                    
                    # Bonus for exact title match
                    if job_title.lower() in pattern.lower() or pattern.lower() in job_title.lower():
                        confidence += 0.05
                    
                    # Bonus for multiple matches
                    if len(matches) > 1:
                        confidence += 0.02
                    
                    # Bonus for role-specific keywords in description
                    role_keywords = self.role_keywords.get(role, [])
                    keyword_matches = sum(1 for keyword in role_keywords if keyword.lower() in search_text_lower)
                    if keyword_matches > 0:
                        confidence += min(0.03, keyword_matches * 0.01)
                    
                    confidence = min(1.0, confidence)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = role
        
        # Only return if confidence is high enough
        if best_confidence >= 0.80:
            return best_match, best_confidence
        
        return None
    
    def _fallback_skill_based_detection(self, job_description: str) -> Tuple[str, float]:
        """
        Fallback to skill-based role detection when title patterns don't match
        
        Args:
            job_description (str): Job description text
            
        Returns:
            Tuple[str, float]: (detected_role, confidence_score)
        """
        if not self.role_keywords:
            return "Software Engineer", 0.0
        
        job_lower = job_description.lower()
        role_scores = {}
        
        # Score each role based on keyword matches
        for role, keywords in self.role_keywords.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword in job_lower:
                    score += 1
                    matches += 1
            
            # Add bonus for exact role name matches
            role_words = role.lower().split()
            for word in role_words:
                if word in job_lower:
                    score += 2
            
            # Add priority score
            score += self.role_priority.get(role, 0)
            
            # Special bonus for exact role name matches
            if role == "Software Engineer" and any(term in job_lower for term in ['software engineer', 'senior software engineer']):
                score += 15  # Significant bonus for exact Software Engineer match
            elif role == "DevOps Engineer" and any(term in job_lower for term in ['devops engineer', 'senior devops engineer']):
                score += 15  # Significant bonus for exact DevOps Engineer match
            elif role == "Product Manager" and any(term in job_lower for term in ['product manager', 'senior product manager']):
                score += 15  # Significant bonus for exact Product Manager match
            elif role == "Data Scientist" and any(term in job_lower for term in ['data scientist', 'senior data scientist', 'data science']):
                score += 15  # Significant bonus for exact Data Scientist match
            elif role == "Machine Learning Engineer" and any(term in job_lower for term in ['machine learning engineer', 'ml engineer', 'ai engineer']):
                score += 15  # Significant bonus for exact ML Engineer match
            
            # Additional context bonuses
            elif role == "Data Scientist" and any(term in job_lower for term in ['machine learning', 'ml', 'ai', 'statistics']):
                score += 8   # Bonus for Data Scientist with ML terms
            elif role == "Data Engineer" and any(term in job_lower for term in ['data engineer', 'etl', 'pipeline', 'warehouse']):
                score += 8   # Bonus for Data Engineer
            
            # Calculate confidence based on matches and total keywords
            if keywords:
                confidence = min(1.0, (matches / len(keywords)) * 0.6 + (score / 20) * 0.4)
            else:
                confidence = 0.0
            
            role_scores[role] = (score, confidence)
        
        if not role_scores:
            return "Software Engineer", 0.0
        
        # Find the role with the highest score
        best_role = max(role_scores.keys(), key=lambda r: role_scores[r][0])
        best_score, best_confidence = role_scores[best_role]
        
        # If confidence is too low, try to infer from context
        if best_confidence < 0.3:
            inferred_role = self._infer_role_from_context(job_lower)
            if inferred_role:
                return inferred_role, 0.4
        
        return best_role, best_confidence
    
    def _infer_role_from_context(self, job_lower: str) -> Optional[str]:
        """
        Infer role from job description context when keyword matching is insufficient
        
        Args:
            job_lower (str): Lowercase job description
            
        Returns:
            Optional[str]: Inferred role or None
        """
        # Context-based role inference
        if any(word in job_lower for word in ['python', 'java', 'javascript', 'coding', 'programming']):
            if any(word in job_lower for word in ['frontend', 'ui', 'ux', 'react', 'angular']):
                return "Frontend Engineer"
            elif any(word in job_lower for word in ['backend', 'api', 'server', 'database']):
                return "Backend Engineer"
            elif any(word in job_lower for word in ['full stack', 'fullstack', 'end-to-end']):
                return "Full Stack Engineer"
            else:
                return "Software Engineer"
        
        elif any(word in job_lower for word in ['data', 'analytics', 'sql', 'excel']):
            # Prioritize Data Scientist when ML/AI terms are present
            if any(word in job_lower for word in ['machine learning', 'ai', 'ml', 'statistics', 'python', 'r', 'matlab']):
                # Check if it's explicitly a Data Scientist role
                if any(term in job_lower for term in ['data scientist', 'data science']):
                    return "Data Scientist"
                # Check if it's more engineering-focused
                elif any(term in job_lower for term in ['pipeline', 'etl', 'warehouse', 'engineering', 'infrastructure']):
                    return "Data Engineer"
                else:
                    return "Data Scientist"  # Default to Data Scientist for ML/AI roles
            elif any(word in job_lower for word in ['pipeline', 'etl', 'warehouse', 'engineering']):
                return "Data Engineer"
            else:
                return "Data Analyst"
        
        elif any(word in job_lower for word in ['devops', 'docker', 'kubernetes', 'aws', 'cloud']):
            return "DevOps Engineer"
        
        elif any(word in job_lower for word in ['salesforce', 'crm', 'business process']):
            return "Business Analyst"
        
        elif any(word in job_lower for word in ['product', 'strategy', 'user experience']):
            return "Product Manager"
        
        elif any(word in job_lower for word in ['project', 'planning', 'coordination']):
            return "Project Manager"
        
        return None
    
    def get_role_alternatives(self, job_description: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Get alternative role suggestions for a job description
        
        Args:
            job_description (str): Job description text
            top_n (int): Number of alternative roles to return
            
        Returns:
            List[Tuple[str, float]]: List of (role, confidence) tuples
        """
        if not self.role_keywords:
            return [("Software Engineer", 0.0)]
        
        job_lower = job_description.lower()
        role_scores = []
        
        for role, keywords in self.role_keywords.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword in job_lower:
                    score += 1
                    matches += 1
            
            # Add priority score
            score += self.role_priority.get(role, 0)
            
            # Calculate confidence
            if keywords:
                confidence = min(1.0, (matches / len(keywords)) * 0.7 + (score / 20) * 0.3)
            else:
                confidence = 0.0
            
            role_scores.append((role, score, confidence))
        
        # Sort by score and return top N
        role_scores.sort(key=lambda x: x[1], reverse=True)
        return [(role, confidence) for role, score, confidence in role_scores[:top_n]]
    
    def get_role_description(self, role: str) -> str:
        """
        Get a human-readable description of what a role typically involves
        
        Args:
            role (str): The role name
            
        Returns:
            str: Role description
        """
        role_descriptions = {
            "Software Engineer": "Develops software applications and systems using programming languages and frameworks",
            "Data Scientist": "Analyzes data to extract insights and build predictive models using statistical and ML techniques",
            "DevOps Engineer": "Manages infrastructure, deployment pipelines, and operational processes for software systems",
            "Product Manager": "Leads product strategy, user experience design, and cross-functional team coordination",
            "Business Analyst": "Analyzes business processes, requirements, and data to drive process improvements",
            "Data Engineer": "Builds data pipelines, databases, and infrastructure for data processing and analytics",
            "Frontend Engineer": "Develops user interfaces and frontend applications using web technologies",
            "Backend Engineer": "Builds server-side applications, APIs, and database systems",
            "Full Stack Engineer": "Develops both frontend and backend components of web applications",
            "Cloud Engineer": "Designs and manages cloud infrastructure and services",
            "Security Engineer": "Implements security measures and protects systems from threats",
            "Machine Learning Engineer": "Builds and deploys machine learning models and AI systems",
            "Salesforce Administrator": "Manages Salesforce CRM system configuration and user administration",
            "Project Manager": "Leads project planning, execution, and team coordination",
            "Technical Lead": "Leads technical teams and provides technical guidance and architecture decisions"
        }
        
        return role_descriptions.get(role, f"Professional role focused on {role.lower()} responsibilities")


def detect_role(job_description: str) -> Dict[str, Any]:
    """
    Convenience function to detect role from job description
    
    Args:
        job_description (str): Job description text
        
    Returns:
        Dict[str, Any]: Dictionary with detected role and confidence
    """
    detector = EnhancedRoleDetector()
    return detector.detect_role(job_description)


# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced role detector
    detector = EnhancedRoleDetector()
    
    # Test job descriptions
    test_descriptions = [
        "Senior Python Developer\n\nWe are seeking a talented Senior Python Developer to join our dynamic team. You will be responsible for developing and maintaining high-quality software solutions.",
        "Data Scientist\n\nLooking for a data scientist with Python, SQL, and machine learning skills to analyze complex datasets and build predictive models.",
        "DevOps Engineer\n\nDevOps engineer needed for AWS, Docker, and Kubernetes experience. Must have automation skills and CI/CD pipeline experience.",
        "Product Manager\n\nProduct manager to lead product strategy and user experience design. Experience with business analysis and stakeholder management required.",
        "Business Analyst\n\nBusiness analyst with Salesforce and process optimization experience. Must have strong analytical skills."
    ]
    
    print("🧪 Enhanced Role Detector Test")
    print("=" * 50)
    
    for i, description in enumerate(test_descriptions, 1):
        print(f"\n📋 Test {i}: {description[:60]}...")
        
        # Detect primary role
        primary_role_info = detector.detect_role(description)
        primary_role = primary_role_info['target_role']
        confidence = primary_role_info['role_confidence']
        detection_method = primary_role_info['detection_method']
        
        print(f"   🎯 Primary Role: {primary_role} (Confidence: {confidence:.2f}, Method: {detection_method})")
        
        # Get alternatives
        alternatives = detector.get_role_alternatives(description, top_n=2)
        print(f"   🔄 Alternatives: {', '.join([f'{role} ({conf:.2f})' for role, conf in alternatives[1:]])}")
        
        # Get role description
        role_desc = detector.get_role_description(primary_role)
        print(f"   📝 Description: {role_desc}")
    
    # Show available roles
    print(f"\n📊 Available Roles: {len(detector.role_keywords)}")
    print(f"   Sample roles: {', '.join(list(detector.role_keywords.keys())[:10])}...")
    
    # Test the specific case that was failing
    print(f"\n🔍 Testing the failing case: 'Senior Python Developer'")
    print("-" * 50)
    
    failing_case = """Senior Python Developer

We are seeking a talented Senior Python Developer to join our dynamic team. You will be responsible for developing and maintaining high-quality software solutions.

Requirements:
- 5+ years of experience with Python development
- Strong experience with Django, Flask, or FastAPI frameworks
- Proficiency with PostgreSQL, MySQL, or MongoDB databases
- Experience with AWS cloud services and Docker containerization
- Knowledge of Kubernetes for orchestration
- Familiarity with React, JavaScript, and modern frontend technologies
- Experience with Git version control and CI/CD pipelines
- Understanding of REST APIs and microservices architecture
- Experience with Redis for caching and session management
- Knowledge of Elasticsearch for search functionality
- Familiarity with Jira for project management
- Experience with unit testing and test-driven development"""
    
    role_info = detector.detect_role(failing_case)
    role = role_info['target_role']
    confidence = role_info['role_confidence']
    detection_method = role_info['detection_method']
    
    print(f"   Detected Role: {role}")
    print(f"   Confidence: {confidence:.2f}")
    print(f"   Detection Method: {detection_method}")
    print(f"   Expected: Software Engineer or Python Developer")
    print(f"   Success: {'✅' if 'Software Engineer' in role or 'Python Developer' in role else '❌'}")
