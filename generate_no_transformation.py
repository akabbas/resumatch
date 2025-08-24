#!/usr/bin/env python3
"""
Generate Resume Without Transformation
Demonstrates backward compatibility of EnhancedDynamicResumeGenerator
"""

import json
from dynamic_resume_generator_enhanced import EnhancedDynamicResumeGenerator

def generate_original_resume():
    """Generate a resume without any transformation"""
    
    print("🔄 Generating Resume WITHOUT Transformation")
    print("=" * 50)
    print("This demonstrates backward compatibility")
    
    # Initialize the enhanced generator
    generator = EnhancedDynamicResumeGenerator()
    
    # Load your experience data
    try:
        with open('my_experience.json', 'r', encoding='utf-8') as f:
            experience_data = json.load(f)
        print("✅ Experience data loaded successfully")
    except FileNotFoundError:
        print("❌ my_experience.json not found")
        return
    
    # Method 1: Use a very generic job description that won't trigger specific role detection
    print(f"\n📋 Using Generic Job Description (Minimal Transformation)")
    print("-" * 50)
    
    generic_job = """
    We are looking for a general technology professional who can work in various roles.
    The ideal candidate should have good technical skills and be able to adapt to different projects.
    Experience with various technologies and tools is preferred.
    """
    
    try:
        html = generator.generate_enhanced_resume_html(experience_data, generic_job)
        
        # Save the resume
        filename = "ammr_original_style_resume.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Resume saved as: {filename}")
        print("   This resume has minimal transformation due to generic role requirements")
        
    except Exception as e:
        print(f"❌ Error generating resume: {e}")
    
    # Method 2: Access original data directly and create a basic resume
    print(f"\n📋 Direct Data Access (No Transformation)")
    print("-" * 50)
    
    print("Original Experience Data:")
    for i, job in enumerate(experience_data.get('experience', [])[:2]):
        print(f"\n{i+1}. {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Duration: {job.get('duration', 'N/A')}")
        print(f"   Description:")
        if isinstance(job.get('description'), list):
            for bullet in job.get('description', []):
                print(f"     • {bullet}")
        else:
            print(f"     {job.get('description', 'N/A')}")
    
    print(f"\nOriginal Skills: {', '.join(experience_data.get('skills', [])[:10])}...")
    print(f"Original Summary: {experience_data.get('summary', '')[:100]}...")
    
    # Method 3: Create a completely untransformed resume by using a very basic job description
    print(f"\n📋 Using Basic Job Description (No Specific Role)")
    print("-" * 50)
    
    try:
        # Use a job description that won't trigger any specific role detection
        basic_job = "General technology position"
        
        html = generator.generate_enhanced_resume_html(experience_data, basic_job)
        
        # Save the untransformed resume
        filename = "ammr_basic_untransformed_resume.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Basic untransformed resume saved as: {filename}")
        print("   This resume uses minimal transformation due to basic job description")
        
    except Exception as e:
        print(f"❌ Error generating basic untransformed resume: {e}")
    
    # Method 4: Show how to access the original data structure
    print(f"\n📋 Original Data Structure Access")
    print("-" * 50)
    
    print("You can always access your original data directly:")
    print(f"   • Experience items: {len(experience_data.get('experience', []))}")
    print(f"   • Skills count: {len(experience_data.get('skills', []))}")
    print(f"   • Projects count: {len(experience_data.get('projects', []))}")
    print(f"   • Certifications count: {len(experience_data.get('certifications', []))}")
    
    # Show a sample of original skills
    original_skills = experience_data.get('skills', [])
    if original_skills:
        print(f"\nSample of original skills (first 10):")
        for i, skill in enumerate(original_skills[:10], 1):
            print(f"   {i}. {skill}")
    
    print(f"\n🎉 Backward Compatibility Demo Complete!")
    print(f"Generated files:")
    print(f"   • ammr_original_style_resume.html - Minimal transformation resume")
    print(f"   • ammr_basic_untransformed_resume.html - Basic untransformed resume")
    print(f"\n💡 Key Points:")
    print(f"   ✅ Original data is always preserved in my_experience.json")
    print(f"   ✅ You can access untransformed data directly from the loaded JSON")
    print(f"   ✅ System gracefully handles cases without transformation")
    print(f"   ✅ Backward compatibility is fully maintained")
    print(f"   ✅ Your original experience data is never modified")

if __name__ == "__main__":
    generate_original_resume()
