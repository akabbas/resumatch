#!/usr/bin/env python3
"""
Dynamic Resume Generator CLI - Analyzes any job description and customizes resume automatically
"""

import json
import argparse
import sys
from datetime import datetime
from dynamic_resume_generator import DynamicResumeGenerator

def main():
    parser = argparse.ArgumentParser(
        description="Generate dynamically tailored resume based on any job description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate resume from job description text
  python3 dynamic_cli.py --job-desc "We are seeking a Senior Data Engineer..."

  # Generate resume from job description file
  python3 dynamic_cli.py --job-file job_posting.txt

  # Generate resume with custom output filename
  python3 dynamic_cli.py --job-desc "..." --output my_resume.html

  # Show detailed analysis without generating resume
  python3 dynamic_cli.py --job-desc "..." --analyze-only
        """
    )
    
    parser.add_argument(
        '--job-desc', 
        type=str, 
        help='Job description text'
    )
    
    parser.add_argument(
        '--job-file', 
        type=str, 
        help='File containing job description'
    )
    
    parser.add_argument(
        '--experience-file', 
        type=str, 
        default='my_experience.json',
        help='Your experience data file (default: my_experience.json)'
    )
    
    parser.add_argument(
        '--output', 
        type=str, 
        help='Output filename (default: ammr_dynamic_resume_[timestamp].html)'
    )
    
    parser.add_argument(
        '--analyze-only', 
        action='store_true',
        help='Show job analysis without generating resume'
    )
    
    args = parser.parse_args()
    
    # Check if job description is provided
    if not args.job_desc and not args.job_file:
        print("❌ Error: Please provide either --job-desc or --job-file")
        print("Use --help for examples")
        sys.exit(1)
    
    # Load experience data
    try:
        with open(args.experience_file, 'r', encoding='utf-8') as f:
            experience_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {args.experience_file} not found")
        print("Please create your experience file first")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: {args.experience_file} is not valid JSON")
        sys.exit(1)
    
    # Get job description
    job_description = ""
    if args.job_desc:
        job_description = args.job_desc
    elif args.job_file:
        try:
            with open(args.job_file, 'r', encoding='utf-8') as f:
                job_description = f.read()
        except FileNotFoundError:
            print(f"❌ Error: {args.job_file} not found")
            sys.exit(1)
    
    # Initialize generator
    generator = DynamicResumeGenerator()
    
    # Analyze job description
    print("🔍 Analyzing job description...")
    analysis = generator.analyze_job_description(job_description)
    
    print(f"\n🎯 Job Analysis Results:")
    print(f"   📋 Job Title: {analysis['job_title']}")
    print(f"   📊 Experience Level: {analysis['experience_level']}")
    print(f"   🏢 Industry Focus: {analysis['industry_focus']}")
    print(f"   💻 Key Skills Required: {', '.join(analysis['required_skills'][:5])}")
    
    if analysis['technologies']:
        print(f"   🛠️  Technologies: {', '.join(analysis['technologies'][:3])}")
    
    if analysis['soft_skills']:
        print(f"   🤝 Soft Skills: {', '.join(analysis['soft_skills'][:3])}")
    
    # Show responsibilities if found
    if analysis['responsibilities']:
        print(f"   📝 Key Responsibilities:")
        for i, resp in enumerate(analysis['responsibilities'][:3], 1):
            print(f"      {i}. {resp[:80]}...")
    
    # If analyze-only mode, stop here
    if args.analyze_only:
        print(f"\n✅ Analysis complete. Use without --analyze-only to generate resume.")
        return
    
    # Generate resume
    print(f"\n🚀 Generating tailored resume...")
    html = generator.generate_resume_html(experience_data, job_description)
    
    # Determine output filename
    if args.output:
        filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ammr_dynamic_resume_{timestamp}.html"
    
    # Save resume
    generator.save_html(html, filename)
    
    # Show summary
    print(f"\n📊 Resume Generation Summary:")
    print(f"   📄 Output File: {filename}")
    print(f"   🎯 Job Title: {analysis['job_title']}")
    print(f"   📊 Experience Level: {analysis['experience_level']}")
    print(f"   🏢 Industry: {analysis['industry_focus']}")
    
    # Show skills matching
    user_skills = experience_data.get('skills', [])
    matched_skills = generator.match_skills_to_job(analysis, user_skills)
    print(f"   ✅ Skills Matched: {len(matched_skills)}/{len(user_skills)}")
    print(f"   💡 Top Matched Skills: {', '.join(matched_skills[:5])}")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Open {filename} in your browser")
    print(f"   2. Print to PDF or save as PDF")
    print(f"   3. Customize further if needed")
    print(f"   4. Submit your application!")

if __name__ == "__main__":
    main() 