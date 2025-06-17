# StickForStats Production Deployment Guide

This document outlines the steps required to deploy the StickForStats platform to a production environment.

## Prerequisites

- Docker and Docker Compose
- A PostgreSQL database server
- Redis server for caching and Celery
- Domain name with SSL certificate
- Server with at least 4GB RAM and 2 CPU cores
- Object storage service (optional, for user uploads)

## Production Environment Preparation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/stickforstats.git
cd stickforstats
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Django settings
DEBUG=False
SECRET_KEY=your-secure-secret-key
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=stickforstats_production
DB_USER=stickforstats_user
DB_PASSWORD=secure-database-password
DB_HOST=postgres
DB_PORT=5432

# Cache and Celery settings
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Storage settings
USE_S3_STORAGE=False
# If USE_S3_STORAGE is True, these are required:
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=your-region

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=StickForStats <noreply@yourdomain.com>

# RAG System settings
RAG_MODEL_NAME=all-MiniLM-L6-v2
RAG_VECTOR_SIZE=384
RAG_CHUNK_SIZE=300
RAG_CHUNK_OVERLAP=50
RAG_RETRIEVAL_TOP_K=5
RAG_CACHE_EMBEDDINGS=True

# Logging settings
LOG_LEVEL=INFO
```

### 3. Configure Production Settings

Update `stickforstats/settings.py` to ensure production-ready settings:

```python
# Production-specific settings
if not DEBUG:
    # Security settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Static and Media files with S3 (if configured)
    if os.environ.get('USE_S3_STORAGE', 'False') == 'True':
        # S3 Storage settings
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
        
        AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
        AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
        
        STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    else:
        # Local storage
        STATIC_ROOT = BASE_DIR / 'static'
        STATIC_URL = '/static/'
        MEDIA_ROOT = BASE_DIR / 'media'
        MEDIA_URL = '/media/'
