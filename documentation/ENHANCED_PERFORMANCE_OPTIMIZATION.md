# Enhanced Performance Optimization Guide for Production

This document builds on the existing performance optimization guide, providing additional strategies specifically for production deployment of the StickForStats platform.

## Table of Contents

1. [Overview](#overview)
2. [Production Server Configuration](#production-server-configuration)
3. [Docker Optimization](#docker-optimization)
4. [PostgreSQL with pgvector Optimization](#postgresql-with-pgvector-optimization)
5. [Advanced Caching Strategies](#advanced-caching-strategies)
6. [CDN Integration](#cdn-integration)
7. [WebSocket Optimization](#websocket-optimization)
8. [Resource Monitoring and Auto-scaling](#resource-monitoring-and-auto-scaling)
9. [Security and Performance](#security-and-performance)
10. [Continuous Performance Improvement](#continuous-performance-improvement)

## Overview

While the existing performance optimization guide focuses on code-level improvements, this document addresses system-level and infrastructure optimizations crucial for production deployment. These enhancements build on the existing strategies to create a high-performance, scalable, and resilient production environment.

## Production Server Configuration

### Gunicorn and Uvicorn Optimization

For Django-based applications with WebSocket support:

```python
# gunicorn.conf.py for production

import multiprocessing

# General configuration
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 2

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "warning"

# Worker configurations
worker_connections = 1000
worker_tmp_dir = "/dev/shm"  # Use shared memory for worker temp files

# Load application faster
preload_app = True

# Performance tuning
forwarded_allow_ips = "*"  # Trust X-Forwarded-* headers

def post_fork(server, worker):
    # Optimize worker settings after fork
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_int(worker):
    # Prepare for worker shutdown
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    # Handle worker abort
    worker.log.info("Worker received SIGABRT signal")
```

### Nginx Configuration for Static Files and Caching

```nginx
# /etc/nginx/conf.d/stickforstats.conf

# Cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=stickforstats_cache:10m max_size=1g inactive=60m;
proxy_temp_path /var/cache/nginx/temp;

# Compression
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
gzip_min_length 1000;
gzip_proxied any;
gzip_vary on;

server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # HSTS (15768000 seconds = 6 months)
    add_header Strict-Transport-Security "max-age=15768000; includeSubDomains" always;

    # Client max body size for file uploads
    client_max_body_size 100M;

    # Static files with aggressive caching
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000, immutable";
        access_log off;
    }

    # Media files with moderate caching
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    # API endpoints with appropriate caching
    location /api/ {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        
        # Cache GET requests
        proxy_cache stickforstats_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_methods GET;
        proxy_cache_bypass $http_cache_control;
        add_header X-Cache-Status $upstream_cache_status;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
    }

    # WebSockets endpoint
    location /ws/ {
        proxy_pass http://asgi:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Frontend app with HTML5 history mode support
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Cache HTML responses for a short period
        proxy_cache stickforstats_cache;
        proxy_cache_valid 200 1m;
    }
}
```

## Docker Optimization

### Multi-stage Build for Frontend

```dockerfile
# Frontend Dockerfile with multi-stage build
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:1.25-alpine

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx conf
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Optimized Django Container

```dockerfile
# Backend Dockerfile with optimization
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app

# Create app user
RUN addgroup --system app && adduser --system --group app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs
RUN chown -R app:app /app/staticfiles /app/media /app/logs

# Set correct permissions
RUN chmod -R 755 /app/staticfiles /app/media /app/logs
RUN chmod +x /app/docker/entrypoint.sh

# Switch to app user
USER app

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

# Expose port
EXPOSE 8000

# Run entrypoint script
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Default command
CMD ["gunicorn", "stickforstats.wsgi:application", "--config", "gunicorn.conf.py"]
```

### Docker Compose Resource Limits

Add resource limits to your docker-compose.prod.yml file:

```yaml
services:
  web:
    # ... other configurations ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
  
  asgi:
    # ... other configurations ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
  
  celery:
    # ... other configurations ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## PostgreSQL with pgvector Optimization

### Configuration Optimization

Create a custom PostgreSQL configuration file to be mounted in your Docker container:

```
# postgresql.conf optimizations

# Connection Settings
max_connections = 200
superuser_reserved_connections = 3

# Memory Settings
shared_buffers = 2GB                      # 25% of available RAM
work_mem = 32MB                           # for complex queries
maintenance_work_mem = 256MB              # for maintenance operations
effective_cache_size = 6GB                # 75% of available RAM

# Background Writer
bgwriter_delay = 200ms
bgwriter_lru_maxpages = 100
bgwriter_lru_multiplier = 2.0

# WAL Settings
wal_buffers = 16MB
checkpoint_timeout = 15min
max_wal_size = 2GB
min_wal_size = 1GB

# Query Planner
random_page_cost = 1.1                    # SSD storage (default 4.0)
effective_io_concurrency = 200            # SSD storage
default_statistics_target = 100
constraint_exclusion = partition

# Autovacuum Settings
autovacuum = on
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
autovacuum_vacuum_cost_delay = 10ms
autovacuum_vacuum_cost_limit = 1000

# pgvector specific optimizations
# Enable auto-index maintenance for vector columns
maintenance_io_concurrency = 200
```

### Optimizing pgvector Indices

For the RAG system using pgvector:

```sql
-- Create optimized index for vector search
-- For approximate nearest neighbor (ANN) search
CREATE INDEX IF NOT EXISTS idx_document_embedding_ann ON rag_system_document USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- For exact nearest neighbor search (slower but more accurate)
CREATE INDEX IF NOT EXISTS idx_document_embedding_exact ON rag_system_document USING vector (embedding);

-- For filtering by category with vector search
CREATE INDEX IF NOT EXISTS idx_document_category_embedding ON rag_system_document USING btree (category) INCLUDE (embedding);
```

### Connection Pooling with PgBouncer

Add PgBouncer configuration to your production setup:

```ini
# pgbouncer.ini
[databases]
stickforstats = host=db port=5432 dbname=stickforstats

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 10
reserve_pool_timeout = 5.0
server_reset_query = DISCARD ALL
server_check_query = SELECT 1
server_lifetime = 3600
server_idle_timeout = 600
log_connections = 0
log_disconnections = 0
application_name_add_host = 1
```

Update your Django database settings to use PgBouncer:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'stickforstats'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'pgbouncer'),  # Use PgBouncer instead of direct db
        'PORT': os.environ.get('DB_PORT', '6432'),       # PgBouncer port
        'CONN_MAX_AGE': 0,  # Disable persistent connections with connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
            'application_name': 'stickforstats',
        },
    }
}
```

## Advanced Caching Strategies

### Redis Cache Configuration

```python
# settings.py extended Redis configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.msgpack.MSGPackSerializer',
        },
        'KEY_PREFIX': 'stickforstats',
        'TIMEOUT': 3600,  # 1 hour default timeout
    },
    'statistical': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.msgpack.MSGPackSerializer',
        },
        'KEY_PREFIX': 'stats',
        'TIMEOUT': 86400,  # 24 hours for statistical results
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24 hours for sessions
    },
}

# Use Redis as session store
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Site-wide cache middleware for non-authenticated pages
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # Must be first
    # ...other middleware...
    'django.middleware.cache.FetchFromCacheMiddleware',  # Must be last
]

