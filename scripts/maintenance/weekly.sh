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
