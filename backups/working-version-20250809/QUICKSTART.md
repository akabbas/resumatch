# Quick Start Guide

Get your ATS-friendly resume generated in minutes!

## 🚀 Quick Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Download required models:**
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

3. **Test the installation:**
```bash
python test_generator.py
```

## 📝 Basic Usage

### Option 1: Using the CLI (Recommended)

```bash
# Generate resume from text files
python cli.py --job-file examples/sample_job_description.txt --experience-file examples/sample_experience.json --output my_resume.pdf

# Generate resume from URL
python cli.py --job-url "https://example.com/job-posting" --experience-file my_experience.json --output resume.pdf

# Generate resume with custom details
python cli.py --job-desc "Senior Python Developer..." --experience-file exp.json --name "John Doe" --contact "john@email.com | 555-1234" --output resume.pdf
```

### Option 2: Using Python Code

```python
from resume_generator import ResumeGenerator

# Initialize generator
generator = ResumeGenerator()

# Generate resume
generator.generate_resume(
    job_description="Your job description here...",
    experience_data="Your experience data here...",
    output_path="resume.pdf",
    name="Your Name",
    contact_info="email@example.com | phone | location"
)
```

## 📋 Input Formats

### Job Description
- **Text**: Direct job description text
- **URL**: Web page URL (will be scraped automatically)
- **File**: Text file containing job description

### Experience Data
- **JSON**: Structured data with experience, skills, projects
- **Text**: Simple text description of your experience

### JSON Format Example:
```json
{
  "summary": "Experienced developer...",
  "experience": [
    {
      "title": "Senior Developer",
      "company": "Tech Corp",
      "duration": "2020-2023",
      "description": "Led development team..."
    }
  ],
  "skills": ["Python", "Django", "AWS"],
  "certifications": ["AWS Certified"],
  "projects": [
    {
      "name": "Project Name",
      "description": "Project description...",
      "technologies": ["Python", "React"]
    }
  ]
}
```

## ⚙️ Advanced Options

### OpenAI Integration
For better keyword extraction, set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Then use the `--use-openai` flag:
```bash
python cli.py --job-desc "..." --experience-file exp.json --use-openai --output resume.pdf
```

### Customization Options
```bash
# Single page resume
python cli.py --max-pages 1 --job-desc "..." --experience-file exp.json

# Exclude projects section
python cli.py --no-projects --job-desc "..." --experience-file exp.json

# Verbose output for debugging
python cli.py --verbose --job-desc "..." --experience-file exp.json
```

## 🎯 CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `--job-desc` | Job description as text | `--job-desc "Senior Python Developer..."` |
| `--job-url` | URL to job posting | `--job-url "https://example.com/job"` |
| `--job-file` | File with job description | `--job-file job.txt` |
| `--experience` | Experience as JSON string | `--experience '{"summary": "..."}'` |
| `--experience-file` | File with experience data | `--experience-file exp.json` |
| `--output` | Output PDF file | `--output resume.pdf` |
| `--name` | Your name | `--name "John Doe"` |
| `--contact` | Contact information | `--contact "john@email.com | 555-1234"` |
| `--use-openai` | Use OpenAI for keywords | `--use-openai` |
| `--max-pages` | Maximum pages | `--max-pages 2` |
| `--no-projects` | Exclude projects | `--no-projects` |
| `--verbose` | Verbose output | `--verbose` |

## 🔧 Troubleshooting

### Common Issues:

1. **spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

2. **NLTK data missing:**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

3. **PDF generation fails:**
- Install system dependencies for WeasyPrint
- On macOS: `brew install cairo pango gdk-pixbuf libffi`
- On Ubuntu: `sudo apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev`

4. **OpenAI API errors:**
- Check your API key is set: `echo $OPENAI_API_KEY`
- Ensure you have credits in your OpenAI account

### Getting Help:
- Run with `--verbose` for detailed output
- Check the generated PDF for formatting issues
- Review the extracted keywords in the console output

## 📊 Example Output

The tool will generate a professional PDF resume that includes:
- ✅ ATS-friendly formatting (no tables, graphics)
- ✅ Keyword-matched experience
- ✅ Relevant skills highlighted
- ✅ Clean, readable design
- ✅ Professional typography

Your resume will be optimized for both ATS systems and human reviewers! 