# Cache settings for middleware
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'stickforstats_page'
```

### API Result Versioning with ETags

```python
# utils/etag.py
from django.utils.http import quote_etag
from rest_framework.response import Response

def etag_decorator(etag_func):
    """Decorator for DRF views to support ETags."""
    def decorator(view_func):
        def wrapped_view(self, request, *args, **kwargs):
            # Get the ETag for this request
            etag = etag_func(request, *args, **kwargs)
            if etag:
                etag = quote_etag(etag)
                
                # Check If-None-Match header
                if_none_match = request.META.get('HTTP_IF_NONE_MATCH', '')
                if if_none_match and if_none_match == etag:
                    # Resource not modified
                    return Response(status=304)
            
            # Process the view as normal
            response = view_func(self, request, *args, **kwargs)
            
            # Add ETag header to response
            if etag:
                response['ETag'] = etag
                
            return response
        return wrapped_view
    return decorator

# Usage in views
from .utils.etag import etag_decorator

def dataset_etag(request, pk=None):
    """Generate ETag for dataset view."""
    try:
        dataset = Dataset.objects.get(pk=pk)
        return f"{pk}-{dataset.updated_at.isoformat()}-{dataset.version}"
    except Dataset.DoesNotExist:
        return None

class DatasetViewSet(viewsets.ModelViewSet):
    # ... other configuration ...
    
    @etag_decorator(dataset_etag)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

