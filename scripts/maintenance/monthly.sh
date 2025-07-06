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