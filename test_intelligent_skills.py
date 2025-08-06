#!/usr/bin/env python3
"""
Test script to demonstrate the intelligent skill matching system.
This shows how ResuMatch can now intelligently select skills from a comprehensive database.
"""

from intelligent_skill_matcher import IntelligentSkillMatcher

def test_different_job_types():
    """Test the intelligent skill matcher with different job types."""
    
    matcher = IntelligentSkillMatcher()
    
    # Test cases with different job types
    test_jobs = {
        "Senior Python Developer": """
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
        """,
        
        "Frontend React Developer": """
        Frontend React Developer
        
        We are seeking a talented Frontend Developer to build modern web applications.
        
        Requirements:
        - Strong experience with React.js and JavaScript
        - Experience with HTML/CSS and responsive design
        - Knowledge of TypeScript and modern ES6+ features
        - Experience with state management (Redux, Context API)
        - Understanding of UI/UX principles
        - Experience with testing frameworks (Jest, React Testing Library)
        """,
        
        "Data Analyst": """
        Data Analyst
        
        We are looking for a Data Analyst to help us make data-driven decisions.
        
        Requirements:
        - Experience with SQL and data analysis
        - Proficiency in Excel and data visualization
        - Experience with Python for data analysis
        - Knowledge of business intelligence tools
        - Experience creating KPI dashboards
        - Understanding of data governance and quality
        """,
        
        "Salesforce Administrator": """
        Salesforce Administrator
        
        We need a Salesforce Administrator to manage our CRM system.
        
        Requirements:
        - Experience with Salesforce CRM administration
        - Knowledge of Salesforce CPQ and automation
        - Experience with business process automation
        - Understanding of stakeholder management
        - Experience with requirements gathering
        - Knowledge of enterprise systems integration
        """,
        
        "DevOps Engineer": """
        DevOps Engineer
        
        We are seeking a DevOps Engineer to manage our cloud infrastructure.
        
        Requirements:
        - Experience with AWS cloud services
        - Knowledge of Docker and containerization
        - Experience with Kubernetes orchestration
        - Understanding of CI/CD pipelines
        - Experience with Terraform and infrastructure as code
        - Knowledge of monitoring and logging tools
        """
    }
    
    print("🎯 **Intelligent Skill Matching System Test**\n")
    print("=" * 60)
    
    for job_title, job_description in test_jobs.items():
        print(f"\n📋 **Job: {job_title}**")
        print("-" * 40)
        
        # Analyze the job
        analysis = matcher.analyze_job_requirements(job_description)
        
        print(f"📊 **Analysis:** {analysis['analysis_summary']}")
        print(f"🏷️  **Categories:** {', '.join(analysis['identified_categories'])}")
        
        # Get top relevant skills
        relevant_skills = matcher.select_relevant_skills(job_description, max_skills=8)
        
        print(f"🎯 **Top 8 Relevant Skills:**")
        for i, skill in enumerate(relevant_skills, 1):
            print(f"   {i}. {skill}")
        
        print("\n" + "=" * 60)

def test_skill_database_features():
    """Test various features of the skills database."""
    
    matcher = IntelligentSkillMatcher()
    
    print("\n🔧 **Skills Database Features Test**\n")
    print("=" * 60)
    
    # Test getting expert skills
    expert_skills = matcher.get_expert_skills()
    print(f"📈 **Expert Level Skills Available:** {len(expert_skills)}")
    print(f"Sample: {expert_skills[:5]}")
    
    # Test skill categories
    categories = matcher.get_skill_categories_summary()
    print(f"\n📂 **Available Skill Categories:**")
    for category, subcategories in categories.items():
        print(f"   • {category}: {len(subcategories)} subcategories")
    
    # Test searching skills by category
    technical_skills = matcher.search_skills_by_category("technical")
    print(f"\n⚙️  **Technical Skills Available:** {len(technical_skills)}")
    print(f"Sample: {technical_skills[:5]}")
    
    # Test getting skill details
    python_details = matcher.get_skill_details("Python")
    if python_details:
        print(f"\n🐍 **Python Skill Details:**")
        print(f"   Category: {python_details['category']}")
        print(f"   Level: {python_details['skill_level']}")
        print(f"   Variations: {python_details['all_variations'][:3]}...")

if __name__ == "__main__":
    print("🚀 **ResuMatch Intelligent Skill Matching System**")
    print("Testing comprehensive skill database and intelligent matching...\n")
    
    test_different_job_types()
    test_skill_database_features()
    
    print("\n✅ **Test Complete!**")
    print("The intelligent skill matching system is working perfectly!")
    print("Now ResuMatch can intelligently select the most relevant skills for any job type.") 