## CDN Integration

### CloudFront/Cloudflare Configuration

1. **Update Django settings for CDN**:

```python
# settings.py
if not DEBUG:
    # Static files with CDN
    AWS_S3_CUSTOM_DOMAIN = 'cdn.example.com'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    
    # Security settings for CDN
    CSRF_TRUSTED_ORIGINS = ['https://example.com', 'https://cdn.example.com']
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

2. **Configure static files to use optimal cache headers**:

```python
# settings.py
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400,public',
}

# Different cache control for different file types
STATICFILES_STORAGE = 'stickforstats.storage.OptimizedStaticFilesStorage'

# storage.py
from storages.backends.s3boto3 import S3Boto3Storage

class OptimizedStaticFilesStorage(S3Boto3Storage):
    location = 'static'
    
    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        
        # Set different cache headers based on file extension
        if name.endswith('.css') or name.endswith('.js'):
            # Versioned assets can have longer cache
            params['CacheControl'] = 'max-age=31536000,public,immutable'
        elif name.endswith('.png') or name.endswith('.jpg') or name.endswith('.webp'):
            # Images can have longer cache
            params['CacheControl'] = 'max-age=604800,public'
        else:
            # Default cache control
            params['CacheControl'] = 'max-age=86400,public'
            
        return params
```

## WebSocket Optimization

### ASGI Server Configuration

```python
# Additional ASGI server configuration
# asgi_config.py

from uvicorn.config import Config

class OptimizedASGIConfig(Config):
    """Optimized ASGI server configuration."""
    
    def __init__(self, app, **kwargs):
        # Set optimized defaults
        kwargs.setdefault('host', '0.0.0.0')
        kwargs.setdefault('port', 8001)
        kwargs.setdefault('workers', 4)
        kwargs.setdefault('loop', 'uvloop')
        kwargs.setdefault('http', 'httptools')
        kwargs.setdefault('lifespan', 'on')
        kwargs.setdefault('log_level', 'warning')
        kwargs.setdefault('access_log', False)
        kwargs.setdefault('proxy_headers', True)
        kwargs.setdefault('forwarded_allow_ips', '*')
        kwargs.setdefault('ws_max_size', 16 * 1024 * 1024)  # 16MB max message size
        kwargs.setdefault('ws_ping_interval', 20.0)  # Send ping every 20 seconds
        kwargs.setdefault('ws_ping_timeout', 30.0)  # Wait 30 seconds for pong
        
        super().__init__(app, **kwargs)
```

### WebSocket Consumer Optimization

```python
# core/consumers.py - Optimized WebSocket consumer
import orjson
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

