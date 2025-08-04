# Project Structure

```
ats_resume_generator/
├── README.md                 # Main documentation
├── QUICKSTART.md            # Quick start guide
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup script
├── .gitignore              # Git ignore rules
├── __init__.py             # Package initialization
├── resume_generator.py     # Main resume generator module
├── cli.py                  # Command-line interface
├── test_generator.py       # Test script
├── PROJECT_STRUCTURE.md    # This file
└── examples/               # Example files
    ├── sample_job_description.txt
    └── sample_experience.json
```

## Core Components

### 📁 `resume_generator.py`
The main module containing all core functionality:

- **`ResumeGenerator`**: Main class for generating resumes
- **`KeywordExtractor`**: Extracts keywords from job descriptions using NLP
- **`ExperienceMatcher`**: Matches experience with extracted keywords
- **Data Classes**: `JobExperience`, `Project`, `ResumeData`

### 📁 `cli.py`
Command-line interface with comprehensive options:
- Multiple input formats (text, URL, file)
- Customization options (name, contact, pages)
- OpenAI integration
- Verbose debugging

### 📁 `examples/`
Sample files for testing and demonstration:
- `sample_job_description.txt`: Example job posting
- `sample_experience.json`: Structured experience data

### 📁 Configuration Files
- `requirements.txt`: Python dependencies
- `setup.py`: Package installation configuration
- `.gitignore`: Version control exclusions

## Key Features

### 🔍 Keyword Extraction
- **NLP-based**: Uses spaCy and KeyBERT for keyword extraction
- **Technical Dictionary**: Built-in technical terms database
- **OpenAI Integration**: Optional GPT-powered extraction
- **URL Scraping**: Automatically extracts content from job posting URLs

### 🎯 Experience Matching
- **Similarity Scoring**: TF-IDF and cosine similarity
- **Keyword Matching**: Direct keyword presence detection
- **Relevance Filtering**: Only includes relevant experience
- **Skill Highlighting**: Shows matched skills for each experience

### 📄 PDF Generation
- **ATS-Friendly**: No tables, graphics, or complex layouts
- **Professional Design**: Clean, readable typography
- **Responsive Layout**: Adapts to content length
- **Print Optimized**: Proper page breaks and margins

## Architecture

```
Job Description → Keyword Extraction → Experience Matching → Resume Generation → PDF Output
     ↓                    ↓                    ↓                    ↓              ↓
   Text/URL         NLP/OpenAI          TF-IDF/Similarity    Jinja2 Template   WeasyPrint
```

## Dependencies

### Core NLP
- **spaCy**: Natural language processing
- **KeyBERT**: Keyword extraction
- **NLTK**: Text processing utilities

### PDF Generation
- **WeasyPrint**: HTML to PDF conversion
- **Jinja2**: HTML template rendering

### Machine Learning
- **scikit-learn**: TF-IDF vectorization and similarity
- **pandas/numpy**: Data manipulation

### Optional
- **OpenAI**: Enhanced keyword extraction
- **requests/beautifulsoup4**: Web scraping

## Usage Patterns

### 1. Basic Usage
```python
from resume_generator import ResumeGenerator
generator = ResumeGenerator()
generator.generate_resume(job_desc, experience, "output.pdf")
```

### 2. CLI Usage
```bash
python cli.py --job-file job.txt --experience-file exp.json --output resume.pdf
```

### 3. Advanced Usage
```python
generator = ResumeGenerator(use_openai=True, max_pages=1)
generator.generate_resume(job_desc, experience, "output.pdf", name="John Doe")
```

## Extensibility

The modular design allows easy extension:

- **New Keyword Extractors**: Add to `KeywordExtractor` class
- **Custom Templates**: Modify Jinja2 template in `_load_template()`
- **Additional Formats**: Extend `parse_experience_data()` method
- **New Output Formats**: Add to `ResumeGenerator` class

## Testing

- **`test_generator.py`**: Comprehensive test suite
- **Example files**: Real-world test data
- **CLI testing**: Command-line interface validation
- **PDF validation**: Output quality checks 