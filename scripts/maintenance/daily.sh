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