class OptimizedAnalysisConsumer(AsyncJsonWebsocketConsumer):
    """Optimized consumer for analysis results."""
    
    async def connect(self):
        # Validate connection quickly
        self.analysis_id = self.scope['url_route']['kwargs']['analysis_id']
        self.user = self.scope['user']
        
        # Check permissions efficiently
        if not self.user.is_authenticated:
            await self.close(code=4003)
            return
            
        has_permission = await self.check_permission()
        if not has_permission:
            await self.close(code=4003)
            return
        
        # Join group for this analysis
        self.group_name = f'analysis_{self.analysis_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send initial state immediately
        state = await self.get_analysis_state()
        await self.send_json(state)
    
    async def disconnect(self, close_code):
        # Cleanup resources
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive_json(self, content):
        """Handle received messages with optimized processing."""
        action = content.get('action')
        
        # Handle different action types
        if action == 'subscribe_updates':
            # Subscribe to specific update types
            update_types = content.get('update_types', [])
            self.update_types = update_types
            await self.send_json({
                'type': 'subscription_confirmed',
                'update_types': update_types
            })
        elif action == 'request_data':
            # Request specific data segments
            data_type = content.get('data_type')
            params = content.get('params', {})
            
            # Get data efficiently based on type
            data = await self.get_analysis_data(data_type, params)
            
            # Send data (potentially chunked if large)
            if data and 'size_hint' in data and data['size_hint'] > 500 * 1024:  # 500KB threshold
                await self.send_chunked_data(data)
            else:
                await self.send_json({
                    'type': 'data',
                    'data_type': data_type,
                    'data': data
                })
    
    async def analysis_update(self, event):
        """Handle updates from the analysis process."""
        # Send update to client, respecting subscriptions
        update_type = event.get('update_type')
        
        # Check if client is subscribed to this update type
        if hasattr(self, 'update_types') and update_type not in self.update_types:
            return
        
        # Send update
        await self.send_json(event)
    
    async def send_chunked_data(self, data):
        """Send large data in chunks to avoid WebSocket size limits."""
        # Serialize data
        serialized = orjson.dumps(data)
        chunk_size = 500 * 1024  # 500KB chunks
        
        # Prepare chunk metadata
        total_chunks = (len(serialized) + chunk_size - 1) // chunk_size
        
        # Send chunks
        for i in range(total_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(serialized))
            
            chunk_data = serialized[start:end]
            
            # Send chunk
            await self.send_json({
                'type': 'data_chunk',
                'chunk_index': i,
                'total_chunks': total_chunks,
                'data': chunk_data.decode('utf-8')
            })
    
    @database_sync_to_async
    def check_permission(self):
        """Efficiently check if user has permission to access this analysis."""
        from django.db.models import Q
        from core.models import Analysis
        
        # Fast permission check
        return Analysis.objects.filter(
            Q(id=self.analysis_id) & 
            (Q(user=self.user) | Q(shared_with=self.user))
        ).exists()
    
    @database_sync_to_async
    def get_analysis_state(self):
        """Get current analysis state efficiently."""
        from core.models import Analysis
        from django.db.models import Prefetch
        
        # Efficient database query with select_related
        analysis = Analysis.objects.select_related('dataset').get(id=self.analysis_id)
        
        # Return minimal state data
        return {
            'type': 'state',
            'analysis_id': self.analysis_id,
            'status': analysis.status,
            'progress': analysis.progress,
            'dataset_name': analysis.dataset.name,
            'created_at': analysis.created_at.isoformat(),
            'updated_at': analysis.updated_at.isoformat()
        }
    
    @database_sync_to_async
    def get_analysis_data(self, data_type, params):
        """Get analysis data based on type and parameters."""
        from core.models import Analysis
        from core.services.data_service import OptimizedDataService
        
        # Get services
        data_service = OptimizedDataService()
        
        # Get analysis
        analysis = Analysis.objects.get(id=self.analysis_id)
        
        # Return different data based on requested type
        if data_type == 'full_results':
            return analysis.get_results()
        elif data_type == 'visualization_data':
            # Get visualization type
            viz_type = params.get('visualization_type')
            return analysis.get_visualization_data(viz_type)
        elif data_type == 'sample_data':
            # Get sample data
            sample_size = params.get('sample_size', 100)
            return data_service.get_dataset_sample(analysis.dataset, sample_size)
        
        # Default empty response
        return None
```

## Resource Monitoring and Auto-scaling

### Prometheus and Grafana Configuration

1. **Add Prometheus integration to Django**:

```python
# Install django-prometheus
# pip install django-prometheus

