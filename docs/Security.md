# Security Guide for Lorien API

This document outlines the comprehensive security features implemented in the Lorien API and provides guidance for secure deployment and configuration.

## Overview

The Lorien API implements multiple layers of security to protect against common web vulnerabilities and ensure secure operation in production environments.

## Security Features

### 1. Authentication & Authorization

#### Token-Based Authentication

- **Bearer Token**: All write operations require a valid Bearer token
- **Environment-Based**: Authentication requirements based on environment
- **Production Mandatory**: Authentication is mandatory in production
- **Timing Attack Protection**: Uses constant-time comparison for token validation

#### Configuration

```bash
# Required for production
ENVIRONMENT=production
AUTH_TOKEN=your-secure-random-token-here
AUTH_REQUIRED=true
```

#### Rate Limiting

- **Failed Attempts**: Tracks failed authentication attempts per IP
- **Automatic Blocking**: Blocks IPs with >5 failed attempts in 1 hour
- **Request Rate Limiting**: Configurable rate limits for API requests

### 2. Input Validation & Sanitization

#### Comprehensive Validation

- **SQL Injection Prevention**: Blocks common SQL injection patterns
- **XSS Protection**: Prevents cross-site scripting attacks
- **Path Traversal Protection**: Blocks directory traversal attempts
- **Command Injection Protection**: Prevents command injection attacks

#### Field-Specific Validation

- **Node Labels**: Validated for length and dangerous content
- **Triage Text**: Sanitized for safe storage and display
- **File Names**: Validated for path traversal safety
- **Numeric Inputs**: Type and range validation

### 3. Security Headers

#### HTTP Security Headers

- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables browser XSS filtering
- **Strict-Transport-Security**: Enforces HTTPS in production
- **Content-Security-Policy**: Restricts resource loading
- **Referrer-Policy**: Controls referrer information

#### Configuration

```bash
SECURITY_HEADERS_ENABLED=true
HSTS_MAX_AGE=31536000
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline'
```

### 4. CORS Configuration

#### Secure CORS Setup

- **Origin Restrictions**: Configurable allowed origins
- **Credential Control**: Configurable credential handling
- **Method Restrictions**: Limited to necessary HTTP methods
- **Header Restrictions**: Controlled header exposure

#### Configuration

```bash
# Production example
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_CREDENTIALS=false

# Development example
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=false
```

### 5. Request Size Limits

#### Protection Against DoS

- **Maximum Request Size**: Configurable limit (default: 10MB)
- **File Upload Limits**: Controlled file size limits
- **Memory Protection**: Prevents memory exhaustion attacks

### 6. Security Logging

#### Comprehensive Audit Trail

- **Authentication Events**: Failed attempts, successful logins
- **Security Violations**: XSS attempts, SQL injection attempts
- **Rate Limiting Events**: Rate limit violations
- **Input Validation Failures**: Malicious input attempts

#### Log Format

```json
{
  "event_type": "invalid_auth_token",
  "method": "POST",
  "path": "/api/v1/tree/parents/123/children",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "timestamp": 1640995200.0,
  "token_length": 32
}
```

## Environment Configuration

### Development Environment

```bash
ENVIRONMENT=development
AUTH_REQUIRED=false
RATE_LIMIT_ENABLED=false
SECURITY_HEADERS_ENABLED=false
CORS_ORIGINS=*
INPUT_VALIDATION_ENABLED=true
SECURITY_LOGGING_ENABLED=true
```

### Production Environment

```bash
ENVIRONMENT=production
AUTH_TOKEN=your-very-secure-random-token-here
AUTH_REQUIRED=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
CORS_ORIGINS=https://yourdomain.com
CORS_ALLOW_CREDENTIALS=false
SECURITY_HEADERS_ENABLED=true
HSTS_MAX_AGE=31536000
CONTENT_SECURITY_POLICY=default-src 'self'
INPUT_VALIDATION_ENABLED=true
MAX_REQUEST_SIZE=10485760
SECURITY_LOGGING_ENABLED=true
LOG_FAILED_AUTH_ATTEMPTS=true
```

