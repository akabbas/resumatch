# Contributing to ResuMatch

Thank you for your interest in contributing to ResuMatch! We welcome contributions from the community.

## How to Contribute

### 1. Fork the Repository
1. Go to the ResuMatch repository on GitHub
2. Click the "Fork" button to create your own copy

### 2. Clone Your Fork
```bash
git clone https://github.com/yourusername/resumatch.git
cd resumatch
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes
- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed

### 5. Test Your Changes
```bash
python test_generator.py
```

### 6. Commit Your Changes
```bash
git add .
git commit -m "Add: brief description of your changes"
```

### 7. Push and Create a Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with a clear description of your changes.

## Development Setup

### Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### Run Tests
```bash
python test_generator.py
```

## Areas for Contribution

### High Priority
- **Bug fixes**: Report and fix any issues you find
- **Documentation**: Improve README, add examples
- **Testing**: Add more comprehensive tests
- **Performance**: Optimize keyword extraction or matching

### Medium Priority
- **New features**: Add new input formats, output options
- **Templates**: Create additional resume templates
- **CLI improvements**: Add new command-line options
- **Error handling**: Improve error messages and recovery

### Low Priority
- **UI improvements**: Better formatting, styling
- **Additional languages**: Support for non-English job descriptions
- **Integration**: Connect with job boards or APIs

## Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Any error messages

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing to ResuMatch! 🎯 