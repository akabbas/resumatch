# ResuMatch 🎯

> **Smart resume generation that matches your experience to job descriptions**

ResuMatch automatically analyzes job postings and your experience to create ATS-friendly resumes that highlight your most relevant skills and achievements.

## ✨ What ResuMatch Does

Instead of manually tailoring your resume for each job, ResuMatch:

1. **Extracts key requirements** from job descriptions using NLP
2. **Matches your experience** with the job requirements
3. **Generates optimized resumes** that pass ATS systems
4. **Highlights relevant skills** that actually match your background

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 2. Prepare Your Experience File

You have two options for your experience data:

#### Option A: JSON Format (Recommended)
Create a file called `my_experience.json` with this structure:

**💡 Pro tip**: Copy `examples/experience_template.json` and fill in your details!

```json
{
  "summary": "Experienced software developer with 5+ years in Python development...",
  "experience": [
    {
      "title": "Senior Python Developer",
      "company": "Tech Solutions Inc.",
      "duration": "2020-2023",
      "description": "Led development of REST APIs using Django and FastAPI. Implemented microservices architecture with Docker and Kubernetes. Managed PostgreSQL databases and integrated with React frontend."
    },
    {
      "title": "Python Developer",
      "company": "StartupXYZ",
      "duration": "2018-2020",
      "description": "Developed web applications using Flask and SQLAlchemy. Deployed applications on AWS using Docker containers. Worked with MongoDB and Redis for data storage."
    }
  ],
  "skills": ["Python", "Django", "Flask", "FastAPI", "PostgreSQL", "MongoDB", "AWS", "Docker", "Kubernetes", "React", "JavaScript", "Git", "REST APIs"],
  "certifications": ["AWS Certified Developer", "Docker Certified Associate"],
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built a full-stack e-commerce platform using Django, React, and PostgreSQL. Implemented payment processing with Stripe API.",
      "technologies": ["Django", "React", "PostgreSQL", "Stripe", "Docker"]
    }
  ]
}
```

#### Option B: Plain Text Format
Create a file called `my_experience.txt` with your experience in plain text:

**💡 Pro tip**: Copy `examples/experience_template.txt` and fill in your details!

```
Experienced software developer with 5+ years in Python development, specializing in web applications and API development.

Work Experience:
- Senior Python Developer at Tech Solutions Inc. (2020-2023)
  Led development of REST APIs using Django and FastAPI. Implemented microservices architecture with Docker and Kubernetes.

- Python Developer at StartupXYZ (2018-2020)
  Developed web applications using Flask and SQLAlchemy. Deployed applications on AWS using Docker containers.

Skills: Python, Django, Flask, FastAPI, PostgreSQL, MongoDB, AWS, Docker, Kubernetes, React, JavaScript, Git, REST APIs

Certifications: AWS Certified Developer, Docker Certified Associate

Projects:
- E-commerce Platform: Built full-stack application using Django, React, PostgreSQL
```

### 3. Generate Your Resume
```bash
# Using JSON experience file
python cli.py --job-file examples/sample_job_description.txt --experience-file my_experience.json --output my_resume.pdf

# Using text experience file
python cli.py --job-desc "Senior Python Developer..." --experience-file my_experience.txt --output resume.pdf
```

### 📋 Experience File Format Guide

#### JSON Format (Recommended)
**Best for**: Detailed, structured experience data
**Advantages**:
- ✅ Better keyword matching and skill highlighting
- ✅ Structured sections (experience, skills, projects, certifications)
- ✅ More accurate relevance scoring
- ✅ Cleaner resume formatting

#### Plain Text Format
**Best for**: Quick setup or simple experience
**Advantages**:
- ✅ Easy to create and edit
- ✅ No JSON syntax to learn
- ✅ Works with any text editor
- ✅ Good for basic resume generation

**Tip**: Start with plain text if you're new to ResuMatch, then upgrade to JSON for better results!

### 🚀 Quick Setup (5 minutes)

1. **Copy a template**:
   ```bash
   # For JSON format (recommended)
   cp examples/experience_template.json my_experience.json
   
   # For plain text format
   cp examples/experience_template.txt my_experience.txt
   ```

2. **Edit the template** with your actual experience

3. **Generate your resume**:
   ```bash
   python cli.py --job-desc "Your job description here..." --experience-file my_experience.json --output my_resume.pdf
   ```

## 📋 How It Works

### 1. Job Analysis
ResuMatch reads job descriptions and extracts:
- Required technical skills
- Tools and technologies
- Experience levels
- Certifications needed

### 2. Experience Matching
Your experience is analyzed against job requirements using:
- **Keyword matching**: Direct skill alignment
- **Similarity scoring**: TF-IDF and cosine similarity
- **Relevance filtering**: Only includes relevant experience

