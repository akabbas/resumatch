#!/usr/bin/env python3
"""
Example Integration: Resume Health Score with Existing Components
Shows how to integrate the Resume Health Score with resume parser and other services
"""

import json
from services.resume_health_analyzer import analyze_resume_health
from services.skill_transformer import SkillTransformer

def analyze_resume_with_health_score(resume_data: dict, target_role: str = None):
    """
    Analyze resume health and optionally transform skills for a target role
    
    Args:
        resume_data (dict): Parsed resume data
        target_role (str): Optional target role for skill transformation
    """
    
    print("🔍 RESUME ANALYSIS WITH HEALTH SCORE")
    print("=" * 60)
    
    # 1. Analyze resume health
    print("\n📊 Step 1: Analyzing Resume Health...")
    health_result = analyze_resume_health(resume_data)
    
    print(f"Overall Grade: {health_result.overall_grade.value}")
    print(f"Overall Score: {health_result.overall_score:.1f}/100")
    print(f"Summary: {health_result.summary}")
    
    # 2. Show impact analysis details
    impact = health_result.dimension_scores['impact']
    print(f"\n🎯 Impact Analysis:")
    print(f"  Grade: {impact.grade.value}")
    print(f"  Score: {impact.score:.1f}/100")
    
    if impact.feedback:
        print("  Feedback:")
        for feedback in impact.feedback:
            print(f"    • {feedback}")
    
    if impact.suggestions:
        print("  Suggestions:")
        for suggestion in impact.suggestions:
            print(f"    • {suggestion}")
    
    # 3. Optional skill transformation
    if target_role and 'skills' in resume_data:
        print(f"\n🔄 Step 2: Transforming Skills for {target_role}...")
        
        try:
            transformer = SkillTransformer()
            original_skills = resume_data['skills']
            
            if isinstance(original_skills, str):
                # Split skills if they're in a string
                skills_list = [s.strip() for s in original_skills.split(',') if s.strip()]
            else:
                skills_list = original_skills
            
            print(f"Original Skills: {', '.join(skills_list)}")
            print(f"\nTransformed Skills for {target_role}:")
            
            transformed_skills = []
            for skill in skills_list:
                transformed = transformer.transform_skill(skill, target_role)
                if transformed != skill:
                    print(f"  {skill} → {transformed}")
                    transformed_skills.append(transformed)
                else:
                    print(f"  {skill} (no transformation available)")
                    transformed_skills.append(skill)
            
            # Update resume data with transformed skills
            resume_data['transformed_skills'] = transformed_skills
            resume_data['target_role'] = target_role
            
        except Exception as e:
            print(f"Error transforming skills: {e}")
    
    # 4. Generate improvement recommendations
    print(f"\n💡 Step 3: Improvement Recommendations")
    print("-" * 40)
    
    if health_result.overall_grade.value in ['A+', 'A', 'A-']:
        print("🎉 Your resume is excellent! Focus on:")
        print("  • Fine-tuning for specific job applications")
        print("  • Adding recent achievements")
        print("  • Updating skills and certifications")
    
    elif health_result.overall_grade.value in ['B+', 'B', 'B-']:
        print("👍 Your resume is good but can be improved:")
        print("  • Strengthen weak bullet points")
        print("  • Add more quantifiable results")
        print("  • Improve action verb usage")
    
    elif health_result.overall_grade.value in ['C+', 'C', 'C-']:
        print("⚠️ Your resume needs improvement:")
        print("  • Restructure experience section")
        print("  • Replace weak action verbs")
        print("  • Add specific metrics and outcomes")
    
    else:
        print("🚨 Your resume requires significant improvement:")
        print("  • Complete restructuring of experience section")
        print("  • Focus on achievements over responsibilities")
        print("  • Use the STAR method for all bullet points")
    
    # 5. Return comprehensive results
    return {
        'health_score': health_result,
        'resume_data': resume_data,
        'recommendations': health_result.top_priorities
    }

def demo_with_sample_data():
    """Demonstrate the integration with sample resume data"""
    
    # Sample resume data (similar to what resume parser would produce)
    sample_resume = {
        'summary': 'Experienced data professional with expertise in analytics and automation',
        'experience': '''
        • Helped with data analysis and reporting for various departments
        • Was responsible for maintaining database systems and user access
        • Assisted in project coordination and stakeholder communication
        • Increased sales by 25% through targeted marketing campaigns
        • Led team of 5 developers to deliver project 2 weeks early
        • Achieved 40% reduction in processing time through automation
        ''',
        'skills': ['Python', 'SQL', 'Salesforce', 'Data Analysis', 'Project Management'],
        'education': 'Bachelor of Science in Computer Science',
        'certifications': ['Salesforce Administrator', 'Data Science Certification']
    }
    
    print("🚀 DEMO: Resume Health Score Integration")
    print("=" * 60)
    
    # Analyze without role targeting
    print("\n📋 Analysis 1: General Resume Health")
    result1 = analyze_resume_with_health_score(sample_resume)
    
    # Analyze with role targeting
    print("\n" + "="*60)
    print("\n📋 Analysis 2: Targeted for Data Scientist Role")
    result2 = analyze_resume_with_health_score(sample_resume, 'Data Scientist')
    
    # Analyze with different role
    print("\n" + "="*60)
    print("\n📋 Analysis 3: Targeted for Business Analyst Role")
    result3 = analyze_resume_with_health_score(sample_resume, 'Business Analyst')
    
    # Fix the target role for the first analysis
    result1['resume_data']['target_role'] = 'General'
    
    return [result1, result2, result3]

def export_analysis_results(results, filename: str = 'resume_analysis_export.json'):
    """Export analysis results to JSON file"""
    
    export_data = {
        'analysis_timestamp': '2024-01-XX',
        'resume_health_score_version': '1.0',
        'analyses': []
    }
    
    for i, result in enumerate(results):
        analysis = {
            'analysis_id': i + 1,
            'target_role': result['resume_data'].get('target_role', 'General'),
            'health_score': {
                'overall_grade': result['health_score'].overall_grade.value,
                'overall_score': result['health_score'].overall_score,
                'summary': result['health_score'].summary,
                'top_priorities': result['health_score'].top_priorities
            },
            'dimension_scores': {}
        }
        
        for dimension, score in result['health_score'].dimension_scores.items():
            analysis['dimension_scores'][dimension] = {
                'grade': score.grade.value,
                'score': score.score,
                'feedback': score.feedback,
                'suggestions': score.suggestions
            }
        
        if 'transformed_skills' in result['resume_data']:
            analysis['transformed_skills'] = result['resume_data']['transformed_skills']
        
        export_data['analyses'].append(analysis)
    
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"\n✅ Analysis results exported to {filename}")
    except Exception as e:
        print(f"Error exporting results: {e}")

if __name__ == "__main__":
    # Run the demo
    results = demo_with_sample_data()
    
    # Export results
    export_analysis_results(results)
    
    print("\n🎯 Key Benefits of This Integration:")
    print("• Comprehensive resume quality assessment")
    print("• Role-specific skill transformation")
    print("• Actionable improvement recommendations")
    print("• Exportable analysis results")
    print("• Easy integration with existing systems")
