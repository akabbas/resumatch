# 🏗️ ResuMatch Environment Management Guide

This guide explains how to manage both **Production** and **Development** environments for ResuMatch.

## 📊 **Environment Overview**

| Aspect | Production | Development |
|--------|------------|-------------|
| **Purpose** | Live deployment with stable features | Development with GPT-5 features |
| **Port** | 8000 | 8001 |
| **Debug** | Disabled | Enabled |
| **Workers** | 8 | 2 |
| **Security** | Strict | Relaxed |
| **Features** | Current stable features | GPT-5 enhanced features |
| **Database** | PostgreSQL | SQLite |
| **Monitoring** | Sentry + Prometheus | Debug logging |

## 🚀 **Quick Start Commands**

### **Production Environment**
```bash
# Setup production
./scripts/setup_production.sh

# Run production
./scripts/run_production.sh

# Or with Docker
docker-compose -f docker-compose.production.yml up --build
```

### **Development Environment**
```bash
# Setup development with GPT-5
./scripts/setup_development.sh

# Run development
./scripts/run_development.sh

# Or with Docker
docker-compose -f docker-compose.development.yml up --build
```

## 📁 **Environment Structure**

```
resumatch/
├── environments/
│   ├── production/
│   │   └── requirements.txt
│   └── development/
│       └── requirements.txt
├── scripts/
│   ├── setup_production.sh
│   ├── run_production.sh
│   ├── setup_development.sh
│   └── run_development.sh
├── app_production.py
├── app_development.py
├── gpt5_enhanced_generator.py
├── env.production
├── env.development
├── Dockerfile.production
├── Dockerfile.development
├── docker-compose.production.yml
└── docker-compose.development.yml
```

## 🔧 **Environment Configuration**

### **Production Environment (`env.production`)**
```bash
# Core Settings
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_PORT=8000
LOG_LEVEL=WARNING

# Security
SECRET_KEY=your_very_secure_production_secret_key_here
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# OpenAI Configuration
OPENAI_API_KEY=your_production_openai_key_here
OPENAI_MODEL=gpt-4

# Feature Flags - All current features enabled
ENABLE_GPT5_FEATURES=False
ENABLE_ANALYTICS=True
ENABLE_MONITORING=True
ENABLE_INTELLIGENT_SKILL_MATCHING=True
ENABLE_JOB_TITLE_OPTIMIZATION=True
ENABLE_SUMMARY_OPTIMIZATION=True
ENABLE_BULLET_OPTIMIZATION=True
ENABLE_PAGE_OPTIMIZATION=True

# Performance Settings
WORKERS=8
TIMEOUT=120
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50
```

### **Development Environment (`env.development`)**
```bash
# Core Settings
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=8001
LOG_LEVEL=DEBUG

# Security (Development - less strict)
SECRET_KEY=dev-secret-key-change-in-production
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# OpenAI Configuration - GPT-5 Features
OPENAI_API_KEY=your_development_openai_key_here
OPENAI_MODEL=gpt-5
ANTHROPIC_API_KEY=your_anthropic_key_here
COHERE_API_KEY=your_cohere_key_here

# Feature Flags - GPT-5 Features Enabled
ENABLE_GPT5_FEATURES=True
ENABLE_ANALYTICS=True
ENABLE_MONITORING=True
ENABLE_INTELLIGENT_SKILL_MATCHING=True
ENABLE_JOB_TITLE_OPTIMIZATION=True
ENABLE_SUMMARY_OPTIMIZATION=True
ENABLE_BULLET_OPTIMIZATION=True
ENABLE_PAGE_OPTIMIZATION=True

# GPT-5 Enhanced Features
ENABLE_ADVANCED_CONTENT_GENERATION=True
ENABLE_INTELLIGENT_CAREER_ADVICE=True
ENABLE_ADVANCED_JOB_ANALYSIS=True
ENABLE_REAL_TIME_OPTIMIZATION=True
ENABLE_MULTI_MODEL_AI=True
ENABLE_LANGCHAIN_INTEGRATION=True

# Performance Settings (Development - lighter)
WORKERS=2
TIMEOUT=60
MAX_REQUESTS=100
MAX_REQUESTS_JITTER=10
```

