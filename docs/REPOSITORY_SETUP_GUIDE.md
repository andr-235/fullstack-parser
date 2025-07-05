# 🏗️ Полное руководство по настройке репозитория

## 📋 Содержание

1. [Branch Protection Rules](#branch-protection-rules)
2. [GitHub Actions Workflows](#github-actions-workflows)
3. [Security Configuration](#security-configuration)
4. [Environment Setup](#environment-setup)
5. [Team Management](#team-management)
6. [Deployment Configuration](#deployment-configuration)
7. [Monitoring & Alerts](#monitoring-alerts)
8. [Maintenance](#maintenance)

---

## 🛡️ Branch Protection Rules

### 1. Main Branch Protection

Перейдите в **Settings → Branches → Add rule** для ветки `main`:

#### ✅ Основные настройки:
```yaml
Branch name pattern: main
Require a pull request before merging: ✅
  Require approvals: 1
  Dismiss stale reviews when new commits are pushed: ✅
  Require review from code owners: ✅
Require status checks to pass before merging: ✅
  Require branches to be up to date before merging: ✅
  Status checks:
    - "🔄 Continuous Integration / ci-success"
    - "🔒 Security Scanning / security-summary"
    - "🎯 Quality Gate / quality-gate"
Require conversation resolution before merging: ✅
Require signed commits: ✅ (рекомендуется)
Require linear history: ✅
Include administrators: ✅
Allow force pushes: ❌
Allow deletions: ❌
```

### 2. Develop Branch Protection

Аналогично настройте для ветки `develop`:

```yaml
Branch name pattern: develop
Require a pull request before merging: ✅
  Require approvals: 1
  Dismiss stale reviews when new commits are pushed: ✅
Require status checks to pass before merging: ✅
  Status checks:
    - "🔄 Continuous Integration / ci-success"
    - "🔒 Security Scanning / security-summary"
Require conversation resolution before merging: ✅
Include administrators: ❌
Allow force pushes: ❌
Allow deletions: ❌
```

### 3. Feature Branch Pattern

Для веток типа `feature/*`, `fix/*`, `hotfix/*`:

```yaml
Branch name pattern: feature/*
Require a pull request before merging: ✅
  Require approvals: 1
Require status checks to pass before merging: ✅
  Status checks:
    - "🔄 Continuous Integration / ci-success"
```

---

## ⚙️ GitHub Actions Workflows

### 1. Required Status Checks

В Branch Protection Rules добавьте точные названия jobs:

#### 🔄 CI Workflow (`ci.yml`):
- `🔍 Detect Changes / changes`
- `🐍 Backend Tests / backend-test`
- `⚛️ Frontend Tests / frontend-test`
- `🐳 Docker Build Test / docker-test`
- `🎯 Quality Gate / quality-gate`
- `🔗 Integration Test / integration-test`
- `✅ CI Success / ci-success`

#### 🔒 Security Workflow (`security.yml`):
- `🔍 CodeQL Analysis / codeql`
- `🛡️ Trivy Security Scan / trivy`
- `📦 Dependency Scanning / dependency-scan`
- `🔐 Secret Scanning / secret-scan`
- `🐳 Docker Security Scan / docker-scan`
- `📊 Security Summary / security-summary`

### 2. Workflow Secrets

Настройте следующие secrets в **Settings → Secrets and variables → Actions**:

```yaml
# Container Registry
REGISTRY_USERNAME: ghcr.io username
REGISTRY_TOKEN: GitHub Personal Access Token

# Deployment
SSH_PRIVATE_KEY: SSH key for deployment servers
STAGING_HOST: staging server hostname
PRODUCTION_HOST: production server hostname

# Database
DATABASE_URL: production database connection
REDIS_URL: production redis connection

# API Keys
VK_API_KEY: VK API access token
VK_SERVICE_KEY: VK service key

# Monitoring
SENTRY_DSN: Sentry error tracking DSN
DATADOG_API_KEY: DataDog monitoring key

# Notifications
SLACK_WEBHOOK_URL: Slack notifications webhook
TEAMS_WEBHOOK_URL: Microsoft Teams webhook
EMAIL_SMTP_PASSWORD: SMTP password for email notifications
```

### 3. Environment Variables

Настройте variables в **Settings → Secrets and variables → Actions**:

```yaml
# Application
ENVIRONMENT: production
DEBUG: false
LOG_LEVEL: INFO

# URLs
FRONTEND_URL: https://your-domain.com
BACKEND_URL: https://api.your-domain.com

# Features
ENABLE_RATE_LIMITING: true
ENABLE_MONITORING: true
ENABLE_CACHING: true
```

---

## 🔒 Security Configuration

### 1. GitHub Security Features

Включите в **Settings → Security**:

#### 🛡️ Security & analysis:
```yaml
Dependency graph: ✅
Dependabot alerts: ✅
Dependabot security updates: ✅
Code scanning alerts: ✅
Secret scanning alerts: ✅
```

#### 🔐 Advanced security features:
```yaml
Secret scanning push protection: ✅
Dependency review: ✅
```

### 2. CodeQL Setup

Создайте `.github/codeql/codeql-config.yml`:

```yaml
name: "CodeQL Config"
disable-default-queries: false
queries:
  - uses: security-and-quality
  - uses: security-extended
paths-ignore:
  - "tests/"
  - "**/*.test.ts"
  - "**/*.test.js"
  - "node_modules/"
  - ".venv/"
```

### 3. Security Policy

Убедитесь, что файл `.github/SECURITY.md` содержит:
- Поддерживаемые версии
- Процедуру отчета о уязвимостях
- Контактную информацию
- Timeline response

---

## 🌍 Environment Setup

### 1. GitHub Environments

Создайте environments в **Settings → Environments**:

#### 🧪 Staging Environment:
```yaml
Environment name: staging
Deployment branches: main, develop
Required reviewers: (не требуется)
Environment secrets:
  - DATABASE_URL: staging database
  - REDIS_URL: staging redis
  - VK_API_KEY: staging VK API key
Environment variables:
  - ENVIRONMENT: staging
  - DEBUG: true
  - LOG_LEVEL: DEBUG
```

#### 🏭 Production Environment:
```yaml
Environment name: production
Deployment branches: main (only)
Required reviewers: @andr-235, @team-lead
Wait timer: 5 minutes
Environment secrets:
  - DATABASE_URL: production database
  - REDIS_URL: production redis
  - VK_API_KEY: production VK API key
Environment variables:
  - ENVIRONMENT: production
  - DEBUG: false
  - LOG_LEVEL: INFO
```

### 2. Environment Files

Создайте конфигурации для каждого environment:

#### `environments/staging/.env.staging`:
```bash
# Staging Environment Configuration
ENVIRONMENT=staging
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://staging_user:staging_pass@staging-db:5432/vk_parser_staging
REDIS_URL=redis://staging-redis:6379

# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8001
BACKEND_URL=http://backend:8000

# VK API
VK_API_VERSION=5.131
VK_RATE_LIMIT=3

# Features
ENABLE_RATE_LIMITING=false
ENABLE_MONITORING=true
ENABLE_CACHING=true
```

#### `environments/production/.env.production`:
```bash
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database (use secrets)
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}

# API URLs
NEXT_PUBLIC_API_URL=https://api.your-domain.com
BACKEND_URL=https://api.your-domain.com

# VK API (use secrets)
VK_API_KEY=${VK_API_KEY}
VK_API_VERSION=5.131
VK_RATE_LIMIT=20

# Features
ENABLE_RATE_LIMITING=true
ENABLE_MONITORING=true
ENABLE_CACHING=true
```

---

## 👥 Team Management

### 1. Team Structure

Создайте teams в **Organization Settings → Teams**:

#### 🔧 Developers Team:
```yaml
Team name: developers
Members: @andr-235, @developer1, @developer2
Permissions: Write
Responsibilities:
  - Code development
  - Code reviews
  - Bug fixes
  - Feature implementation
```

#### 🛡️ Security Team:
```yaml
Team name: security
Members: @security-lead, @devops-lead
Permissions: Admin
Responsibilities:
  - Security reviews
  - Vulnerability management
  - Security policy updates
  - Incident response
```

#### 🚀 DevOps Team:
```yaml
Team name: devops
Members: @devops-lead, @andr-235
Permissions: Admin
Responsibilities:
  - Infrastructure management
  - Deployment approvals
  - Monitoring setup
  - Performance optimization
```

### 2. CODEOWNERS Setup

Обновите `.github/CODEOWNERS`:

```bash
# Global owners
* @andr-235

# Backend code
/backend/ @developers @andr-235
/backend/app/core/ @security @andr-235
/backend/app/models/ @developers @andr-235

# Frontend code
/frontend/ @developers @andr-235
/frontend/app/ @developers @andr-235

# Infrastructure
/docker-compose*.yml @devops @andr-235
/Dockerfile* @devops @andr-235
/.github/workflows/ @devops @andr-235
/scripts/ @devops @andr-235

# Security
/.github/SECURITY.md @security @andr-235
/.github/dependabot.yml @security @andr-235

# Documentation
/docs/ @developers @andr-235
README.md @andr-235
```

### 3. Issue Templates

Создайте в `.github/ISSUE_TEMPLATE/`:

#### `bug_report.yml`:
```yaml
name: 🐛 Bug Report
description: Report a bug to help us improve
title: "[BUG] "
labels: ["bug", "needs-triage"]
assignees: ["andr-235"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: Also tell us, what did you expect to happen?
      placeholder: Tell us what you see!
    validations:
      required: true
  - type: dropdown
    id: version
    attributes:
      label: Version
      description: What version are you running?
      options:
        - 1.0.0 (Default)
        - 1.1.0
        - 2.0.0
    validations:
      required: true
```

---

## 🚀 Deployment Configuration

### 1. Docker Registry Setup

#### GitHub Container Registry:
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag and push images
docker tag backend:latest ghcr.io/your-org/fullstack-parser/backend:latest
docker tag frontend:latest ghcr.io/your-org/fullstack-parser/frontend:latest

docker push ghcr.io/your-org/fullstack-parser/backend:latest
docker push ghcr.io/your-org/fullstack-parser/frontend:latest
```

### 2. Server Setup

#### Staging Server:
```bash
# SSH to staging server
ssh staging-server

# Create application directory
sudo mkdir -p /opt/vk-parser-staging
sudo chown $USER:$USER /opt/vk-parser-staging
cd /opt/vk-parser-staging

# Clone deployment files
git clone https://github.com/your-org/fullstack-parser.git .
cp environments/staging/.env.staging .env

# Start services
docker-compose -f docker-compose.yml up -d
```

#### Production Server:
```bash
# SSH to production server
ssh production-server

# Create application directory
sudo mkdir -p /opt/vk-parser
sudo chown $USER:$USER /opt/vk-parser
cd /opt/vk-parser

# Clone deployment files
git clone https://github.com/your-org/fullstack-parser.git .
cp environments/production/.env.production .env

# Start services with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Deployment Scripts

Создайте в `scripts/deploy/`:

#### `deploy-staging.sh`:
```bash
#!/bin/bash
set -e

echo "🚀 Deploying to staging..."

# Pull latest images
docker-compose -f docker-compose.yml pull

# Update services with zero downtime
docker-compose -f docker-compose.yml up -d --remove-orphans

# Health check
timeout 60 bash -c 'until curl -f http://localhost:8001/api/v1/health > /dev/null 2>&1; do sleep 2; done'
timeout 60 bash -c 'until curl -f http://localhost:3001 > /dev/null 2>&1; do sleep 2; done'

echo "✅ Staging deployment completed"
```

#### `deploy-production.sh`:
```bash
#!/bin/bash
set -e

echo "🏭 Deploying to production..."

# Backup current state
./scripts/backup.sh

# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Blue-green deployment
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Health check
timeout 120 bash -c 'until curl -f https://api.your-domain.com/health > /dev/null 2>&1; do sleep 5; done'
timeout 120 bash -c 'until curl -f https://your-domain.com > /dev/null 2>&1; do sleep 5; done'

echo "✅ Production deployment completed"
```

---

## 📊 Monitoring & Alerts

### 1. Health Check Endpoints

Добавьте в backend (`app/api/v1/health.py`):

```python
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.database import SessionLocal
import redis

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Database check
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.Redis(host="redis", port=6379, db=0)
        r.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
```

### 2. Monitoring Setup

#### Prometheus Configuration (`monitoring/prometheus.yml`):
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/api/metrics'
```

#### Grafana Dashboard:
```json
{
  "dashboard": {
    "title": "VK Parser Monitoring",
    "panels": [
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m])"
          }
        ]
      }
    ]
  }
}
```

### 3. Alert Rules

#### Alertmanager (`monitoring/alerts.yml`):
```yaml
groups:
  - name: vk-parser-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
          description: "PostgreSQL database is not responding"
```

---

## 🔧 Maintenance

### 1. Daily Tasks

```bash
#!/bin/bash
# Daily maintenance script

# Check system health
curl -f http://localhost:8000/api/v1/health

# Clean up Docker
docker system prune -f

# Rotate logs
logrotate /etc/logrotate.d/vk-parser

# Check disk space
df -h | grep -E "8[0-9]%|9[0-9]%" && echo "Warning: Disk space low"
```

### 2. Weekly Tasks

```bash
#!/bin/bash
# Weekly maintenance script

# Update dependencies
dependabot preview-update

# Security scan
trivy repo .

# Performance test
k6 run tests/performance/load-test.js

# Backup verification
./scripts/verify-backup.sh
```

### 3. Monthly Tasks

```bash
#!/bin/bash
# Monthly maintenance script

# Security audit
npm audit --audit-level moderate
safety check -r requirements.txt

# Certificate check
openssl x509 -in /etc/ssl/certs/domain.crt -noout -dates

# Performance review
echo "Review performance metrics in Grafana"
echo "Check error rates and response times"
```

---

## 📚 Quick Reference

### 🎯 Essential Commands

```bash
# Development
docker-compose up -d                # Start development environment
docker-compose logs -f backend      # View backend logs
docker-compose exec backend pytest  # Run backend tests

# Staging deployment
git push origin main                 # Triggers automatic staging deployment
./scripts/deploy/health-check.sh    # Manual health check

# Production deployment
git tag v1.0.0                      # Create release tag
git push origin v1.0.0              # Triggers production deployment

# Security
trivy repo .                        # Security scan
safety check -r requirements.txt    # Python dependencies check
npm audit                          # Node.js dependencies check

# Monitoring
curl http://localhost:8000/api/v1/health  # Health check
docker stats                             # Resource usage
docker-compose logs --tail=100           # Recent logs
```

### 🔗 Important URLs

- **GitHub Repository**: `https://github.com/your-org/fullstack-parser`
- **Actions**: `https://github.com/your-org/fullstack-parser/actions`
- **Security**: `https://github.com/your-org/fullstack-parser/security`
- **Staging**: `http://staging.your-domain.com`
- **Production**: `https://your-domain.com`
- **Monitoring**: `https://grafana.your-domain.com`

---

**📅 Last Updated**: January 2025  
**👤 Maintained by**: @andr-235  
**📧 Questions**: admin@your-domain.com 