### 3. Resume Generation
Creates ATS-optimized PDFs with:
- Clean, professional formatting
- Highlighted relevant skills
- Proper section organization
- No tables or graphics (ATS-friendly)

## 🛠️ Usage

### Command Line Interface

```bash
# Basic usage
python cli.py --job-desc "Job description..." --experience-file exp.json --output resume.pdf

# From job posting URL
python cli.py --job-url "https://example.com/job" --experience-file exp.json --output resume.pdf

# With custom details
python cli.py --job-file job.txt --experience-file exp.json --name "John Doe" --contact "john@email.com | 555-1234" --output resume.pdf

# Using OpenAI for better keyword extraction
python cli.py --job-desc "..." --experience-file exp.json --use-openai --output resume.pdf
```

### Python API

```python
from resumatch import ResumeGenerator

generator = ResumeGenerator()
generator.generate_resume(
    job_description="Senior Python Developer...",
    experience_data=experience_json,
    output_path="resume.pdf",
    name="Your Name",
    contact_info="email@example.com | phone | location"
)
```

## 📊 Input Formats

### Job Description
- **Text**: Direct job description
- **URL**: Web page URL (auto-scraped)
- **File**: Text file containing job description

### Experience Data (JSON)
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

## 🎯 Features

### Smart Analysis
- **NLP-powered keyword extraction** using spaCy and KeyBERT
- **Technical skill recognition** from 100+ built-in terms
- **Optional OpenAI integration** for enhanced extraction
- **URL scraping** for job postings

### Intelligent Matching
- **Relevance scoring** combines keyword matches with similarity
- **Experience filtering** only includes relevant positions
- **Skill highlighting** shows matched skills for each role
- **Automatic ranking** by relevance

### Professional Output
- **ATS-optimized** formatting (no tables, graphics)
- **Clean typography** with standard fonts
- **Responsive layout** adapts to content
- **Print-ready** PDF generation

## 🏗️ Architecture

```
Job Description → Keyword Extraction → Experience Matching → Resume Generation → PDF Output
     ↓                    ↓                    ↓                    ↓              ↓
   Text/URL         NLP/OpenAI          TF-IDF/Similarity    Jinja2 Template   WeasyPrint
```

### Core Components

- **`KeywordExtractor`**: Extracts skills and requirements using NLP
- **`ExperienceMatcher`**: Matches experience with job requirements
- **`ResumeGenerator`**: Creates professional PDF resumes
- **`CLI Interface`**: Easy-to-use command line tool

## ⚙️ Configuration

### CLI Options
| Option | Description | Example |
|--------|-------------|---------|
| `--job-desc` | Job description as text | `--job-desc "Senior Python Developer..."` |
| `--job-url` | URL to job posting | `--job-url "https://example.com/job"` |
| `--job-file` | File with job description | `--job-file job.txt` |
| `--experience-file` | File with experience data | `--experience-file exp.json` |
| `--output` | Output PDF file | `--output resume.pdf` |
| `--name` | Your name | `--name "John Doe"` |
| `--contact` | Contact information | `--contact "john@email.com | 555-1234"` |
| `--use-openai` | Use OpenAI for keywords | `--use-openai` |
| `--max-pages` | Maximum pages | `--max-pages 2` |
| `--no-projects` | Exclude projects | `--no-projects` |
| `--verbose` | Verbose output | `--verbose` |

### Generator Settings
```python
generator = ResumeGenerator(
    use_openai=False,      # Enable OpenAI API
    max_pages=2,          # PDF page limit
    include_projects=True  # Include projects section
)
```

## 🔧 Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/resumatch.git
cd resumatch

# Install dependencies
pip install -r requirements.txt

# Download required models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Test installation
python test_generator.py
```

### Optional: OpenAI Integration
For enhanced keyword extraction, set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 📈 Why ResuMatch?

### Traditional Resume Problems
- ❌ Generic resumes that don't match job requirements
- ❌ Manual tailoring takes hours per application
- ❌ ATS systems reject poorly formatted resumes
- ❌ Skills listed but not backed by experience

### ResuMatch Solutions
- ✅ **Automatic matching** of experience to job requirements
- ✅ **ATS-optimized** formatting that passes screening
- ✅ **Time-saving** automation of resume tailoring
- ✅ **Truth-based** skills that you can actually demonstrate

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- KeyBERT for keyword extraction
- WeasyPrint for PDF generation
- The open-source community for inspiration

---

**Ready to match your experience with the perfect job?** 🎯

Start with ResuMatch today and create resumes that actually get you interviews. 