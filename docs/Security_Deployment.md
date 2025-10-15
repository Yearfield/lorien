# Security Deployment Guide

This guide provides step-by-step instructions for securely deploying the Lorien API with all security features enabled.

## Pre-Deployment Security Checklist

### 1. Environment Configuration

#### Required Environment Variables

```bash
# Production Environment
ENVIRONMENT=production
AUTH_TOKEN=your-secure-random-token-here
AUTH_REQUIRED=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_CREDENTIALS=false

# Security Headers
SECURITY_HEADERS_ENABLED=true
HSTS_MAX_AGE=31536000
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline'

# Input Validation
INPUT_VALIDATION_ENABLED=true
MAX_REQUEST_SIZE=10485760

# Security Logging
SECURITY_LOGGING_ENABLED=true
LOG_FAILED_AUTH_ATTEMPTS=true
```

### 2. Token Generation

#### Generate Secure Authentication Token

```bash
# Using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32

# Using /dev/urandom
head -c 32 /dev/urandom | base64
```

#### Store Token Securely

```bash
# Set environment variable
export AUTH_TOKEN="your-generated-token-here"

# Or add to .env file (never commit to version control)
echo "AUTH_TOKEN=your-generated-token-here" >> .env
```

### 3. Database Security

#### SQLite Security Configuration

```bash
# Set secure database path
export LORIEN_DB_PATH="/secure/path/to/lorien.db"

# Set proper permissions
chmod 600 /secure/path/to/lorien.db
chown lorien:lorien /secure/path/to/lorien.db
```

### 4. Network Security

#### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

#### Reverse Proxy Configuration (nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

## Deployment Steps

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

### 2. Configure SSL Certificate

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d app.yourdomain.com

# Set up automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Deploy Application

```bash
# Create application directory
sudo mkdir -p /opt/lorien
sudo chown lorien:lorien /opt/lorien

# Copy application files
sudo cp -r . /opt/lorien/
cd /opt/lorien

# Set up environment
sudo cp security.env.example .env
sudo nano .env  # Configure environment variables

# Install dependencies
pip install -r requirements.txt
```

### 4. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/lorien.service
```

```ini
[Unit]
Description=Lorien API
After=network.target

[Service]
Type=exec
User=lorien
Group=lorien
WorkingDirectory=/opt/lorien
Environment=PATH=/opt/lorien/.venv/bin
EnvironmentFile=/opt/lorien/.env
ExecStart=/opt/lorien/.venv/bin/uvicorn api.app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable lorien
sudo systemctl start lorien
sudo systemctl status lorien
```

### 5. Configure Logging

```bash
# Create log directory
sudo mkdir -p /var/log/lorien
sudo chown lorien:lorien /var/log/lorien

# Configure logrotate
sudo nano /etc/logrotate.d/lorien
```

```
/var/log/lorien/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 lorien lorien
    postrotate
        systemctl reload lorien
    endscript
}
```

## Post-Deployment Security Verification

### 1. Security Headers Test

```bash
# Test security headers
curl -I https://yourdomain.com/api/v1/health

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 2. Authentication Test

```bash
# Test without authentication (should fail for write operations)
curl -X POST https://yourdomain.com/api/v1/import/preview

# Test with authentication (should work)
curl -X POST \
  -H "Authorization: Bearer your-token-here" \
  https://yourdomain.com/api/v1/import/preview
```

### 3. CORS Test

```bash
# Test CORS from browser console
fetch('https://yourdomain.com/api/v1/health', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### 4. Rate Limiting Test

```bash
# Test rate limiting
for i in {1..20}; do
  curl -H "Authorization: Bearer invalid-token" \
    https://yourdomain.com/api/v1/import/preview
  echo "Request $i"
done
```

### 5. Input Validation Test

```bash
# Test XSS protection
curl -X POST \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"label": "<script>alert(\"xss\")</script>"}' \
  https://yourdomain.com/api/v1/tree/parents/1/children
```

## Monitoring and Alerting

### 1. Security Event Monitoring

```bash
# Monitor security logs
tail -f /var/log/lorien/security.log | grep -E "(invalid_auth_token|rate_limited|suspicious_input)"

# Set up log monitoring
sudo apt-get install -y fail2ban
sudo nano /etc/fail2ban/jail.local
```

```ini
[lorien-auth]
enabled = true
port = 443
filter = lorien-auth
logpath = /var/log/lorien/security.log
maxretry = 5
bantime = 3600
findtime = 600
```

### 2. Health Monitoring

```bash
# Set up health check monitoring
curl -f https://yourdomain.com/api/v1/health || echo "API is down"

# Set up cron job for monitoring
crontab -e
# Add: */5 * * * * curl -f https://yourdomain.com/api/v1/health || echo "API is down" | mail -s "Lorien API Down" admin@yourdomain.com
```

### 3. Performance Monitoring

```bash
# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/api/v1/health
```

Create `curl-format.txt`:

```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

## Security Maintenance

### 1. Regular Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update application
git pull origin main
pip install -r requirements.txt
sudo systemctl restart lorien
```

### 2. Security Audits

```bash
# Run security audit
pip install pip-audit
pip-audit

# Check for vulnerabilities
sudo apt-get install -y lynis
sudo lynis audit system
```

### 3. Backup Security

```bash
# Backup database
cp /secure/path/to/lorien.db /backup/lorien-$(date +%Y%m%d).db

# Backup configuration
tar -czf /backup/lorien-config-$(date +%Y%m%d).tar.gz /opt/lorien/.env /etc/nginx/sites-available/lorien
```

## Troubleshooting

### Common Issues

#### 1. Authentication Not Working

```bash
# Check environment variables
sudo systemctl show lorien --property=Environment

# Check logs
sudo journalctl -u lorien -f

# Test token manually
python3 -c "import os; print(os.getenv('AUTH_TOKEN'))"
```

#### 2. CORS Issues

```bash
# Check CORS configuration
curl -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Requested-With" \
  -X OPTIONS \
  https://yourdomain.com/api/v1/health
```

#### 3. Rate Limiting Issues

```bash
# Check rate limiting logs
grep "rate_limited" /var/log/lorien/security.log

# Reset rate limiting (if needed)
sudo systemctl restart lorien
```

#### 4. SSL Issues

```bash
# Check SSL certificate
openssl x509 -in /path/to/certificate.crt -text -noout

# Test SSL configuration
curl -I https://yourdomain.com/api/v1/health
```

## Emergency Procedures

### 1. Security Incident Response

```bash
# Block suspicious IP
sudo ufw deny from suspicious-ip-address

# Restart service
sudo systemctl restart lorien

# Check logs
sudo journalctl -u lorien --since "1 hour ago"
```

### 2. Service Recovery

```bash
# Stop service
sudo systemctl stop lorien

# Restore from backup
cp /backup/lorien-$(date +%Y%m%d).db /secure/path/to/lorien.db

# Restart service
sudo systemctl start lorien
```

### 3. Rollback Procedure

```bash
# Rollback to previous version
git checkout previous-stable-tag
pip install -r requirements.txt
sudo systemctl restart lorien
```

## Contact Information

For security-related issues:

- **Security Team**: <security@yourdomain.com>
- **Emergency Contact**: +1-XXX-XXX-XXXX
- **Incident Response**: <incident@yourdomain.com>

Remember to update contact information for your organization.
