# Deployment Guide

This document provides deployment instructions and configuration options for the Lorien application.

## Deployment Options

### Local Development

See [DEVELOPMENT.md](./DEVELOPMENT.md) for local development setup.

### Production Deployment

#### Backend Deployment

1. **Environment Setup**:
   ```bash
   # Set production environment
   export LORIEN_ENV=production
   export LORIEN_DB_PATH=/var/lib/lorien/lorien.db
   export LORIEN_LOG_LEVEL=INFO
   ```

2. **Database Setup**:
   ```bash
   # Create database directory
   sudo mkdir -p /var/lib/lorien
   sudo chown lorien:lorien /var/lib/lorien
   
   # Initialize database
   python -c "from api.db import ensure_schema; ensure_schema()"
   ```

3. **Service Configuration**:
   ```bash
   # Install as systemd service
   sudo cp deployment/lorien.service /etc/systemd/system/
   sudo systemctl enable lorien
   sudo systemctl start lorien
   ```

4. **Reverse Proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

#### Frontend Deployment

1. **Build Flutter App**:
   ```bash
   cd ui_flutter
   flutter build linux --release
   ```

2. **Package for Distribution**:
   ```bash
   # Create AppImage or package for target platform
   flutter build linux --release --dart-define=API_BASE_URL=https://your-api-domain.com
   ```

### Docker Deployment

1. **Backend Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -e .[prod]
   EXPOSE 8000
   CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Docker Compose**:
   ```yaml
   version: '3.8'
   services:
     lorien-api:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./data:/var/lib/lorien
       environment:
         - LORIEN_DB_PATH=/var/lib/lorien/lorien.db
   ```

## Configuration

### Environment Variables

- `LORIEN_ENV`: Environment (development, production)
- `LORIEN_DB_PATH`: Database file path
- `LORIEN_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LORIEN_CORS_ORIGINS`: Allowed CORS origins
- `LORIEN_AUTH_TOKEN`: Optional authentication token

### Database Configuration

- **SQLite**: Default, suitable for single-instance deployments
- **WAL Mode**: Enabled by default for better concurrency
- **Foreign Keys**: Enabled by default
- **Backup**: Regular backups recommended

### Security Considerations

1. **Authentication**: Set `LORIEN_AUTH_TOKEN` for write operations
2. **CORS**: Configure `LORIEN_CORS_ORIGINS` appropriately
3. **Database**: Secure database file permissions
4. **Network**: Use HTTPS in production
5. **Updates**: Keep dependencies updated

## Monitoring

### Health Checks

- **API Health**: `GET /api/v1/health`
- **Metrics**: `GET /api/v1/health/metrics` (if enabled)

### Logging

- **Application Logs**: Check systemd journal or Docker logs
- **Database Logs**: SQLite WAL files in database directory
- **Access Logs**: Nginx or reverse proxy logs

### Backup

1. **Database Backup**:
   ```bash
   # Create backup
   sqlite3 /var/lib/lorien/lorien.db ".backup /backup/lorien-$(date +%Y%m%d).db"
   ```

2. **Automated Backup**:
   ```bash
   # Add to crontab
   0 2 * * * /usr/local/bin/lorien-backup.sh
   ```

## Troubleshooting

### Common Issues

1. **Service won't start**: Check logs with `journalctl -u lorien`
2. **Database errors**: Verify file permissions and disk space
3. **Connection refused**: Check if service is running and port is open
4. **CORS errors**: Verify `LORIEN_CORS_ORIGINS` configuration

### Performance Tuning

1. **Database**: Ensure WAL mode is enabled
2. **Memory**: Monitor memory usage, especially for large datasets
3. **Network**: Use connection pooling for high-traffic deployments
4. **Caching**: Consider Redis for session storage

### Maintenance

1. **Regular Updates**: Keep dependencies updated
2. **Database Maintenance**: Run VACUUM periodically
3. **Log Rotation**: Configure log rotation to prevent disk full
4. **Monitoring**: Set up alerts for critical metrics

## Scaling

### Horizontal Scaling

- **Load Balancer**: Use Nginx or similar
- **Multiple Instances**: Run multiple API instances
- **Database**: Consider PostgreSQL for multi-instance deployments
- **Session Storage**: Use Redis for shared session storage

### Vertical Scaling

- **CPU**: More cores for concurrent requests
- **Memory**: More RAM for larger datasets
- **Storage**: SSD for better database performance
- **Network**: Higher bandwidth for data transfer
