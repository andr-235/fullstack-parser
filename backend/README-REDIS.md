# Redis Integration for VK Parser

## Overview

This project uses Redis for caching and task state management. Redis is configured to work both in development and production environments.

## Features

- **Task State Management**: Store and track parsing task progress
- **Caching**: Cache frequently accessed data
- **Queue Management**: Handle task queues for background processing
- **Health Monitoring**: Redis health checks included

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL="redis://redis:6379/0"  # Production
REDIS_URL="redis://localhost:6379" # Development
REDIS_TTL=3600                     # Cache TTL in seconds
REDIS_MAX_KEYS=1000               # Maximum cache keys
```

### Production Setup

The production Docker Compose file (`docker-compose.prod.ip.yml`) includes Redis with the following configuration:

```yaml
redis:
  image: redis:7-alpine
  command: >
    redis-server
    --appendonly yes
    --maxmemory 256mb
    --maxmemory-policy noeviction
    --save 900 1
    --save 300 10
    --save 60 10000
```

## Usage

### Basic Redis Operations

```typescript
import { RedisService } from "./common/redis";

@Injectable()
export class MyService {
  constructor(private readonly redisService: RedisService) {}

  // Cache operations
  async getData(key: string) {
    return await this.redisService.get(key);
  }

  async setData(key: string, value: any, ttl?: number) {
    await this.redisService.set(key, value, ttl);
  }

  // Task management
  async createTask(taskId: string, taskData: any) {
    await this.redisService.setTaskStatus(taskId, taskData);
  }

  async getTaskStatus(taskId: string) {
    return await this.redisService.getTaskStatus(taskId);
  }
}
```

### Task State Management

The Redis service provides specialized methods for managing parsing tasks:

- `setTaskStatus(taskId, status)` - Set task status
- `getTaskStatus(taskId)` - Get task status
- `setTaskProgress(taskId, progress)` - Update progress
- `getTaskProgress(taskId)` - Get current progress
- `setCurrentGroup(taskId, groupId)` - Set current processing group
- `incrementProcessedGroups(taskId)` - Increment processed count
- `setTaskError(taskId, error)` - Set error message
- `setTaskResults(taskId, results)` - Store task results

## Health Monitoring

The health endpoint (`/api/v1/health`) includes Redis status:

```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 123.456,
  "redis": "connected"
}
```

## Development

### Local Redis Setup

1. Install Redis locally or use Docker:

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or install locally
sudo apt-get install redis-server
```

2. Set environment variables:

```bash
REDIS_URL="redis://localhost:6379"
```

### Testing Redis Connection

```bash
# Test connection
redis-cli ping

# Check keys
redis-cli keys "*"

# Monitor operations
redis-cli monitor
```

## Production Deployment

### Docker Compose

The production setup includes:

- Redis with persistence (AOF)
- Memory limits (256MB)
- Health checks
- Proper networking

### Monitoring

- Redis Commander available at port 8081 (if enabled)
- Health checks via `/api/v1/health`
- Logging configured for production

### Backup

Redis data is persisted in Docker volumes:

```yaml
volumes:
  redis_data:
    driver: local
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if Redis is running
   - Verify REDIS_URL configuration
   - Check network connectivity

2. **Memory Issues**
   - Monitor Redis memory usage
   - Adjust maxmemory settings
   - Check for memory leaks

3. **Performance Issues**
   - Monitor Redis operations
   - Check for slow queries
   - Optimize data structures

### Debug Commands

```bash
# Check Redis info
redis-cli info

# Check memory usage
redis-cli info memory

# Check connected clients
redis-cli client list

# Monitor commands
redis-cli monitor
```

## Security

- Redis is configured without authentication in development
- Production should use Redis password
- Network isolation in Docker Compose
- Proper firewall rules recommended

## Performance Tips

1. **Use appropriate data structures**
   - Hashes for object storage
   - Lists for queues
   - Sets for unique collections

2. **Set TTL for cache entries**
   - Prevent memory leaks
   - Automatic cleanup

3. **Monitor memory usage**
   - Set maxmemory limits
   - Configure eviction policies

4. **Use pipelining for bulk operations**
   - Reduce network round trips
   - Improve performance
