#!/usr/bin/env python3
"""
Test script for the Impact Analyzer
Demonstrates how the analyzer evaluates different types of resume bullet points
"""

from services.resume_health_analyzer import ResumeHealthAnalyzer, analyze_resume_health

def test_impact_analyzer():
    """Test the impact analyzer with various resume examples"""
    
    print("🚀 Resume Health Score - Impact Analyzer Test")
    print("=" * 60)
    
    # Test Case 1: Weak resume with poor impact
    print("\n📋 Test Case 1: Weak Resume (Poor Impact)")
    print("-" * 40)
    
    weak_resume = {
        'experience': '''
        • Helped with data analysis and reporting
        • Was responsible for maintaining database
        • Assisted in project coordination
        • Handled customer inquiries
        • Monitored system performance
        • Documented procedures
        '''
    }
    
    result1 = analyze_resume_health(weak_resume)
    print(f"Overall Grade: {result1.overall_grade.value}")
    print(f"Overall Score: {result1.overall_score:.1f}/100")
    print(f"Summary: {result1.summary}")
    
    impact1 = result1.dimension_scores['impact']
    print(f"\nImpact Analysis:")
    print(f"Grade: {impact1.grade.value}")
    print(f"Score: {impact1.score:.1f}/100")
    print("Feedback:")
    for feedback in impact1.feedback:
        print(f"  • {feedback}")
    print("Suggestions:")
    for suggestion in impact1.suggestions:
        print(f"  • {suggestion}")
    
    # Test Case 2: Mixed resume with some good points
    print("\n📋 Test Case 2: Mixed Resume (Some Good Impact)")
    print("-" * 40)
    
    mixed_resume = {
        'experience': '''
        • Helped with data analysis and reporting
        • Increased sales by 15% through targeted campaigns
        • Was responsible for maintaining database
        • Led team of 3 people to complete project on time
        • Assisted in project coordination
        • Achieved 20% improvement in customer satisfaction
        '''
    }
    
    result2 = analyze_resume_health(mixed_resume)
    print(f"Overall Grade: {result2.overall_grade.value}")
    print(f"Overall Score: {result2.overall_score:.1f}/100")
    print(f"Summary: {result2.summary}")
    
    impact2 = result2.dimension_scores['impact']
    print(f"\nImpact Analysis:")
    print(f"Grade: {impact2.grade.value}")
    print(f"Score: {impact2.score:.1f}/100")
    print("Feedback:")
    for feedback in impact2.feedback:
        print(f"  • {feedback}")
    print("Suggestions:")
    for suggestion in impact2.suggestions:
        print(f"  • {suggestion}")
    
    # Test Case 3: Strong resume with excellent impact
    print("\n📋 Test Case 3: Strong Resume (Excellent Impact)")
    print("-" * 40)
    
    strong_resume = {
        'experience': '''
        • Increased sales by 25% through targeted marketing campaigns, resulting in $500K additional revenue
        • Led team of 5 developers to deliver project 2 weeks early, saving $50K in development costs
        • Achieved 40% reduction in processing time through automation, improving team productivity
        • Implemented new CRM system that improved customer retention by 30%
        • Developed data pipeline that processed 1M+ records daily, enabling real-time analytics
        • Managed $2M budget and delivered 15% cost savings through vendor negotiations
        '''
    }
    
    result3 = analyze_resume_health(strong_resume)
    print(f"Overall Grade: {result3.overall_grade.value}")
    print(f"Overall Score: {result3.overall_score:.1f}/100")
    print(f"Summary: {result3.summary}")
    
    impact3 = result3.dimension_scores['impact']
    print(f"\nImpact Analysis:")
    print(f"Grade: {impact3.grade.value}")
    print(f"Score: {impact3.score:.1f}/100")
    print("Feedback:")
    for feedback in impact3.feedback:
        print(f"  • {feedback}")
    print("Suggestions:")
    for suggestion in impact3.suggestions:
        print(f"  • {suggestion}")
    
    # Test Case 4: Empty resume
    print("\n📋 Test Case 4: Empty Resume")
    print("-" * 40)
    
    empty_resume = {
        'experience': ''
    }
    
    result4 = analyze_resume_health(empty_resume)
    print(f"Overall Grade: {result4.overall_grade.value}")
    print(f"Overall Score: {result4.overall_score:.1f}/100")
    print(f"Summary: {result4.summary}")
    
    impact4 = result4.dimension_scores['impact']
    print(f"\nImpact Analysis:")
    print(f"Grade: {impact4.grade.value}")
    print(f"Score: {impact4.score:.1f}/100")
    print("Feedback:")
    for feedback in impact4.feedback:
        print(f"  • {feedback}")
    print("Suggestions:")
    for suggestion in impact4.suggestions:
        print(f"  • {suggestion}")
    
    # Summary of all results
    print("\n📊 Summary of All Test Cases")
    print("=" * 60)
    print(f"1. Weak Resume:     {result1.overall_grade.value} ({result1.overall_score:.1f}/100)")
    print(f"2. Mixed Resume:    {result2.overall_grade.value} ({result2.overall_score:.1f}/100)")
    print(f"3. Strong Resume:   {result3.overall_grade.value} ({result3.overall_score:.1f}/100)")
    print(f"4. Empty Resume:    {result4.overall_grade.value} ({result4.overall_score:.1f}/100)")
    
    print("\n🎯 Key Insights:")
    print("• Strong action verbs (increased, led, achieved) boost scores significantly")
    print("• Quantifiable results (25%, $500K, 40%) are highly valued")
    print("• Weak verbs (helped, assisted, was responsible for) reduce scores")
    print("• Clear outcomes and results improve impact scores")
    print("• The analyzer provides specific feedback and actionable suggestions")

if __name__ == "__main__":
    test_impact_analyzer()


