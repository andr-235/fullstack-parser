# Deployment Guide

## 📋 Overview

This guide covers deployment strategies for the VK Parser Frontend Angular application, including development, staging, and production environments.

## 🚀 Quick Deployment

### Prerequisites

- Node.js 18+
- npm 9+
- Docker (optional)
- Nginx (for production)

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Access application
open http://localhost:4200
```

### Production Build

```bash
# Build for production
npm run build

# Serve production build locally
npm run serve:prod
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Multi-stage build for production
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist/frontend-angular /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # Angular routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API proxy (if needed)
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  frontend:
    build: .
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend

  backend:
    image: vk-parser-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/vkparser
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=vkparser
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🌍 Environment Configuration

### Environment Files

```typescript
// src/environments/environment.ts (development)
export const environment = {
  production: false,
  apiUrl: "http://localhost:8000/api",
  version: "1.0.0",
  enableDebug: true,
  cacheTimeout: 2 * 60 * 1000, // 2 minutes
};
```

```typescript
// src/environments/environment.prod.ts (production)
export const environment = {
  production: true,
  apiUrl: "https://api.vkparser.com/api",
  version: "1.0.0",
  enableDebug: false,
  cacheTimeout: 5 * 60 * 1000, // 5 minutes
};
```

### Build Configurations

```json
// angular.json
{
  "configurations": {
    "development": {
      "optimization": false,
      "sourceMap": true,
      "extractLicenses": false
    },
    "production": {
      "optimization": true,
      "sourceMap": false,
      "extractLicenses": true,
      "budgets": [
        {
          "type": "initial",
          "maximumWarning": "2MB",
          "maximumError": "3MB"
        }
      ]
    },
    "staging": {
      "optimization": true,
      "sourceMap": true,
      "extractLicenses": true
    }
  }
}
```

## 🔧 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "18"
      - run: npm ci
      - run: npm test
      - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "18"
      - run: npm ci
      - run: npm run build -- --configuration=production
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            cd /var/www/vkparser
            git pull origin main
            npm ci
            npm run build -- --configuration=production
            sudo systemctl restart nginx
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: node:18-alpine
  script:
    - npm ci
    - npm test
    - npm run lint

build:
  stage: build
  image: node:18-alpine
  script:
    - npm ci
    - npm run build -- --configuration=production
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh $SSH_USER@$SSH_HOST "cd /var/www/vkparser && git pull && npm ci && npm run build -- --configuration=production && sudo systemctl restart nginx"
  only:
    - main
```

## 🔒 Security Configuration

### HTTPS Setup

```nginx
# SSL configuration
server {
    listen 443 ssl http2;
    server_name vkparser.com;

    ssl_certificate /etc/ssl/certs/vkparser.crt;
    ssl_certificate_key /etc/ssl/private/vkparser.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name vkparser.com;
    return 301 https://$server_name$request_uri;
}
```

### Content Security Policy

```typescript
// CSP configuration
const cspConfig = {
  "default-src": ["'self'"],
  "script-src": ["'self'", "'unsafe-inline'"],
  "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
  "font-src": ["'self'", "https://fonts.gstatic.com"],
  "img-src": ["'self'", "data:", "https:"],
  "connect-src": ["'self'", "https://api.vkparser.com"],
  "frame-ancestors": ["'none'"],
  "base-uri": ["'self'"],
  "form-action": ["'self'"],
};
```

## 📊 Monitoring & Logging

### Application Monitoring

```typescript
// Performance monitoring
import { PerformanceService } from "./core/services/performance.service";

@Component({
  selector: "app-root",
  template: "<router-outlet></router-outlet>",
})
export class AppComponent implements OnInit {
  constructor(private performanceService: PerformanceService) {}

  ngOnInit() {
    // Monitor application performance
    this.performanceService.getMetrics().subscribe((metrics) => {
      console.log("Performance metrics:", metrics);
    });

    // Monitor performance alerts
    this.performanceService.getAlerts().subscribe((alerts) => {
      alerts.forEach((alert) => {
        console.warn("Performance alert:", alert);
      });
    });
  }
}
```

### Error Tracking

```typescript
// Error handling service
@Injectable({
  providedIn: "root",
})
export class ErrorTrackingService {
  logError(error: Error, context?: any) {
    console.error("Application error:", error);

    // Send to error tracking service
    if (environment.production) {
      // Send to Sentry, LogRocket, etc.
    }
  }
}
```

## 🔄 Deployment Strategies

### Blue-Green Deployment

```bash
#!/bin/bash
# blue-green-deploy.sh

# Build new version
npm run build -- --configuration=production

# Deploy to green environment
cp -r dist/frontend-angular /var/www/vkparser-green/

# Update nginx to point to green
sed -i 's/blue/green/g' /etc/nginx/sites-available/vkparser

# Test green environment
curl -f http://localhost/green || exit 1

# Switch traffic to green
nginx -s reload

# Keep blue as backup
# rm -rf /var/www/vkparser-blue
```

### Rolling Deployment

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vkparser-frontend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: vkparser-frontend
  template:
    metadata:
      labels:
        app: vkparser-frontend
    spec:
      containers:
        - name: frontend
          image: vkparser-frontend:latest
          ports:
            - containerPort: 80
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
```

## 🧪 Testing Deployment

### Health Checks

```typescript
// Health check endpoint
@Injectable({
  providedIn: "root",
})
export class HealthCheckService {
  checkHealth(): Observable<HealthStatus> {
    return this.http.get<HealthStatus>("/api/health");
  }
}

interface HealthStatus {
  status: "healthy" | "unhealthy";
  timestamp: string;
  version: string;
  uptime: number;
}
```

### Smoke Tests

```bash
#!/bin/bash
# smoke-test.sh

# Test application loads
curl -f http://localhost/ || exit 1

# Test API connectivity
curl -f http://localhost/api/health || exit 1

# Test authentication
curl -f http://localhost/api/auth/status || exit 1

echo "Smoke tests passed"
```

## 📈 Performance Optimization

### Bundle Analysis

```bash
# Analyze bundle size
npm run build -- --stats-json
npx webpack-bundle-analyzer dist/frontend-angular/stats.json

# Optimize bundle
npm run build -- --configuration=production --optimization
```

### Caching Strategy

```nginx
# Cache configuration
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(html)$ {
    expires 1h;
    add_header Cache-Control "public, must-revalidate";
}
```

## 🆘 Troubleshooting

### Common Issues

#### Build Failures

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version

# Check Angular CLI
ng version
```

#### Runtime Errors

```bash
# Check browser console
# Check network tab
# Check application logs
```

#### Performance Issues

```bash
# Monitor bundle size
npm run build -- --stats-json

# Check memory usage
# Monitor API response times
```

---

**Last Updated**: 2024  
**Version**: 1.0.0
