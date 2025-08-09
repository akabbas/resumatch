# 🚀 ResuMatch Production Environment Setup

This guide will help you set up a production-ready environment for ResuMatch with all current features enabled.

## 📋 Current Features Enabled in Production

### ✅ **Core Features**
- **AI-Powered Resume Generation**: Intelligent resume creation based on job descriptions
- **Intelligent Skill Matching**: Advanced skill selection from comprehensive database
- **Job Title Optimization**: Smart job title adaptation for better ATS matching
- **Summary Rewriting**: Professional summary optimization based on job requirements
- **Bullet Point Enhancement**: Action verb optimization and content improvement
- **Page Optimization**: Smart content adjustment for 1-2 page resumes
- **Harvard-Style Formatting**: Professional, ATS-friendly resume templates
- **Web Interface**: Modern, responsive Bootstrap 5 interface
- **PDF Generation**: High-quality PDF output with WeasyPrint

### 🔧 **Production Features**
- **Gunicorn WSGI Server**: Multi-worker production server
- **Security Headers**: HTTPS-ready with secure cookies
- **Error Handling**: Comprehensive error pages and logging
- **Health Checks**: Production monitoring endpoints
- **Logging**: Structured logging with configurable levels
- **Monitoring**: Sentry integration for error tracking
- **Analytics**: Resume generation tracking
- **Docker Support**: Containerized deployment
- **Environment Management**: Isolated production configuration

## 🛠️ Quick Setup

### **Option 1: Virtual Environment (Recommended)**

```bash
# 1. Make scripts executable
chmod +x scripts/*.sh

# 2. Setup production environment
./scripts/setup_production.sh

# 3. Update environment configuration
cp env.production env.production.backup
# Edit env.production with your actual settings

# 4. Run production server
./scripts/run_production.sh
```

### **Option 2: Docker (Recommended for Deployment)**

```bash
# 1. Build and run with Docker Compose
docker-compose -f docker-compose.production.yml up --build

# 2. Or build manually
docker build -f Dockerfile.production -t resumatch-prod .
docker run -p 8000:8000 --env-file env.production resumatch-prod
```

## ⚙️ Configuration

### **Environment Variables (`env.production`)**

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

# Feature Flags (All Enabled)
ENABLE_ANALYTICS=True
ENABLE_MONITORING=True
ENABLE_INTELLIGENT_SKILL_MATCHING=True
ENABLE_JOB_TITLE_OPTIMIZATION=True
ENABLE_SUMMARY_OPTIMIZATION=True
ENABLE_BULLET_OPTIMIZATION=True
ENABLE_PAGE_OPTIMIZATION=True

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
PROMETHEUS_PORT=9090
```

## 🔍 Production Features

### **Health Check Endpoint**
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

### **Logging**
- **Access Logs**: `logs/access.log`
- **Error Logs**: `logs/error.log`
- **Application Logs**: Console output with structured logging

### **Security Features**
- **HTTPS Ready**: Secure cookie configuration
- **CSRF Protection**: Built-in Flask security
- **Input Validation**: Comprehensive form validation
- **File Upload Security**: Restricted file types and sizes
- **Non-root User**: Docker runs as non-root user

### **Performance Features**
- **Multi-worker**: 8 Gunicorn workers
- **Request Limits**: 1000 requests per worker
- **Timeout Handling**: 120-second request timeout
- **Resource Limits**: Memory and CPU constraints
- **Health Monitoring**: Automatic health checks

## 📊 Monitoring & Analytics

### **Sentry Integration**
```python
# Automatic error tracking
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    environment='production',
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1
)
```

### **Analytics Tracking**
```python
# Resume generation analytics
def log_resume_generation(resume_id: str, job_description_preview: str):
    logger.info(f"Resume generation analytics - ID: {resume_id}, Job: {job_description_preview}")
```

## 🐳 Docker Deployment

### **Production Dockerfile Features**
- **Multi-stage build**: Optimized for production
- **Security**: Non-root user execution
- **Health checks**: Automatic container health monitoring
- **Resource limits**: Memory and CPU constraints
- **Dependency caching**: Optimized layer caching

### **Docker Compose Services**
- **ResuMatch App**: Main application server
- **Redis**: Optional caching layer
- **PostgreSQL**: Optional analytics database

## 🔧 Troubleshooting

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Find and kill process
   lsof -ti:8000 | xargs kill -9
   ```

2. **Permission Issues**
   ```bash
   # Fix uploads directory permissions
   chmod 755 uploads
   chown -R resumatch:resumatch uploads
   ```

3. **Memory Issues**
   ```bash
   # Reduce workers for low-memory environments
   gunicorn --workers 4 --bind 0.0.0.0:8000 app_production:app
   ```

4. **NLP Model Issues**
   ```bash
   # Reinstall spaCy model
   python -m spacy download en_core_web_sm
   ```

### **Logs**
```bash
# View application logs
tail -f logs/error.log

# View access logs
tail -f logs/access.log

# Docker logs
docker-compose -f docker-compose.production.yml logs -f
```

## 🚀 Deployment Checklist

- [ ] Environment variables configured
- [ ] API keys set up (OpenAI, Sentry)
- [ ] SSL certificate configured (for HTTPS)
- [ ] Database configured (if using)
- [ ] Monitoring set up (Sentry, Prometheus)
- [ ] Backup strategy implemented
- [ ] Load balancer configured (if needed)
- [ ] Domain and DNS configured
- [ ] Health checks passing
- [ ] Error pages working
- [ ] File uploads working
- [ ] Resume generation working
- [ ] All features tested

## 📈 Performance Optimization

### **Gunicorn Settings**
```bash
--workers 8                    # Number of worker processes
--timeout 120                  # Request timeout in seconds
--max-requests 1000           # Restart workers after N requests
--max-requests-jitter 50      # Add randomness to restarts
--preload                     # Preload application code
```

### **Resource Limits**
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
    reservations:
      memory: 1G
      cpus: '1.0'
```

## 🔒 Security Checklist

- [ ] HTTPS enabled
- [ ] Secure cookies configured
- [ ] CSRF protection enabled
- [ ] Input validation implemented
- [ ] File upload restrictions
- [ ] Non-root user execution
- [ ] Environment variables secured
- [ ] Error messages sanitized
- [ ] Rate limiting (if needed)
- [ ] Security headers configured

## 📞 Support

For production issues:
1. Check logs: `logs/error.log`
2. Verify health endpoint: `/health`
3. Test resume generation
4. Check environment variables
5. Verify file permissions

---

**🎉 Your ResuMatch production environment is now ready with all current features enabled!**