## 🎯 **Feature Comparison**

### **Production Features**
- ✅ **Intelligent Skill Matching** - Advanced skill selection
- ✅ **Job Title Optimization** - Smart job title adaptation
- ✅ **Summary Rewriting** - Professional summary optimization
- ✅ **Bullet Point Enhancement** - Action verb optimization
- ✅ **Page Optimization** - Smart content adjustment
- ✅ **Harvard-Style Formatting** - Professional templates
- ✅ **Web Interface** - Bootstrap 5 interface
- ✅ **PDF Generation** - High-quality PDF output
- ✅ **Production Server** - Gunicorn WSGI server
- ✅ **Security Headers** - HTTPS-ready
- ✅ **Error Handling** - Comprehensive error pages
- ✅ **Health Checks** - Production monitoring
- ✅ **Logging** - Structured logging
- ✅ **Monitoring** - Sentry integration
- ✅ **Analytics** - Resume generation tracking

### **Development Features (All Production + GPT-5)**
- ✅ **All Production Features** - Everything from production
- ✅ **Advanced Content Generation** - GPT-5 powered summaries
- ✅ **Intelligent Career Advice** - Personalized insights
- ✅ **Advanced Job Analysis** - Deep job understanding
- ✅ **Real-time Optimization** - Continuous improvement
- ✅ **Multi-model AI** - Anthropic, Cohere integration
- ✅ **LangChain Integration** - Advanced AI workflows
- ✅ **Hot Reload** - Development server with auto-restart
- ✅ **Debug Tools** - Jupyter, IPython, profiling
- ✅ **Development Monitoring** - Enhanced debugging
- ✅ **Career Advice API** - `/career-advice` endpoint
- ✅ **Job Analysis API** - `/job-analysis` endpoint

## 🐳 **Docker Management**

### **Production Docker**
```bash
# Build and run production
docker-compose -f docker-compose.production.yml up --build

# Production services:
# - resumatch-prod:8000 (Main app)
# - redis:6379 (Caching)
# - postgres:5432 (Database)
```

### **Development Docker**
```bash
# Build and run development
docker-compose -f docker-compose.development.yml up --build

# Development services:
# - resumatch-dev:8001 (Main app with GPT-5)
# - redis-dev:6379 (Development caching)
# - postgres-dev:5432 (Development database)
# - jupyter-dev:8888 (Jupyter Lab)
```

## 🔄 **Environment Switching**

### **Quick Switch Scripts**
```bash
# Switch to production
./scripts/run_production.sh

# Switch to development
./scripts/run_development.sh

# Check current environment
curl http://localhost:8000/health  # Production
curl http://localhost:8001/health  # Development
```

### **Environment Variables**
```bash
# Production
export FLASK_ENV=production
export FLASK_PORT=8000
export FLASK_DEBUG=False

# Development
export FLASK_ENV=development
export FLASK_PORT=8001
export FLASK_DEBUG=True
```

## 📊 **Monitoring & Health Checks**

### **Production Health Check**
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "environment": "production",
  "features_enabled": {
    "intelligent_skill_matching": true,
    "job_title_optimization": true,
    "summary_optimization": true,
    "bullet_optimization": true,
    "page_optimization": true
  }
}
```

### **Development Health Check**
```bash
curl http://localhost:8001/health
```
Response:
```json
{
  "status": "healthy",
  "environment": "development",
  "gpt5_enabled": true,
  "features_enabled": {
    "intelligent_skill_matching": true,
    "job_title_optimization": true,
    "summary_optimization": true,
    "bullet_optimization": true,
    "page_optimization": true,
    "gpt5_features": true,
    "advanced_content_generation": true,
    "intelligent_career_advice": true,
    "advanced_job_analysis": true,
    "real_time_optimization": true,
    "multi_model_ai": true,
    "langchain_integration": true
  }
}
```

## 🛠️ **Development Tools**

### **Jupyter Lab**
```bash
# Access Jupyter Lab
http://localhost:8888