# settings.py
INSTALLED_APPS = [
    # ... other apps ...
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Add Prometheus URL patterns
# urls.py
urlpatterns = [
    # ... other URL patterns ...
    path('', include('django_prometheus.urls')),
]
```

2. **Configure Prometheus service in docker-compose.prod.yml**:

```yaml
services:
  # ... other services ...
  
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: stickforstats-prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana:10.1.0
    container_name: stickforstats-grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false

volumes:
  # ... other volumes ...
  prometheus_data:
  grafana_data:
```

3. **Create prometheus.yml configuration**:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'django'
    scrape_interval: 5s
    metrics_path: /metrics
    static_configs:
      - targets: ['web:8000']
  
  - job_name: 'asgi'
    scrape_interval: 5s
    metrics_path: /metrics
    static_configs:
      - targets: ['asgi:8001']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

### Container Monitoring

Add container monitoring services to docker-compose.prod.yml:

```yaml
services:
  # ... other services ...
  
  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: stickforstats-node-exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    expose:
      - 9100
  
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.1
    container_name: stickforstats-cadvisor
    restart: unless-stopped
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    expose:
      - 8080
```

## Security and Performance

### Secure Headers for Performance

```python
# middleware/security.py
class SecureHeadersMiddleware:
    """Add security headers that also improve performance."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Performance related headers
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # For HTML responses, add CSP
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' cdn.example.com; "
                "style-src 'self' 'unsafe-inline' cdn.example.com; "
                "img-src 'self' data: cdn.example.com; "
                "font-src 'self' cdn.example.com; "
                "connect-src 'self' ws: wss:; "
                "object-src 'none'; "
                "base-uri 'self';"
            )
        
        return response
```

### Rate Limiting for API

```python
# throttling.py
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class StandardAnonThrottle(AnonRateThrottle):
    rate = '60/minute'

class StandardUserThrottle(UserRateThrottle):
    rate = '1000/minute'

class BurstAnonThrottle(AnonRateThrottle):
    rate = '10/second'

class BurstUserThrottle(UserRateThrottle):
    rate = '30/second'

class UploadThrottle(UserRateThrottle):
    rate = '10/minute'
    scope = 'uploads'

# Apply in views
from .throttling import StandardAnonThrottle, StandardUserThrottle, UploadThrottle

class DatasetViewSet(viewsets.ModelViewSet):
    # ... other configuration ...
    throttle_classes = [StandardAnonThrottle, StandardUserThrottle]
    
    def create(self, request, *args, **kwargs):
        # Override throttle classes for uploads
        self.throttle_classes = [UploadThrottle]
        return super().create(request, *args, **kwargs)
```

## Continuous Performance Improvement

### Performance Test Suite

Create a load testing script using Locust:

```python
# locustfile.py
from locust import HttpUser, task, between
import random
import json

class StickForStatsUser(HttpUser):
    wait_time = between(1, 5)
    token = None
    
    def on_start(self):
        # Login to get token
        response = self.client.post("/api/v1/core/auth/login/", {
            "email": "test@example.com",
            "password": "testpassword123"
        })
        self.token = response.json()["token"]
        self.client.headers.update({'Authorization': f'Bearer {self.token}'})
    
    @task(10)
    def view_dashboard(self):
        self.client.get("/api/v1/core/dashboard/")
    
    @task(5)
    def list_datasets(self):
        self.client.get("/api/v1/core/datasets/")
    
    @task(3)
    def view_dataset(self):
        response = self.client.get("/api/v1/core/datasets/")
        datasets = response.json()
        if datasets:
            dataset_id = random.choice(datasets)["id"]
            self.client.get(f"/api/v1/core/datasets/{dataset_id}/")
    
    @task(2)
    def create_analysis(self):
        response = self.client.get("/api/v1/core/datasets/")
        datasets = response.json()
        if datasets:
            dataset_id = random.choice(datasets)["id"]
            self.client.post("/api/v1/sqc-analysis/controlcharts/", {
                "dataset": dataset_id,
                "variable": "measurement",
                "chart_type": "xbar_r",
                "subgroup_size": 5,
                "name": "Test Analysis"
            })
    
    @task(1)
    def upload_dataset(self):
        # Upload a small dataset
        files = {'file': ('test_data.csv', open('test_data.csv', 'rb'), 'text/csv')}
        self.client.post(
            "/api/v1/core/datasets/",
            data={
                'name': f'Test Dataset {random.randint(1, 1000)}',
                'description': 'Dataset for load testing'
            },
            files=files
        )
```

### Regular Performance Monitoring

Create a script to check performance metrics regularly:

```python
# performance_check.py
import requests
import json
import time
import statistics
import datetime
import sys

def measure_endpoint_performance(base_url, endpoint, token=None, iterations=10):
    """Measure performance of an API endpoint."""
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    url = f"{base_url}{endpoint}"
    response_times = []
    
    for i in range(iterations):
        start_time = time.time()
        response = requests.get(url, headers=headers)
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = (end_time - start_time) * 1000  # Convert to ms
            response_times.append(response_time)
        else:
            print(f"Error: {response.status_code} on {url}")
        
        time.sleep(1)  # Brief pause between requests
    
    if not response_times:
        return None
    
    return {
        "min": min(response_times),
        "max": max(response_times),
        "avg": statistics.mean(response_times),
        "median": statistics.median(response_times),
        "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
        "p95": sorted(response_times)[int(len(response_times) * 0.95)],
        "count": len(response_times)
    }

def login(base_url, email, password):
    """Login to get auth token."""
    response = requests.post(
        f"{base_url}/api/v1/core/auth/login/",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["token"]
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python performance_check.py [environment]")
        sys.exit(1)
    
    environment = sys.argv[1]
    
    # Config for different environments
    configs = {
        "local": {"base_url": "http://localhost:8000", "email": "admin@example.com", "password": "admin123"},
        "staging": {"base_url": "https://staging.example.com", "email": "admin@example.com", "password": "stagingpass"},
        "production": {"base_url": "https://example.com", "email": "admin@example.com", "password": "prodpass"}
    }
    
    if environment not in configs:
        print(f"Unknown environment: {environment}")
        sys.exit(1)
    
    config = configs[environment]
    base_url = config["base_url"]
    
    # Login
    token = login(base_url, config["email"], config["password"])
    if not token:
        print("Login failed")
        sys.exit(1)
    
    # Endpoints to test
    endpoints = [
        "/api/v1/core/dashboard/",
        "/api/v1/core/datasets/",
        "/api/v1/sqc-analysis/controlcharts/",
        "/api/v1/probability-distributions/distributions/",
        "/api/v1/confidence-intervals/calculations/"
    ]
    
    # Run tests
    results = {}
    for endpoint in endpoints:
        print(f"Testing {endpoint}...")
        results[endpoint] = measure_endpoint_performance(base_url, endpoint, token)
    
    # Print results
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nPerformance Report - {environment.upper()} - {timestamp}\n")
    print(f"{'Endpoint':<50} {'Avg (ms)':<10} {'Median (ms)':<10} {'P95 (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10}")
    print("-" * 100)
    
    for endpoint, metrics in results.items():
        if metrics:
            print(f"{endpoint:<50} {metrics['avg']:<10.2f} {metrics['median']:<10.2f} {metrics['p95']:<10.2f} {metrics['min']:<10.2f} {metrics['max']:<10.2f}")
    
    # Save results to file
    with open(f"performance_{environment}_{timestamp.replace(':', '-').replace(' ', '_')}.json", "w") as f:
        json.dump({"timestamp": timestamp, "environment": environment, "results": results}, f, indent=2)

if __name__ == "__main__":
    main()
```

## Conclusion

This enhanced performance optimization guide provides the necessary strategies and configurations to fully optimize the StickForStats platform for production deployment. By implementing these optimizations, you'll be able to handle greater user load, process larger datasets, and provide a more responsive user experience.

The key takeaways from this guide are:

1. **Multi-layered caching** is essential for performance - from database query caching to HTTP response caching to CDN integration.

2. **Database optimization** is critical, especially for the vector database components needed for the RAG system.

3. **Resource allocation and monitoring** ensures stable performance and helps identify bottlenecks before they impact users.

4. **WebSocket optimization** is vital for real-time functionality and large dataset transfers.

5. **Frontend/UI optimizations** ensure a responsive user experience regardless of the complexity of the statistical analyses.

Remember to implement these optimizations incrementally and test thoroughly at each stage. Regular performance testing and monitoring will help identify new optimization opportunities as the system evolves.