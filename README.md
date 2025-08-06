# ResuMatch 🎯

> **AI-powered resume generator that creates perfect, job-specific resumes in seconds**

ResuMatch takes your comprehensive experience data and any job description, then generates a professional, ATS-optimized PDF resume tailored specifically for that opportunity.

## ⚠️ **Important Note: Naming Disclaimer**

**This is an open-source project** and is **NOT affiliated** with the commercial platform [ResuMatch.io](https://www.resumatch.io). 

- **This project**: Free, open-source, Python-based resume generator
- **ResuMatch.io**: Commercial SaaS platform with additional features (interviews, cover letters, etc.)

Both tools serve similar purposes but with different approaches and target audiences.

## 🚀 **One Click → Perfect Resume**

**Input**: Your experience data + Job description  
**Output**: Professional PDF resume optimized for that specific job

No more manual resume tailoring. No more generic templates. Just your experience + any job posting = the perfect resume.

## ✨ **How It Works**

ResuMatch uses AI to intelligently optimize your resume for each job:

1. **🧠 Analyzes** your complete professional background (experience, skills, projects, education)
2. **📋 Reads** any job description and identifies key requirements
3. **🎯 Generates** a perfectly tailored resume PDF optimized for that specific job
4. **⚡ Delivers** ATS-compliant formatting that passes automated screening

### **AI-Powered Features:**
- **Job Title Optimization**: Adapts your titles to match target roles (truthfully)
- **Summary Rewriting**: Creates compelling summaries using job keywords
- **Bullet Point Enhancement**: Optimizes descriptions with strong action verbs
- **Intelligent Skill Selection**: Picks most relevant skills from your database
- **Page Optimization**: Automatically adjusts content to fit 1-2 pages

## 🎯 **Why ResuMatch?**

### **vs. Generic Resume Builders:**
- ✅ **Intelligent**: Uses AI to adapt content for each job
- ✅ **Comprehensive**: Stores ALL your skills and selects best ones
- ✅ **Truthful**: Only uses information from your actual experience
- ✅ **ATS-Optimized**: Designed for modern hiring systems

### **vs. Manual Resume Writing:**
- ✅ **Faster**: Seconds instead of hours per application
- ✅ **Consistent**: Professional quality every time
- ✅ **Optimized**: Uses data science for skill matching
- ✅ **Scalable**: Easy to apply to hundreds of jobs

## 🎯 **Streamlined Approach**

**ResuMatch focuses on ONE thing exceptionally well**: Creating perfect resumes from your experience data and job descriptions.

- **No confusing features** - Just resume generation
- **No complex workflows** - Simple input/output
- **No feature bloat** - Laser-focused on core functionality
- **No learning curve** - Upload data, paste job description, get perfect resume

## 🚀 **Current Project Status**

### **✅ Fully Functional Features:**
- **AI-Powered Resume Generation**: Complete with job title optimization, summary rewriting, and bullet point enhancement
- **Intelligent Skill Matching**: Comprehensive skills database with context-aware selection
- **Web Interface**: Modern Flask-based UI for easy resume generation
- **Command Line Interface**: CLI for batch processing and automation
- **ATS Optimization**: Harvard-style formatting that passes automated screening
- **Page Management**: Automatic content adjustment for 1-2 page resumes

### **🔧 Technical Stack:**
- **Backend**: Python 3.13, Flask, spaCy, NLTK, KeyBERT
- **AI/ML**: Intelligent skill matching, keyword extraction, content optimization
- **Frontend**: Bootstrap 5, modern responsive design
- **Output**: Professional PDF resumes with WeasyPrint

### **📊 Project Metrics:**
- **Lines of Code**: 15,000+ lines across multiple modules
- **Skills Database**: 300+ skills with variations and levels
- **AI Features**: 5+ intelligent optimization algorithms
- **Documentation**: Comprehensive guides and examples

### **🔄 Recent Evolution:**
- **Streamlined Interface**: Removed confusing dual-feature approach
- **Focused Functionality**: Single clear workflow for resume generation
- **Enhanced AI**: Advanced job title optimization and summary rewriting
- **Improved UX**: Simplified web interface with clear value proposition

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

#### **Command Line:**
```bash
# Using JSON experience file (recommended)
python cli.py --job-file examples/sample_job_description.txt --experience-file my_experience.json --output my_resume.pdf

# Using text experience file
python cli.py --job-desc "Senior Python Developer..." --experience-file my_experience.txt --output resume.pdf

# With custom contact info
python cli.py --job-desc "..." --experience-file my_experience.json --name "Your Name" --contact "email@example.com | phone | location" --output resume.pdf
```

#### **Web Interface (Recommended):**
```bash
python app.py
# Then visit http://localhost:8001
```

#### **Python API:**
```python
from resumatch import ResumeGenerator

generator = ResumeGenerator()
generator.generate_resume(
    job_description="Senior Python Developer...",
    experience_data=your_experience_json,
    output_path="resume.pdf",
    name="Your Name",
    contact_info="email@example.com | phone | location"
)
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

### Experience Data Format

#### JSON Format
```json
[
  {
    "text": "Developed REST APIs using Django and FastAPI serving 1M+ requests daily",
    "tags": ["Python", "Django", "FastAPI", "REST APIs", "Backend"],
    "category": "experience",
    "impact": "Improved API response time by 40%"
  }
]
```

#### Text Format
```
TEXT: Developed REST APIs using Django and FastAPI serving 1M+ requests daily
TAGS: Python, Django, FastAPI, REST APIs, Backend

TEXT: Implemented microservices architecture with Docker and Kubernetes on AWS
TAGS: Microservices, Docker, Kubernetes, AWS, DevOps
```

**💡 Pro tip**: Copy `examples/sample_bullets.json` or `examples/sample_bullets.txt` and customize!

## 🎯 Features

### Smart Analysis
- **NLP-powered keyword extraction** using spaCy and KeyBERT
- **Technical skill recognition** from 100+ built-in terms
- **Optional OpenAI integration** for enhanced extraction
- **URL scraping** for job postings
- **Job description analysis** with title, skills, and experience level extraction

### Intelligent Matching
- **Relevance scoring** combines keyword matches with similarity
- **Experience filtering** only includes relevant positions
- **Skill highlighting** shows matched skills for each role
- **Automatic ranking** by relevance
- **Bullet point matching** with keyword and fuzzy scoring
- **Modular experience system** for easy customization

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