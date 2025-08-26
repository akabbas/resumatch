#!/usr/bin/env python3
"""
Resume Health Score CLI
Command-line interface for analyzing resume health
"""

import argparse
import json
import sys
from pathlib import Path
from services.resume_health_analyzer import analyze_resume_health, ResumeHealthAnalyzer

def analyze_resume_file(file_path: str) -> dict:
    """Analyze a resume file and return structured data"""
    # For now, we'll create a simple structure
    # In a real implementation, this would use the resume parser
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple parsing - extract experience section
        lines = content.split('\n')
        experience_lines = []
        in_experience = False
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['experience', 'work history', 'employment']):
                in_experience = True
                continue
            elif any(keyword in line_lower for keyword in ['education', 'skills', 'summary', 'profile']):
                in_experience = False
                continue
            
            if in_experience and line.strip():
                experience_lines.append(line.strip())
        
        return {
            'experience': '\n'.join(experience_lines),
            'source_file': file_path
        }
    
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return {'experience': '', 'error': str(e)}

def analyze_resume_text(text: str) -> dict:
    """Analyze resume text directly"""
    # Split by bullet points if they're on the same line
    if '•' in text or '-' in text:
        # Split by bullet indicators and clean up
        lines = []
        for line in text.split('•'):
            if line.strip():
                lines.append('•' + line.strip())
        for line in text.split('-'):
            if line.strip():
                lines.append('-' + line.strip())
        
        # Remove duplicates and empty lines
        lines = [line.strip() for line in lines if line.strip()]
        if lines:
            text = '\n'.join(lines)
    
    return {
        'experience': text,
        'source': 'direct_input'
    }

def display_results(result, show_details: bool = False):
    """Display analysis results in a formatted way"""
    
    print("\n" + "="*60)
    print("🏥 RESUME HEALTH SCORE ANALYSIS")
    print("="*60)
    
    # Overall score
    print(f"\n📊 OVERALL SCORE")
    print(f"Grade: {result.overall_grade.value}")
    print(f"Score: {result.overall_score:.1f}/100")
    
    # Summary
    print(f"\n📝 SUMMARY")
    print(result.summary)
    
    # Top priorities
    print(f"\n🎯 TOP PRIORITIES")
    for i, priority in enumerate(result.top_priorities, 1):
        print(f"{i}. {priority}")
    
    if show_details:
        # Detailed dimension analysis
        print(f"\n🔍 DETAILED ANALYSIS")
        for dimension, score in result.dimension_scores.items():
            print(f"\n{dimension.upper()} ANALYSIS:")
            print(f"  Grade: {score.grade.value}")
            print(f"  Score: {score.score:.1f}/100")
            
            if score.feedback:
                print(f"  Feedback:")
                for feedback in score.feedback:
                    print(f"    • {feedback}")
            
            if score.suggestions:
                print(f"  Suggestions:")
                for suggestion in score.suggestions:
                    print(f"    • {suggestion}")
    
    print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(
        description="Analyze resume health and provide actionable feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a resume file
  python resume_health_cli.py -f resume.txt
  
  # Analyze resume text directly
  python resume_health_cli.py -t "• Increased sales by 25%"
  
  # Show detailed analysis
  python resume_health_cli.py -f resume.txt --detailed
  
  # Interactive mode
  python resume_health_cli.py --interactive
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Path to resume file to analyze'
    )
    
    parser.add_argument(
        '-t', '--text',
        help='Resume text to analyze directly'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed analysis for all dimensions'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        run_interactive_mode()
        return
    
    # File analysis
    if args.file:
        if not Path(args.file).exists():
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
        
        resume_data = analyze_resume_file(args.file)
        if 'error' in resume_data:
            print(f"Error analyzing file: {resume_data['error']}")
            sys.exit(1)
    
    # Text analysis
    elif args.text:
        resume_data = analyze_resume_text(args.text)
    
    else:
        print("Error: Must specify either --file, --text, or --interactive")
        parser.print_help()
        sys.exit(1)
    
    # Analyze resume health
    try:
        result = analyze_resume_health(resume_data)
        
        if args.json:
            # Output JSON format
            output = {
                'overall_grade': result.overall_grade.value,
                'overall_score': result.overall_score,
                'summary': result.summary,
                'top_priorities': result.top_priorities,
                'dimensions': {}
            }
            
            for dimension, score in result.dimension_scores.items():
                output['dimensions'][dimension] = {
                    'grade': score.grade.value,
                    'score': score.score,
                    'feedback': score.feedback,
                    'suggestions': score.suggestions
                }
            
            print(json.dumps(output, indent=2))
        else:
            # Display formatted results
            display_results(result, args.detailed)
    
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        sys.exit(1)

def run_interactive_mode():
    """Run the CLI in interactive mode"""
    print("🏥 Resume Health Score - Interactive Mode")
    print("="*50)
    print("Enter your resume experience section (one bullet point per line)")
    print("Type 'END' on a new line when finished")
    print("Type 'HELP' for formatting tips")
    print("-" * 50)
    
    experience_lines = []
    
    while True:
        try:
            line = input("> ").strip()
            
            if line.upper() == 'END':
                break
            elif line.upper() == 'HELP':
                print("\n📋 FORMATTING TIPS:")
                print("• Start each bullet point with • or -")
                print("• Use strong action verbs: achieved, increased, led, implemented")
                print("• Include quantifiable results: 25%, $500K, 5 people")
                print("• Show clear outcomes: resulted in, led to, enabled")
                print("• Example: • Increased sales by 25% through targeted campaigns")
                print("-" * 50)
                continue
            elif line:
                experience_lines.append(line)
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return
        except EOFError:
            break
    
    if not experience_lines:
        print("No experience data entered. Exiting.")
        return
    
    # Analyze the entered experience
    experience_text = '\n'.join(experience_lines)
    resume_data = analyze_resume_text(experience_text)
    
    try:
        result = analyze_resume_health(resume_data)
        display_results(result, show_details=True)
        
        # Ask if user wants to save
        save = input("\n💾 Save this analysis to a file? (y/n): ").strip().lower()
        if save in ['y', 'yes']:
            filename = input("Enter filename (default: resume_analysis.txt): ").strip()
            if not filename:
                filename = "resume_analysis.txt"
            
            try:
                with open(filename, 'w') as f:
                    f.write("Resume Health Score Analysis\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Overall Grade: {result.overall_grade.value}\n")
                    f.write(f"Overall Score: {result.overall_score:.1f}/100\n\n")
                    f.write(f"Summary: {result.summary}\n\n")
                    f.write("Top Priorities:\n")
                    for priority in result.top_priorities:
                        f.write(f"• {priority}\n")
                    f.write("\nDetailed Analysis:\n")
                    for dimension, score in result.dimension_scores.items():
                        f.write(f"\n{dimension.upper()}:\n")
                        f.write(f"  Grade: {score.grade.value}\n")
                        f.write(f"  Score: {score.score:.1f}/100\n")
                        f.write("  Feedback:\n")
                        for feedback in score.feedback:
                            f.write(f"    • {feedback}\n")
                        f.write("  Suggestions:\n")
                        for suggestion in score.suggestions:
                            f.write(f"    • {suggestion}\n")
                
                print(f"✅ Analysis saved to {filename}")
            
            except Exception as e:
                print(f"Error saving file: {e}")
    
    except Exception as e:
        print(f"Error analyzing resume: {e}")

if __name__ == "__main__":
    main()
