# Multi-stage build for StickForStats Django backend
# Stage 1: Build dependencies
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    gfortran \
    python3-dev \
    pkg-config \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    libatlas-base-dev \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Upgrade pip and install wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.10-slim AS production

# Add labels
LABEL maintainer="StickForStats Team"
LABEL description="StickForStats Django Backend - Production Ready"
LABEL version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=stickforstats.settings
ENV PATH=/home/appuser/.local/bin:$PATH

# Set work directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libopenblas0 \
    libgomp1 \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy project
COPY . /app/

# Create necessary directories with proper ownership
RUN mkdir -p /app/media /app/staticfiles /app/logs && \
    chown -R appuser:appgroup /app

# Note: Static files will be collected in entrypoint.sh with proper environment

# Make entrypoint executable and set proper permissions
RUN chmod +x /app/docker/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Default command
CMD ["gunicorn", "stickforstats.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]