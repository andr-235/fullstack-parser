# VK Parser API - Production-Ready Docker Setup

🚀 **Production-ready FastAPI backend with Docker Compose + Nginx (HTTP-only)**

## 📋 Overview

This project provides a complete production-ready setup for a FastAPI backend application with:
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker
- **Celery** - Background task processing
- **Nginx** - Reverse proxy and load balancer
- **Docker Compose** - Container orchestration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   FastAPI API   │    │   PostgreSQL    │
│  (Port 80)      │───▶│   (Port 8000)   │───▶│   (Port 5432)   │
│  Reverse Proxy  │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Celery Worker  │    │     Redis       │
                       │  Background     │───▶│   (Port 6379)   │
                       │  Tasks          │    │  Cache & Queue  │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)
- At least 2GB RAM and 1 CPU core

### 2. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd vk-parser-api

# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
```

### 3. Configure Environment

Edit `.env` file with your settings:

```bash
# Database
POSTGRES_DB=vk_parser
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# CORS (add your frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 4. Deploy

```bash
# Development deployment
docker-compose up -d

# Production deployment
./scripts/deploy.sh
```

## 📁 Project Structure

```
project/
├── backend/                 # FastAPI backend
│   ├── src/                # Source code
│   ├── Dockerfile          # Optimized production Dockerfile
│   ├── docker-entrypoint.sh # Production entrypoint script
│   └── .dockerignore       # Docker ignore file
├── nginx/                  # Nginx configuration
│   ├── nginx.conf          # Main nginx config
│   └── conf.d/             # Additional configs
├── scripts/                # Deployment scripts
│   ├── deploy.sh           # Zero-downtime deployment
│   └── backup-db.sh        # Database backup
├── docker-compose.yml      # Main compose file
├── docker-compose.prod.yml # Production overrides
├── env.example            # Environment template
└── README.md              # This file
```

## 🔧 Management Commands

### Deployment

```bash
# Deploy application
./scripts/deploy.sh

# Check deployment status
./scripts/deploy.sh status

# Check service health
./scripts/deploy.sh health

# View logs
./scripts/deploy.sh logs
```

### Database Backup

```bash
# Create backup
./scripts/backup-db.sh

# List backups
./scripts/backup-db.sh list

# Restore from backup
./scripts/backup-db.sh restore ./backups/db_backup_20240101_120000.sql.gz

# Clean old backups
./scripts/backup-db.sh cleanup
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Start with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## 🔍 Monitoring & Health Checks

### Health Endpoints

- **Application Health**: `http://localhost/health`
- **API Health**: `http://localhost/api/health`

### Service Status

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs redis
docker-compose logs nginx
```

### Logs

Logs are stored in `./logs/` directory:
- `logs/api/` - FastAPI application logs
- `logs/celery/` - Celery worker logs
- `logs/nginx/` - Nginx access and error logs

## 🔒 Security Features

### HTTP Security Headers (No SSL Required)

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: no-referrer-when-downgrade`
- `Content-Security-Policy`
- `Permissions-Policy`

### Rate Limiting

- **API endpoints**: 10 requests/second per IP
- **General endpoints**: 30 requests/second per IP

### Access Control

- Admin/debug routes restricted to localhost and private networks
- Non-root user in containers
- Minimal base images (Alpine Linux)

## 📊 Performance Optimizations

### Nginx

- Gzip compression enabled
- Connection keep-alive
- Upstream connection pooling
- Static file caching

### Database

- Connection pooling configured
- Optimized PostgreSQL settings for production
- Automated backups with retention policy

### Application

- Multi-stage Docker build
- Optimized layer caching
- Health checks for zero-downtime deployments
- Graceful shutdown handling

## 🛠️ Development

### Adding New Services

1. Add service to `docker-compose.yml`
2. Configure health checks
3. Add to network: `app-network`
4. Update dependencies if needed

### Environment Variables

All configuration is done through environment variables in `.env` file. See `env.example` for all available options.

### Database Migrations

Migrations run automatically on container startup. For manual migration:

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 80, 5432, 6379, 8000 are available
2. **Permission issues**: Ensure scripts are executable (`chmod +x scripts/*.sh`)
3. **Database connection**: Check PostgreSQL container is healthy
4. **Memory issues**: Increase Docker memory limits

### Debug Commands

```bash
# Check container health
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 -f

# Execute commands in container
docker-compose exec api bash
docker-compose exec postgres psql -U postgres -d vk_parser

# Check resource usage
docker stats
```

## 📈 Scaling

### Horizontal Scaling

To scale API instances:

```yaml
# In docker-compose.yml
api:
  deploy:
    replicas: 3
```

### Vertical Scaling

Adjust resource limits in `docker-compose.prod.yml`:

```yaml
api:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '2.0'
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        run: |
          ssh user@server "cd /path/to/project && ./scripts/deploy.sh"
```

## 📞 Support

For issues and questions:
1. Check the logs: `./scripts/deploy.sh logs`
2. Verify health: `./scripts/deploy.sh health`
3. Check service status: `docker-compose ps`

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using Docker Compose + Nginx (HTTP-only) - Production Ready 2025**