# Features:
# - Interactive Python notebooks
# - GPT-5 feature testing
# - Data analysis
# - Model experimentation
```

### **API Testing**
```bash
# Test career advice
curl -X POST http://localhost:8001/career-advice \
  -H "Content-Type: application/json" \
  -d '{"job_description": "...", "experience_json": "..."}'

# Test job analysis
curl -X POST http://localhost:8001/job-analysis \
  -H "Content-Type: application/json" \
  -d '{"job_description": "..."}'
```

## 🔒 **Security Considerations**

### **Production Security**
- ✅ HTTPS ready configuration
- ✅ Secure cookies
- ✅ CSRF protection
- ✅ Input validation
- ✅ File upload restrictions
- ✅ Non-root user execution
- ✅ Environment variable security
- ✅ Error message sanitization

### **Development Security**
- ⚠️ Relaxed security for development
- ⚠️ Debug mode enabled
- ⚠️ Less strict cookie settings
- ⚠️ Detailed error messages
- ⚠️ Hot reload enabled

## 📈 **Performance Comparison**

| Metric | Production | Development |
|--------|------------|-------------|
| **Workers** | 8 | 2 |
| **Memory** | 2GB | 4GB |
| **CPU** | 2 cores | 2 cores |
| **Timeout** | 120s | 60s |
| **Max Requests** | 1000 | 100 |
| **Response Time** | 5-15s | 10-30s |
| **Concurrent Users** | 50+ | 10+ |

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Port Conflicts**
   ```bash
   # Kill processes on ports
   lsof -ti:8000 | xargs kill -9  # Production
   lsof -ti:8001 | xargs kill -9  # Development
   ```

2. **Environment Variables**
   ```bash
   # Check environment
   echo $FLASK_ENV
   echo $FLASK_PORT
   echo $OPENAI_API_KEY
   ```

3. **Dependencies**
   ```bash
   # Reinstall dependencies
   pip install -r environments/production/requirements.txt
   pip install -r environments/development/requirements.txt
   ```

4. **GPT-5 API Issues**
   ```bash
   # Test API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
   ```

### **Logs**
```bash
# Production logs
tail -f logs/error.log
tail -f logs/access.log

# Development logs
tail -f logs_dev/error.log
tail -f logs_dev/access.log

# Docker logs
docker-compose -f docker-compose.production.yml logs -f
docker-compose -f docker-compose.development.yml logs -f
```

## 🚀 **Deployment Workflow**

### **Development → Production Workflow**
1. **Develop** with GPT-5 features in development environment
2. **Test** thoroughly with development tools
3. **Validate** features work correctly
4. **Deploy** to production with stable features
5. **Monitor** production performance
6. **Iterate** based on feedback

### **Feature Promotion Process**
1. **Development**: Implement new GPT-5 features
2. **Testing**: Validate in development environment
3. **Stabilization**: Ensure features are production-ready
4. **Production**: Deploy stable features to production
5. **Monitoring**: Track performance and usage
6. **Optimization**: Refine based on production data

## 📋 **Environment Checklist**

### **Production Setup**
- [ ] Environment variables configured
- [ ] API keys set up
- [ ] Security settings applied
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] Error pages working
- [ ] File uploads working
- [ ] Resume generation working
- [ ] All features tested

### **Development Setup**
- [ ] GPT-5 API keys configured
- [ ] Development tools installed
- [ ] Hot reload working
- [ ] Jupyter Lab accessible
- [ ] Career advice API working
- [ ] Job analysis API working
- [ ] Debug logging enabled
- [ ] All GPT-5 features tested

---

**🎉 You now have a complete environment management system for both Production and Development with GPT-5 features!**