```

## Deployment

### 1. Update Docker Compose for Production

Create a `docker-compose.prod.yml` file:

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: docker/Dockerfile
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    restart: always
    command: gunicorn stickforstats.wsgi:application --bind 0.0.0.0:8000 --workers 4

  celery:
    build:
      context: .
      dockerfile: docker/Dockerfile
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    restart: always
    command: celery -A stickforstats worker -l info

  celery-beat:
    build:
      context: .
      dockerfile: docker/Dockerfile
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    restart: always
    command: celery -A stickforstats beat -l info

  nginx:
    image: nginx:1.21
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/static
      - media_volume:/app/media
      - ./docker/certbot/conf:/etc/letsencrypt
      - ./docker/certbot/www:/var/www/certbot
    depends_on:
      - web
    restart: always

  certbot:
    image: certbot/certbot
    volumes:
      - ./docker/certbot/conf:/etc/letsencrypt
      - ./docker/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - .env
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_DB=${DB_NAME}
    restart: always

  redis:
    image: redis:7
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### 2. Configure Nginx for SSL

Update `docker/nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    server_tokens off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;
    server_tokens off;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 50M;

    location /static/ {
        alias /app/static/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://web:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Update Dockerfile for Production

Ensure `docker/Dockerfile` is optimized for production:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn==20.1.0

# Copy project
COPY . .

# Create directory for static files
RUN mkdir -p /app/static
RUN mkdir -p /app/media

# Run entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### 4. Update Entrypoint Script

Update `docker/entrypoint.sh`:

```bash
#!/bin/bash

set -e

# Wait for postgres
until nc -z -v -w30 postgres 5432
do
  echo "Waiting for postgres..."
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for redis
until nc -z -v -w30 redis 6379
do
  echo "Waiting for redis..."
  sleep 1
done
echo "Redis is ready!"

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Register modules
python register_modules.py

# Execute command
exec "$@"
```

### 5. Set Up SSL Certificates

Run the following to obtain SSL certificates:

```bash
# Create directories for certbot
mkdir -p docker/certbot/conf
mkdir -p docker/certbot/www

# Start nginx service
docker-compose -f docker-compose.prod.yml up -d nginx

# Get certificates
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email admin@yourdomain.com --agree-tos --no-eff-email -d yourdomain.com -d www.yourdomain.com

# Reload nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 6. Database Initialization

Before the first deployment, initialize the database:

```bash
# Start the database
docker-compose -f docker-compose.prod.yml up -d postgres

# Create superuser
docker-compose -f docker-compose.prod.yml run --rm web python create_superuser.py

# Optionally load initial data
docker-compose -f docker-compose.prod.yml run --rm web python manage.py loaddata initial_data.json
```

### 7. Deploy the Application

Launch the full production stack:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring and Maintenance

### 1. Health Checks

Add monitoring endpoints to check system health:

```python
# health_check/views.py
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from redis import Redis
from redis.exceptions import RedisError
from celery.task.control import inspect

def health_check(request):
    # Check database
    db_healthy = True
    try:
        connections['default'].cursor()
    except OperationalError:
        db_healthy = False
    
    # Check Redis
    redis_healthy = True
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
    except RedisError:
        redis_healthy = False
    
    # Check Celery
    celery_healthy = True
    try:
        i = inspect()
        if not i.ping():
            celery_healthy = False
    except:
        celery_healthy = False
    
    system_healthy = all([db_healthy, redis_healthy, celery_healthy])
    
    response = {
        'status': 'healthy' if system_healthy else 'unhealthy',
        'database': 'up' if db_healthy else 'down',
        'redis': 'up' if redis_healthy else 'down',
        'celery': 'up' if celery_healthy else 'down',
    }
    
    status_code = 200 if system_healthy else 503
    
    return JsonResponse(response, status=status_code)
```

### 2. Backup Strategy

Set up regular database backups:

```bash
# Create a backup script
cat > docker/backup.sh << EOF
#!/bin/bash

TIMESTAMP=\$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"

# Ensure backup directory exists
mkdir -p \$BACKUP_DIR

# Database backup
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U \$DB_USER \$DB_NAME | gzip > "\$BACKUP_DIR/db_backup_\$TIMESTAMP.sql.gz"

# Media files backup
tar -czf "\$BACKUP_DIR/media_backup_\$TIMESTAMP.tar.gz" -C /path/to/stickforstats/media .

# Clean old backups (keep last 7 days)
find \$BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
find \$BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$TIMESTAMP"
EOF

chmod +x docker/backup.sh

# Add to crontab
echo "0 2 * * * /path/to/stickforstats/docker/backup.sh >> /path/to/stickforstats/logs/backup.log 2>&1" | crontab -
```

### 3. Log Management

Configure centralized logging:

```yaml
# Add this to docker-compose.prod.yml
services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.15.0
    volumes:
      - ./docker/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - web
      - celery
    restart: always
```

Create `docker/filebeat.yml`:

```yaml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices:
    - index: "stickforstats-%{+yyyy.MM.dd}"
```

### 4. Update Procedure

Document the update procedure:

```bash
# Pull latest changes
git pull

# Build new images
docker-compose -f docker-compose.prod.yml build

# Apply migrations (if any)
docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate

# Collect static files (if changed)
docker-compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput

# Restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## Scaling Considerations

### 1. Database Scaling

For increased database performance:

- Use database connection pooling with PgBouncer
- Set up PostgreSQL replication for read replicas
- Consider sharding for very large datasets

### 2. Horizontal Scaling

For handling more traffic:

- Add more web workers behind a load balancer
- Scale Celery workers across multiple machines
- Use a distributed cache like Redis Cluster

### 3. Content Delivery

For faster global access:

- Use a CDN for static assets
- Configure geographically distributed cache nodes
- Use edge computing for common data processing tasks

## Security Checklist

- ✅ HTTPS with valid SSL certificate
- ✅ Secure Django settings (CSRF, XSS protection, etc.)
- ✅ Database credentials stored as environment variables
- ✅ Regular security updates for all components
- ✅ Rate limiting for API endpoints
- ✅ Input validation and sanitization
- ✅ Proper authentication and authorization
- ✅ Regular security audits and vulnerability scanning

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   
   ```
   django.db.utils.OperationalError: could not connect to server: Connection refused
   ```

   Solution: Check if PostgreSQL is running and accessible from the web container.

2. **Static Files Not Loading**

   Solution: Verify STATIC_ROOT and STATIC_URL settings, and ensure `collectstatic` has been run.

3. **Celery Tasks Not Running**

   Solution: Check Redis connection and verify Celery worker is running with `docker-compose -f docker-compose.prod.yml logs celery`.

4. **SSL Certificate Issues**

   Solution: Verify certificate paths in nginx configuration and ensure certificates are renewed.

### Debugging

For advanced debugging:

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs -f web

# Access a container shell
docker-compose -f docker-compose.prod.yml exec web bash

# Run Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Check database
docker-compose -f docker-compose.prod.yml exec postgres psql -U stickforstats_user -d stickforstats_production
```

## Conclusion

Following this deployment guide will ensure a secure, scalable, and maintainable production environment for the StickForStats platform. Adjust configurations as needed for your specific infrastructure and requirements.

For additional support, refer to the project documentation or contact the development team.