## Security Best Practices

### 1. Token Management

- **Generate Secure Tokens**: Use cryptographically secure random generators
- **Token Rotation**: Regularly rotate authentication tokens
- **Secure Storage**: Store tokens securely, never in code
- **Environment Variables**: Use environment variables for sensitive data

### 2. Network Security

- **HTTPS Only**: Always use HTTPS in production
- **Firewall Configuration**: Restrict access to necessary ports only
- **Reverse Proxy**: Use a reverse proxy (nginx, Apache) for additional security
- **Load Balancer**: Implement load balancing for high availability

### 3. Monitoring & Alerting

- **Security Event Monitoring**: Monitor security logs for suspicious activity
- **Failed Authentication Alerts**: Set up alerts for repeated failed attempts
- **Rate Limit Violations**: Monitor rate limit violations
- **Unusual Traffic Patterns**: Watch for unusual request patterns

### 4. Regular Security Updates

- **Dependency Updates**: Keep all dependencies updated
- **Security Patches**: Apply security patches promptly
- **Vulnerability Scanning**: Regular vulnerability assessments
- **Penetration Testing**: Periodic security testing

## Security Incident Response

### 1. Detection

- Monitor security logs for suspicious activity
- Set up automated alerts for security events
- Regular review of access patterns

### 2. Response

- Immediate containment of security incidents
- Investigation and analysis of security events
- Documentation of incidents and response actions

### 3. Recovery

- Restore service to secure state
- Update security measures if needed
- Post-incident review and improvements

## Compliance Considerations

### Medical Data Protection

- **No PHI Storage**: Ensure no protected health information is stored
- **Data Minimization**: Collect only necessary data
- **Access Controls**: Implement appropriate access controls
- **Audit Trails**: Maintain comprehensive audit trails

### General Data Protection

- **Privacy by Design**: Implement privacy considerations from the start
- **Data Encryption**: Encrypt sensitive data at rest and in transit
- **Access Logging**: Log all access to sensitive data
- **Data Retention**: Implement appropriate data retention policies

## Security Testing

### 1. Automated Testing

- **Input Validation Tests**: Test all input validation functions
- **Authentication Tests**: Test authentication mechanisms
- **Authorization Tests**: Verify access controls
- **Rate Limiting Tests**: Test rate limiting functionality

### 2. Manual Testing

- **Penetration Testing**: Regular penetration tests
- **Security Code Review**: Review code for security issues
- **Configuration Review**: Review security configurations
- **Vulnerability Assessment**: Regular vulnerability assessments

## Troubleshooting Security Issues

### Common Issues

#### Authentication Failures

- Check AUTH_TOKEN environment variable
- Verify token format (Bearer <token>)
- Check rate limiting status
- Review security logs

#### CORS Issues

- Verify CORS_ORIGINS configuration
- Check CORS_ALLOW_CREDENTIALS setting
- Review browser console for CORS errors
- Test with different origins

#### Rate Limiting Issues

- Check RATE_LIMIT_ENABLED setting
- Verify RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW
- Review failed authentication attempts
- Check client IP tracking

### Debug Commands

```bash
# Check security configuration
curl -H "Authorization: Bearer $AUTH_TOKEN" http://localhost:8000/api/v1/health

# Test rate limiting
for i in {1..10}; do curl http://localhost:8000/api/v1/health; done

# Check security headers
curl -I http://localhost:8000/api/v1/health
```

## Security Contacts

For security-related issues or questions:

- **Security Team**: <security@yourdomain.com>
- **Emergency Contact**: +1-XXX-XXX-XXXX
- **Bug Bounty**: <security@yourdomain.com>

## Security Updates

This security guide is updated regularly to reflect the latest security features and best practices. Check for updates before each deployment.
