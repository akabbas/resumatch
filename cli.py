#!/usr/bin/env python3
"""
Command-line interface for ATS Resume Generator
"""

import argparse
import json
import sys
import os
from pathlib import Path
from dynamic_resume_generator_enhanced import EnhancedDynamicResumeGenerator

def load_json_file(file_path: str) -> dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{file_path}'.")
        sys.exit(1)

def load_text_file(file_path: str) -> str:
    """Load text file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Generate ATS-friendly resume from job description and experience",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate resume from text files
  python cli.py --job-desc job.txt --experience exp.json --output resume.pdf

  # Generate resume from URL and JSON
  python cli.py --job-url "https://example.com/job" --experience exp.json --output resume.pdf

  # Generate resume with custom name and contact
  python cli.py --job-desc job.txt --experience exp.json --name "John Doe" --contact "john@email.com | 555-1234" --output resume.pdf

  # Use OpenAI for better keyword extraction
  python cli.py --job-desc job.txt --experience exp.json --use-openai --output resume.pdf
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--job-desc', 
        type=str, 
        help='Job description as text'
    )
    input_group.add_argument(
        '--job-url', 
        type=str, 
        help='URL to job description (will be scraped)'
    )
    input_group.add_argument(
        '--job-file', 
        type=str, 
        help='File containing job description'
    )
    
    # Experience options
    exp_group = parser.add_mutually_exclusive_group(required=True)
    exp_group.add_argument(
        '--experience', 
        type=str, 
        help='Experience data as JSON string'
    )
    exp_group.add_argument(
        '--experience-file', 
        type=str, 
        help='File containing experience data (JSON or text)'
    )
    
    # Output options
    parser.add_argument(
        '--output', 
        type=str, 
        default='resume.pdf',
        help='Output PDF file path (default: resume.pdf)'
    )
    
    # Personal information
    parser.add_argument(
        '--name', 
        type=str, 
        default='Your Name',
        help='Your name (default: Your Name)'
    )
    parser.add_argument(
        '--contact', 
        type=str, 
        default='email@example.com | phone | location',
        help='Contact information (default: email@example.com | phone | location)'
    )
    
    # Generation options
    parser.add_argument(
        '--use-openai', 
        action='store_true',
        help='Use OpenAI API for keyword extraction (requires OPENAI_API_KEY)'
    )
    parser.add_argument(
        '--max-pages', 
        type=int, 
        default=2,
        help='Maximum number of pages (default: 2)'
    )
    parser.add_argument(
        '--no-projects', 
        action='store_true',
        help='Exclude projects section'
    )
    parser.add_argument(
        '--no-transform',
        action='store_true',
        help='Do not transform the resume (e.g., for a specific format)'
    )
    
    # Verbose output
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate OpenAI usage
    if args.use_openai and not os.getenv('OPENAI_API_KEY'):
        print("Error: --use-openai requires OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    # Get job description
    job_description = ""
    if args.job_desc:
        job_description = args.job_desc
    elif args.job_url:
        job_description = args.job_url
    elif args.job_file:
        job_description = load_text_file(args.job_file)
    
    # Get experience data
    experience_data = None
    if args.experience:
        try:
            experience_data = json.loads(args.experience)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --experience argument")
            sys.exit(1)
    elif args.experience_file:
        file_path = args.experience_file
        if file_path.endswith('.json'):
            experience_data = load_json_file(file_path)
        else:
            # Treat as plain text
            experience_data = load_text_file(file_path)
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize generator
        generator = EnhancedDynamicResumeGenerator(
            use_openai=args.use_openai,
            max_pages=args.max_pages,
            include_projects=not args.no_projects,
            no_transform=args.no_transform
        )
        
        if args.verbose:
            print(f"Job description length: {len(job_description)} characters")
            print(f"Experience data type: {type(experience_data)}")
            print(f"Output path: {args.output}")
            print(f"Using OpenAI: {args.use_openai}")
            print(f"AI Transformation: {'Disabled' if args.no_transform else 'Enabled'}")
        
        # Generate resume
        result = generator.generate_resume(
            job_description=job_description,
            experience_data=experience_data,
            output_path=args.output,
            name=args.name,
            contact_info=args.contact
        )
        
        print(f"✅ Resume generated successfully: {args.output}")
        
    except Exception as e:
        print(f"❌ Error generating resume: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 