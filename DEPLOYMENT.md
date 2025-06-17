# Deployment Guide

This document outlines the steps to deploy the StickForStats Django application in various environments.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- Redis 6+
- Node.js 16+ and npm
- Docker and Docker Compose (for containerized deployment)

## Local Development Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgres://postgres:postgres@localhost:5432/stickforstats
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   EMAIL_URL=console://
   ```

4. Create the required directories:
   ```bash
   mkdir -p media staticfiles logs
   ```

5. Create the database and apply migrations:
   ```bash
   createdb stickforstats  # Using PostgreSQL CLI
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. In a separate terminal, start Celery worker:
   ```bash
   celery -A stickforstats worker -l INFO
   ```

9. In a separate terminal, start Celery beat:
   ```bash
   celery -A stickforstats beat -l INFO
   ```

10. Start the frontend development server:
    ```bash
    cd frontend
    npm install
    npm start
    ```

## Docker Development Setup

1. Create a `.env` file as described above.

2. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

3. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. Access the application at http://localhost:80

## Production Deployment

### Docker Swarm Deployment

1. Initialize Docker Swarm (if not already initialized):
   ```bash
   docker swarm init
   ```

2. Create a production `.env` file with secure settings.

3. Deploy the stack:
   ```bash
   docker stack deploy -c docker-compose.yml stickforstats
   ```

### Kubernetes Deployment

Kubernetes deployment files are available in the `kubernetes/` directory. To deploy:

1. Apply the configuration:
   ```bash
   kubectl apply -f kubernetes/namespace.yaml
   kubectl apply -f kubernetes/secrets.yaml
   kubectl apply -f kubernetes/configmap.yaml
   kubectl apply -f kubernetes/postgres.yaml
   kubectl apply -f kubernetes/redis.yaml
   kubectl apply -f kubernetes/web.yaml
   kubectl apply -f kubernetes/asgi.yaml
   kubectl apply -f kubernetes/celery.yaml
   kubectl apply -f kubernetes/nginx.yaml
   ```

2. Check the status of the deployment:
   ```bash
   kubectl get pods -n stickforstats
   ```

### AWS Deployment

For AWS deployment, we recommend using:

1. **ECS with Fargate** for containerized deployment
2. **RDS PostgreSQL** for the database
3. **ElastiCache Redis** for caching and message broker
4. **S3** for static and media file storage
5. **CloudFront** for CDN
6. **Route 53** for DNS

Detailed AWS deployment instructions are available in the `docs/aws-deployment.md` file.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DEBUG | Debug mode | True/False |
| SECRET_KEY | Django secret key | your-secret-key |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts | localhost,example.com |
| DATABASE_URL | Database connection URL | postgres://user:pass@host:port/dbname |
| REDIS_URL | Redis connection URL | redis://host:port/db |
| CELERY_BROKER_URL | Celery broker URL | redis://host:port/db |
| CELERY_RESULT_BACKEND | Celery result backend URL | redis://host:port/db |
| EMAIL_URL | Email configuration URL | smtp://user:pass@host:port |
| DJANGO_SUPERUSER_EMAIL | Initial superuser email | admin@example.com |
| DJANGO_SUPERUSER_PASSWORD | Initial superuser password | securepassword |
| RAG_MODEL_NAME | RAG embedding model name | sentence-transformers/all-MiniLM-L6-v2 |

## SSL Configuration

For production deployments, SSL is required. You can configure SSL in the Nginx configuration:

1. Obtain SSL certificates from Let's Encrypt or another provider.
2. Update the Nginx configuration in `docker/nginx.conf` to include SSL settings.

## Monitoring

The application is configured for monitoring with:

1. **Prometheus** for metrics collection
2. **Grafana** for visualization
3. **Sentry** for error tracking

Configuration files are available in the `monitoring/` directory.

## Backup Strategy

1. **Database**: Use pg_dump for regular backups
2. **Media files**: Use rsync or S3 sync for backups
3. **Application data**: Store in version control or a backup service

Example backup script:

```bash
#!/bin/bash

# Backup database
pg_dump -U postgres stickforstats > backup/db_$(date +%Y%m%d_%H%M%S).sql

# Backup media files
rsync -av media/ backup/media/

# Compress backups
tar -czf backup/backup_$(date +%Y%m%d_%H%M%S).tar.gz backup/db_* backup/media/
```

## Common Issues

### Database Connection Errors

If you see database connection errors, check:
- Database service is running
- Database credentials are correct
- PostgreSQL is configured to accept connections

### Media File Access Issues

If media files are not accessible, check:
- File permissions
- Storage configuration
- Nginx configuration for media serving

### WebSocket Connection Failures

If WebSocket connections fail, check:
- ASGI service is running
- Nginx WebSocket proxy configuration
- Client-side WebSocket URL

## Further Reading

For more information on deploying Django applications, refer to:
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Django with Docker](https://docs.docker.com/samples/django/)
- [Django with Kubernetes](https://kubernetes.io/docs/tutorials/)