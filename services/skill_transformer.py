#!/usr/bin/env python3
"""
Skill Transformer Service
Transforms skills based on target roles using predefined mappings
"""

import json
import os
from typing import Dict, Optional

class SkillTransformer:
    def __init__(self, mapping_file_path: str = "data/skills_mapping.json"):
        """
        Initialize the SkillTransformer with skills mapping data
        
        Args:
            mapping_file_path (str): Path to the skills mapping JSON file
        """
        self.mapping_file_path = mapping_file_path
        self.skills_mapping = self._load_skills_mapping()
    
    def _load_skills_mapping(self) -> Dict:
        """
        Load skills mapping from JSON file
        
        Returns:
            Dict: Skills mapping data
            
        Raises:
            FileNotFoundError: If mapping file doesn't exist
            json.JSONDecodeError: If mapping file has invalid JSON
        """
        try:
            # Get the absolute path relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            full_path = os.path.join(project_root, self.mapping_file_path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Skills mapping file not found at {self.mapping_file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in skills mapping file: {e}")
            return {}
        except Exception as e:
            print(f"Error loading skills mapping: {e}")
            return {}
    
    def transform_skill(self, skill: str, target_role: str) -> str:
        """
        Transform a skill based on the target role
        
        Args:
            skill (str): The original skill to transform
            target_role (str): The target role for transformation
            
        Returns:
            str: Transformed skill phrase or original skill if no mapping found
        """
        if not self.skills_mapping:
            return skill
        
        # Look up the skill in the mapping
        if skill in self.skills_mapping:
            role_mappings = self.skills_mapping[skill]
            
            # Look for exact role match
            if target_role in role_mappings:
                return role_mappings[target_role]
            
            # Look for partial role matches (case-insensitive)
            for role, phrase in role_mappings.items():
                if target_role.lower() in role.lower() or role.lower() in target_role.lower():
                    return phrase
            
            # Look for role category matches
            role_categories = self._get_role_categories(target_role)
            for category in role_categories:
                for role, phrase in role_mappings.items():
                    if category.lower() in role.lower():
                        return phrase
        
        # Return original skill if no transformation found
        return skill
    
    def _get_role_categories(self, target_role: str) -> list:
        """
        Get role categories for better matching
        
        Args:
            target_role (str): The target role
            
        Returns:
            list: List of role categories
        """
        role_lower = target_role.lower()
        categories = []
        
        # Engineering roles
        if any(word in role_lower for word in ['engineer', 'developer', 'programmer']):
            categories.extend(['Software Engineer', 'Backend Engineer', 'Full Stack Engineer'])
        
        # Data roles
        if any(word in role_lower for word in ['data', 'analytics', 'scientist']):
            categories.extend(['Data Scientist', 'Data Engineer', 'Data Analyst'])
        
        # DevOps/Infrastructure roles
        if any(word in role_lower for word in ['devops', 'infrastructure', 'cloud', 'platform']):
            categories.extend(['DevOps Engineer', 'Cloud Engineer', 'Platform Engineer'])
        
        # Business roles
        if any(word in role_lower for word in ['business', 'analyst', 'product', 'manager']):
            categories.extend(['Business Analyst', 'Product Manager', 'Business Systems Analyst'])
        
        # AI/ML roles
        if any(word in role_lower for word in ['ai', 'ml', 'machine learning', 'nlp']):
            categories.extend(['Machine Learning Engineer', 'AI Engineer', 'NLP Engineer'])
        
        # Frontend roles
        if any(word in role_lower for word in ['frontend', 'ui', 'ux', 'web']):
            categories.extend(['Frontend Engineer', 'UI/UX Developer', 'Web Developer'])
        
        # Security roles
        if any(word in role_lower for word in ['security', 'cybersecurity', 'infosec']):
            categories.extend(['Security Engineer', 'Cybersecurity Engineer'])
        
        return categories
    
    def get_available_skills(self) -> list:
        """
        Get list of all available skills in the mapping
        
        Returns:
            list: List of available skills
        """
        return list(self.skills_mapping.keys()) if self.skills_mapping else []
    
    def get_available_roles(self) -> list:
        """
        Get list of all available roles in the mapping
        
        Returns:
            list: List of available roles
        """
        if not self.skills_mapping:
            return []
        
        roles = set()
        for skill_mappings in self.skills_mapping.values():
            roles.update(skill_mappings.keys())
        
        return sorted(list(roles))
    
    def get_skill_roles(self, skill: str) -> list:
        """
        Get all roles that a specific skill can be transformed for
        
        Args:
            skill (str): The skill to check
            
        Returns:
            list: List of roles the skill can be transformed for
        """
        if skill in self.skills_mapping:
            return list(self.skills_mapping[skill].keys())
        return []
    
    def reload_mapping(self) -> bool:
        """
        Reload the skills mapping from file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.skills_mapping = self._load_skills_mapping()
            return True
        except Exception as e:
            print(f"Error reloading skills mapping: {e}")
            return False


def transform_skill(skill: str, target_role: str) -> str:
    """
    Convenience function to transform a skill for a target role
    
    Args:
        skill (str): The original skill to transform
        target_role (str): The target role for transformation
        
    Returns:
        str: Transformed skill phrase or original skill if no mapping found
    """
    transformer = SkillTransformer()
    return transformer.transform_skill(skill, target_role)


# Example usage and testing
if __name__ == "__main__":
    # Test the skill transformer
    transformer = SkillTransformer()
    
    # Test basic transformation
    print("Testing skill transformations:")
    print(f"Python -> Data Scientist: {transformer.transform_skill('Python', 'Data Scientist')}")
    print(f"Python -> DevOps Engineer: {transformer.transform_skill('Python', 'DevOps Engineer')}")
    print(f"Salesforce -> Business Analyst: {transformer.transform_skill('Salesforce', 'Business Analyst')}")
    
    # Test with non-existent mapping
    print(f"Non-existent skill -> Any role: {transformer.transform_skill('NonExistentSkill', 'Software Engineer')}")
    
    # Show available skills and roles
    print(f"\nAvailable skills: {len(transformer.get_available_skills())}")
    print(f"Available roles: {len(transformer.get_available_roles())}")
    
    # Test role categories
    print(f"\nPython can be used for roles: {transformer.get_skill_roles('Python')}")
