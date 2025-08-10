#!/usr/bin/env python3
"""
ResuMatch Job Tailor CLI

Command-line interface for tailoring resumes to specific job descriptions
using modular experience bullets.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Dict
from job_matcher import ResumeTailor, BulletPoint, create_sample_bullets

def load_bullets_from_json(file_path: str) -> List[BulletPoint]:
    """Load bullet points from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        bullets = []
        for item in data:
            bullet = BulletPoint(
                text=item.get('text', ''),
                tags=item.get('tags', []),
                category=item.get('category', 'experience'),
                impact=item.get('impact', '')
            )
            bullets.append(bullet)
        
        return bullets
    except Exception as e:
        print(f"Error loading bullets from {file_path}: {e}")
        sys.exit(1)

def load_bullets_from_text(file_path: str) -> List[BulletPoint]:
    """Load bullet points from text file (simple format)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        bullets = []
        current_bullet = ""
        current_tags = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('TEXT:'):
                if current_bullet:
                    bullets.append(BulletPoint(
                        text=current_bullet.strip(),
                        tags=current_tags,
                        category="experience"
                    ))
                current_bullet = line[5:].strip()
                current_tags = []
            elif line.startswith('TAGS:'):
                current_tags = [tag.strip() for tag in line[5:].split(',')]
            elif line and not line.startswith('#'):  # Skip comments
                current_bullet += " " + line
        
        # Add the last bullet
        if current_bullet:
            bullets.append(BulletPoint(
                text=current_bullet.strip(),
                tags=current_tags,
                category="experience"
            ))
        
        return bullets
    except Exception as e:
        print(f"Error loading bullets from {file_path}: {e}")
        sys.exit(1)

def save_tailored_resume(resume_data: Dict, output_path: str):
    """Save tailored resume to JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Tailored resume saved to: {output_path}")
    except Exception as e:
        print(f"Error saving resume: {e}")
        sys.exit(1)

def generate_resume_text(resume_data: Dict) -> str:
    """Generate human-readable resume text"""
    text = f"# {resume_data['job_title']}\n\n"
    text += f"## Professional Summary\n{resume_data['summary']}\n\n"
    
    text += f"## Key Skills\n"
    for skill in resume_data['skills'][:10]:
        text += f"- {skill}\n"
    text += "\n"
    
    if resume_data['experience_bullets']:
        text += f"## Professional Experience\n"
        for i, bullet in enumerate(resume_data['experience_bullets'], 1):
            text += f"{i}. {bullet}\n"
        text += "\n"
    
    if resume_data['project_bullets']:
        text += f"## Projects\n"
        for i, bullet in enumerate(resume_data['project_bullets'], 1):
            text += f"{i}. {bullet}\n"
        text += "\n"
    
    text += f"## Analysis\n"
    text += f"- Experience Level: {resume_data['experience_level']}\n"
    text += f"- Industry: {resume_data['industry']}\n"
    text += f"- Matched Keywords: {', '.join(resume_data['matched_keywords'][:5])}\n"
    text += f"- Average Match Score: {sum(resume_data['matching_scores']) / len(resume_data['matching_scores']):.2f}\n"
    
    return text

def main():
    parser = argparse.ArgumentParser(
        description="Tailor resume to job description using modular experience bullets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use sample bullets and job description
  python job_tailor_cli.py --job-desc "Senior Python Developer..." --output tailored_resume.json

  # Use custom bullets from JSON file
  python job_tailor_cli.py --job-desc job.txt --bullets bullets.json --output resume.json

  # Use custom bullets from text file
  python job_tailor_cli.py --job-desc job.txt --bullets bullets.txt --output resume.json

  # Generate text output
  python job_tailor_cli.py --job-desc job.txt --output resume.txt --format text
        """
    )
    
    # Input options
    parser.add_argument(
        '--job-desc',
        type=str,
        help='Job description as text'
    )
    parser.add_argument(
        '--job-file',
        type=str,
        help='File containing job description'
    )
    parser.add_argument(
        '--bullets',
        type=str,
        help='File containing bullet points (JSON or text format)'
    )
    parser.add_argument(
        '--use-sample-bullets',
        action='store_true',
        help='Use sample bullet points for testing'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        default='tailored_resume.json',
        help='Output file path (default: tailored_resume.json)'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=8,
        help='Number of top bullets to include (default: 8)'
    )
    
    # Verbose output
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.job_desc and not args.job_file:
        print("Error: Must provide either --job-desc or --job-file")
        sys.exit(1)
    
    if not args.bullets and not args.use_sample_bullets:
        print("Error: Must provide either --bullets or --use-sample-bullets")
        sys.exit(1)
    
    # Get job description
    job_description = ""
    if args.job_desc:
        job_description = args.job_desc
    elif args.job_file:
        try:
            with open(args.job_file, 'r', encoding='utf-8') as f:
                job_description = f.read()
        except Exception as e:
            print(f"Error reading job file: {e}")
            sys.exit(1)
    
    # Get bullet points
    bullets = []
    if args.use_sample_bullets:
        print("📝 Using sample bullet points...")
        bullets = create_sample_bullets()
    elif args.bullets:
        file_path = args.bullets
        if file_path.endswith('.json'):
            bullets = load_bullets_from_json(file_path)
        else:
            bullets = load_bullets_from_text(file_path)
    
    if not bullets:
        print("Error: No bullet points loaded")
        sys.exit(1)
    
    if args.verbose:
        print(f"📋 Loaded {len(bullets)} bullet points")
        print(f"📄 Job description length: {len(job_description)} characters")
    
    # Initialize tailor
    tailor = ResumeTailor()
    
    try:
        # Tailor resume
        tailored_resume = tailor.tailor_resume(
            job_description=job_description,
            bullets=bullets,
            top_n=args.top_n
        )
        
        # Save output
        if args.format == 'json':
            save_tailored_resume(tailored_resume, args.output)
        else:  # text format
            resume_text = generate_resume_text(tailored_resume)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(resume_text)
            print(f"✅ Tailored resume saved to: {args.output}")
        
        # Display summary
        print(f"\n📊 Summary:")
        print(f"  - Job Title: {tailored_resume['job_title']}")
        print(f"  - Experience Level: {tailored_resume['experience_level']}")
        print(f"  - Industry: {tailored_resume['industry']}")
        print(f"  - Selected Bullets: {len(tailored_resume['experience_bullets']) + len(tailored_resume['project_bullets'])}")
        print(f"  - Top Skills: {', '.join(tailored_resume['skills'][:5])}")
        
    except Exception as e:
        print(f"❌ Error tailoring resume: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 