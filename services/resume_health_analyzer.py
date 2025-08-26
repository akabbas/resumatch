#!/usr/bin/env python3
"""
Resume Health Analyzer Service
Analyzes resume quality across multiple dimensions and provides a holistic grade
"""

import re
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class Grade(Enum):
    """Grade enumeration for resume health scores"""
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D_PLUS = "D+"
    D = "D"
    D_MINUS = "D-"
    F = "F"

@dataclass
class DimensionScore:
    """Score for a specific dimension of resume health"""
    score: float  # 0-100
    grade: Grade
    feedback: List[str]
    suggestions: List[str]

@dataclass
class ResumeHealthScore:
    """Complete resume health analysis result"""
    overall_score: float  # 0-100
    overall_grade: Grade
    dimension_scores: Dict[str, DimensionScore]
    summary: str
    top_priorities: List[str]

class ImpactAnalyzer:
    """Analyzes the impact of resume bullet points"""
    
    def __init__(self):
        # Strong action verbs that indicate impact
        self.strong_action_verbs = {
            'achieved', 'increased', 'decreased', 'improved', 'enhanced', 'optimized',
            'streamlined', 'automated', 'implemented', 'developed', 'created', 'built',
            'launched', 'delivered', 'managed', 'led', 'coordinated', 'facilitated',
            'analyzed', 'researched', 'designed', 'architected', 'deployed', 'scaled',
            'reduced', 'eliminated', 'accelerated', 'boosted', 'maximized', 'minimized',
            'transformed', 'revolutionized', 'pioneered', 'established', 'founded',
            'grew', 'expanded', 'consolidated', 'integrated', 'migrated', 'upgraded'
        }
        
        # Quantifiable indicators (numbers, percentages, time periods)
        self.quantifiable_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+[KMB]?',  # Dollar amounts
            r'\d+\s*(million|billion|thousand)',  # Written numbers
            r'\d+\s*(users|customers|clients|projects)',  # Counts
            r'\d+\s*(days|weeks|months|years)',  # Time periods
            r'\d+\s*(hours|minutes)',  # Time units
            r'\d+\s*(people|team members|employees)',  # Team sizes
            r'\d+\s*(languages|technologies|tools)',  # Technology counts
            r'\d+\s*(countries|regions|locations)',  # Geographic scope
            r'\d+\s*(times|instances|occurrences)'  # Frequency
        ]
        
        # Weak action verbs that should be avoided
        self.weak_action_verbs = {
            'helped', 'assisted', 'supported', 'participated', 'involved', 'contributed',
            'worked on', 'was responsible for', 'handled', 'processed', 'maintained',
            'monitored', 'reviewed', 'checked', 'verified', 'tested', 'documented'
        }
    
    def analyze_impact(self, experience_section: str) -> DimensionScore:
        """
        Analyze the impact of experience bullet points
        
        Args:
            experience_section (str): The experience section text
            
        Returns:
            DimensionScore: Analysis result with score, grade, and feedback
        """
        if not experience_section:
            return DimensionScore(
                score=0.0,
                grade=Grade.F,
                feedback=["No experience section found"],
                suggestions=["Add a detailed experience section with specific achievements"]
            )
        
        # Split into bullet points
        bullet_points = self._extract_bullet_points(experience_section)
        
        if not bullet_points:
            return DimensionScore(
                score=0.0,
                grade=Grade.F,
                feedback=["No bullet points found in experience section"],
                suggestions=["Format experience as bullet points with specific achievements"]
            )
        
        # Analyze each bullet point
        analysis_results = []
        total_score = 0
        
        for i, bullet in enumerate(bullet_points):
            bullet_score, bullet_feedback = self._analyze_bullet_point(bullet)
            analysis_results.append({
                'bullet': bullet,
                'score': bullet_score,
                'feedback': bullet_feedback
            })
            total_score += bullet_score
        
        # Calculate overall impact score
        avg_score = total_score / len(bullet_points) if bullet_points else 0
        
        # Generate feedback and suggestions
        feedback = self._generate_impact_feedback(analysis_results)
        suggestions = self._generate_impact_suggestions(analysis_results)
        
        # Determine grade
        grade = self._score_to_grade(avg_score)
        
        return DimensionScore(
            score=avg_score,
            grade=grade,
            feedback=feedback,
            suggestions=suggestions
        )
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text"""
        # Common bullet point patterns
        bullet_patterns = [
            r'^[\s•\-\*\d\.]+\s*(.+)$',  # Standard bullet points
            r'^[\s]*[A-Z][^.!?]*[.!?]?$',  # Capitalized lines that might be bullets
        ]
        
        lines = text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches bullet point patterns
            for pattern in bullet_patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    # Clean up the bullet point
                    clean_bullet = re.sub(r'^[\s•\-\*\d\.]+', '', line).strip()
                    if clean_bullet and len(clean_bullet) > 10:  # Minimum meaningful length
                        bullet_points.append(clean_bullet)
                    break
        
        return bullet_points
    
    def _analyze_bullet_point(self, bullet: str) -> Tuple[float, List[str]]:
        """
        Analyze a single bullet point for impact
        
        Returns:
            Tuple[float, List[str]]: Score (0-100) and feedback
        """
        score = 0
        feedback = []
        
        # Check for strong action verbs
        bullet_lower = bullet.lower()
        strong_verbs_found = []
        weak_verbs_found = []
        
        for verb in self.strong_action_verbs:
            if verb in bullet_lower:
                strong_verbs_found.append(verb)
                score += 25  # Increased from 20
        
        for verb in self.weak_action_verbs:
            if verb in bullet_lower:
                weak_verbs_found.append(verb)
                score -= 15  # Increased penalty from 10
        
        # Check for quantifiable results
        quantifiable_found = []
        for pattern in self.quantifiable_patterns:
            matches = re.findall(pattern, bullet, re.IGNORECASE)
            if matches:
                quantifiable_found.extend(matches)
                score += 30  # Increased from 25
        
        # Check for specific outcomes
        outcome_indicators = [
            'resulted in', 'led to', 'enabled', 'allowed', 'facilitated',
            'achieved', 'accomplished', 'completed', 'delivered', 'launched'
        ]
        
        outcomes_found = []
        for indicator in outcome_indicators:
            if indicator in bullet_lower:
                outcomes_found.append(indicator)
                score += 20  # Increased from 15
        
        # Bonus for multiple strong elements
        if strong_verbs_found and quantifiable_found:
            score += 10  # Bonus for having both strong verbs and quantifiable results
        
        if strong_verbs_found and outcomes_found:
            score += 5   # Bonus for having both strong verbs and clear outcomes
        
        # Generate feedback
        if strong_verbs_found:
            feedback.append(f"Strong action verbs: {', '.join(strong_verbs_found)}")
        
        if weak_verbs_found:
            feedback.append(f"Weak action verbs to improve: {', '.join(weak_verbs_found)}")
        
        if quantifiable_found:
            feedback.append(f"Quantifiable results: {', '.join(quantifiable_found)}")
        else:
            feedback.append("No quantifiable results found")
        
        if outcomes_found:
            feedback.append(f"Clear outcomes: {', '.join(outcomes_found)}")
        
        # Cap score at 100
        score = max(0, min(100, score))
        
        return score, feedback
    
    def _generate_impact_feedback(self, analysis_results: List[Dict]) -> List[str]:
        """Generate overall feedback for impact analysis"""
        feedback = []
        
        # Count high-scoring bullets
        high_scoring = [r for r in analysis_results if r['score'] >= 70]
        medium_scoring = [r for r in analysis_results if 40 <= r['score'] < 70]
        low_scoring = [r for r in analysis_results if r['score'] < 40]
        
        feedback.append(f"Total bullet points analyzed: {len(analysis_results)}")
        feedback.append(f"High-impact bullets: {len(high_scoring)}")
        feedback.append(f"Medium-impact bullets: {len(medium_scoring)}")
        feedback.append(f"Low-impact bullets: {len(low_scoring)}")
        
        if low_scoring:
            feedback.append(f"Bullets needing improvement: {len(low_scoring)}")
        
        return feedback
    
    def _generate_impact_suggestions(self, analysis_results: List[Dict]) -> List[str]:
        """Generate improvement suggestions for impact"""
        suggestions = []
        
        # Analyze common issues
        no_quantifiable = 0
        weak_verbs = 0
        
        for result in analysis_results:
            if "No quantifiable results found" in result['feedback']:
                no_quantifiable += 1
            if any("Weak action verbs" in f for f in result['feedback']):
                weak_verbs += 1
        
        if no_quantifiable > len(analysis_results) * 0.5:
            suggestions.append("Add quantifiable results to most bullet points (numbers, percentages, timeframes)")
        
        if weak_verbs > 0:
            suggestions.append("Replace weak action verbs with strong, impactful verbs")
        
        if len(analysis_results) < 3:
            suggestions.append("Add more detailed bullet points to showcase achievements")
        
        suggestions.append("Use the STAR method: Situation, Task, Action, Result")
        suggestions.append("Include specific metrics and outcomes for each achievement")
        
        return suggestions
    
    def _score_to_grade(self, score: float) -> Grade:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return Grade.A_PLUS
        elif score >= 80:
            return Grade.A
        elif score >= 70:
            return Grade.A_MINUS
        elif score >= 60:
            return Grade.B_PLUS
        elif score >= 50:
            return Grade.B
        elif score >= 40:
            return Grade.B_MINUS
        elif score >= 30:
            return Grade.C_PLUS
        elif score >= 20:
            return Grade.C
        elif score >= 15:
            return Grade.C_MINUS
        elif score >= 10:
            return Grade.D_PLUS
        elif score >= 5:
            return Grade.D
        elif score >= 2:
            return Grade.D_MINUS
        else:
            return Grade.F

class ResumeHealthAnalyzer:
    """Main class for analyzing overall resume health"""
    
    def __init__(self):
        self.impact_analyzer = ImpactAnalyzer()
        # TODO: Add other analyzers
        # self.design_analyzer = DesignAnalyzer()
        # self.skills_analyzer = SkillsAnalyzer()
        # self.clarity_analyzer = ClarityAnalyzer()
    
    def analyze_resume(self, resume_data: Dict) -> ResumeHealthScore:
        """
        Analyze resume health across all dimensions
        
        Args:
            resume_data (Dict): Parsed resume data with sections
            
        Returns:
            ResumeHealthScore: Complete health analysis
        """
        dimension_scores = {}
        
        # Analyze Impact (Experience section)
        experience_section = resume_data.get('experience', '')
        impact_score = self.impact_analyzer.analyze_impact(experience_section)
        dimension_scores['impact'] = impact_score
        
        # TODO: Add other dimension analyses
        # design_score = self.design_analyzer.analyze_design(resume_data)
        # skills_score = self.skills_analyzer.analyze_skills(resume_data)
        # clarity_score = self.clarity_analyzer.analyze_clarity(resume_data)
        
        # Calculate overall score (currently just impact, will be weighted average later)
        overall_score = impact_score.score
        overall_grade = impact_score.grade
        
        # Generate summary and priorities
        summary = self._generate_summary(dimension_scores)
        top_priorities = self._identify_top_priorities(dimension_scores)
        
        return ResumeHealthScore(
            overall_score=overall_score,
            overall_grade=overall_grade,
            dimension_scores=dimension_scores,
            summary=summary,
            top_priorities=top_priorities
        )
    
    def _generate_summary(self, dimension_scores: Dict[str, DimensionScore]) -> str:
        """Generate overall summary of resume health"""
        if not dimension_scores:
            return "No analysis completed"
        
        # For now, just focus on impact
        impact = dimension_scores.get('impact')
        if impact:
            if impact.grade in [Grade.A_PLUS, Grade.A, Grade.A_MINUS]:
                return f"Excellent resume with strong impact ({impact.grade.value}). Your bullet points effectively showcase achievements with quantifiable results."
            elif impact.grade in [Grade.B_PLUS, Grade.B, Grade.B_MINUS]:
                return f"Good resume with solid impact ({impact.grade.value}). Some areas could be strengthened for better results."
            elif impact.grade in [Grade.C_PLUS, Grade.C, Grade.C_MINUS]:
                return f"Resume needs improvement ({impact.grade.value}). Focus on strengthening bullet points and adding quantifiable results."
            else:
                return f"Resume requires significant improvement ({impact.grade.value}). Prioritize restructuring experience section with impactful achievements."
        
        return "Analysis incomplete"
    
    def _identify_top_priorities(self, dimension_scores: Dict[str, DimensionScore]) -> List[str]:
        """Identify top priorities for improvement"""
        priorities = []
        
        for dimension, score in dimension_scores.items():
            if score.grade in [Grade.D, Grade.D_MINUS, Grade.F]:
                priorities.append(f"Urgent: Improve {dimension.title()} section")
            elif score.grade in [Grade.C, Grade.C_MINUS]:
                priorities.append(f"Important: Enhance {dimension.title()} section")
            elif score.grade in [Grade.B, Grade.B_MINUS]:
                priorities.append(f"Consider: Polish {dimension.title()} section")
        
        # Add general priorities
        if not priorities:
            priorities.append("Resume is in good shape - focus on minor refinements")
        
        return priorities[:3]  # Top 3 priorities

# Convenience function
def analyze_resume_health(resume_data: Dict) -> ResumeHealthScore:
    """
    Convenience function to analyze resume health
    
    Args:
        resume_data (Dict): Parsed resume data
        
    Returns:
        ResumeHealthScore: Health analysis result
    """
    analyzer = ResumeHealthAnalyzer()
    return analyzer.analyze_resume(resume_data)

if __name__ == "__main__":
    # Test the analyzer
    test_resume = {
        'experience': '''
        • Helped with data analysis and reporting
        • Was responsible for maintaining database
        • Assisted in project coordination
        • Increased sales by 25% through targeted marketing campaigns
        • Led team of 5 developers to deliver project 2 weeks early
        • Achieved 40% reduction in processing time through automation
        '''
    }
    
    analyzer = ResumeHealthAnalyzer()
    result = analyzer.analyze_resume(test_resume)
    
    print(f"Overall Grade: {result.overall_grade.value}")
    print(f"Overall Score: {result.overall_score:.1f}/100")
    print(f"\nSummary: {result.summary}")
    print(f"\nTop Priorities:")
    for priority in result.top_priorities:
        print(f"• {priority}")
    
    print(f"\nImpact Analysis:")
    impact = result.dimension_scores['impact']
    print(f"Grade: {impact.grade.value}")
    print(f"Score: {impact.score:.1f}/100")
    print(f"Feedback:")
    for feedback in impact.feedback:
        print(f"  - {feedback}")
    print(f"Suggestions:")
    for suggestion in impact.suggestions:
        print(f"  - {suggestion}")
