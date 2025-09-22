# Docker Deployment and Monitoring Guide

## Overview

This document describes how to deploy and monitor the VK Comments Parser Go backend using Docker Compose. The setup includes API, Worker, PostgreSQL, Redis, Prometheus, and Grafana services.

## Prerequisites

- Docker and Docker Compose installed
- Go 1.25.1+ for local development
- Git for version control

## Local Development Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd backend
```

### 2. Build and Run Services

```bash
# Build all services
make build

# Start all services in detached mode
make up

# View logs
make logs

# Stop services
make down

# Clean up (stop and remove volumes)
make clean
```

### 3. Database Migrations

```bash
make migrate
```

### 4. Testing

```bash
make test
```

## Services

### API Service

- Port: 8080
- Health check: http://localhost:8080/health
- Metrics: http://localhost:8080/metrics

### Worker Service

- Asynq worker for task processing
- No external port, monitored via health check

### PostgreSQL

- Port: 5432
- Database: vk_comments
- User: postgres
- Password: postgres

### Redis

- Port: 6379

### Prometheus

- Port: 9090
- Config: prometheus.yml
- Targets: API, Worker, Postgres exporter, Redis exporter

### Grafana

- Port: 3000
- Admin: admin / admin
- Dashboard: VK Comments Parser - Monitoring Dashboard
- Data source: Prometheus (auto-configured)

## Monitoring

### Prometheus

Access Prometheus UI at http://localhost:9090

### Grafana

Access Grafana at http://localhost:3000

- Login: admin / admin
- Dashboard: Import grafana-dashboard.json or use provisioned dashboard
- Panels: API requests, response time, Asynq queues, Postgres connections, Redis memory

### Metrics

- HTTP requests total and duration
- GORM query duration and connection pool
- Asynq queue length and processing rate
- Postgres connections and query duration
- Redis memory usage and commands rate

## Production Deployment

For production, use docker-compose.prod.yml with environment variables for secrets.

### Environment Variables

- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- JWT_SECRET
- REDIS_URL

### Scaling

- API: Scale horizontally with load balancer
- Worker: Scale workers for high load
- Postgres: Use managed service (RDS, CloudSQL)
- Redis: Use cluster for high availability

## Troubleshooting

### Services not starting

- Check Docker logs: `make logs`
- Verify ports not in use
- Check volume permissions

### Database connection issues

- Verify Postgres health: `docker-compose exec postgres pg_isready`
- Check DATABASE_URL format

### Metrics not appearing

- Verify /metrics endpoint: `curl http://localhost:8080/metrics`
- Check Prometheus targets in UI
- Ensure Prometheus scraping config

### Grafana dashboard empty

- Verify Prometheus data source in Grafana
- Check query expressions match metrics
- Wait for data accumulation

## Next Steps

1. Customize environment variables
2. Configure alerting in Prometheus
3. Set up SSL for production
4. Monitor logs and metrics regularly

For more details, see the Makefile targets and docker-compose.yml configuration.