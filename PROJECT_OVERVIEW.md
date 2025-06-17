# StickForStats Django Migration Project

This repository contains the migration of the StickForStats statistical analysis platform from a collection of Streamlit modules to a unified Django web application.

## Project Structure

- `stickforstats/`: Core Django project
  - `core/`: Core application with base models and services
  - `sqc_analysis/`: Statistical Quality Control module
  - `rag_system/`: RAG-based guidance system
  - `reports/`: Report generation module
  - `education/`: Educational content module
  - `settings.py`: Project settings
  - `urls.py`: URL configuration
  - `asgi.py`: ASGI configuration for WebSockets
  - `wsgi.py`: WSGI configuration
  - `celery.py`: Celery configuration

- `frontend/`: React frontend application
  - `src/`: Source code
    - `components/`: React components
    - `hooks/`: Custom hooks
    - `pages/`: Page components
    - `api/`: API clients
    - `context/`: React context providers

- `docker/`: Docker deployment configuration
  - `Dockerfile`: Main application Dockerfile
  - `nginx.conf`: Nginx configuration
  - `entrypoint.sh`: Docker entrypoint script

## Key Files

- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Docker Compose configuration
- `setup_dev.sh`: Development environment setup script
- `manage.py`: Django management script
- `DEPLOYMENT.md`: Deployment instructions
- `MIGRATION_APPROACH.md`: Migration approach documentation
- `IMPLEMENTATION_STATUS.md`: Implementation status tracking

## Statistical Modules

The platform includes several statistical modules:

1. **Statistical Quality Control (SQC)**
   - Control charts (X̄-R, X̄-S, I-MR, p, np, c, u)
   - Process capability analysis
   - Acceptance sampling plans
   - Measurement systems analysis

2. **Design of Experiments (DOE)** - Planned
   - Factorial designs
   - Response surface methodology
   - Mixture designs
   - Screening designs

3. **Principal Component Analysis (PCA)** - Planned
   - Data reduction
   - Visualization
   - Factor extraction
   - Variable correlation

4. **Probability Distributions** - Planned
   - Visualization and exploration
   - Parameter estimation
   - Distribution fitting
   - Random sampling

5. **Confidence Intervals** - Planned
   - Interval estimation
   - Sample size determination
   - Precision analysis
   - Hypothesis testing integration

## Architecture Highlights

1. **Modern Django Backend**
   - Django 4.2+ with REST Framework
   - PostgreSQL with pgvector for vector search
   - Celery for asynchronous processing
   - Channels for WebSocket support

2. **React Frontend**
   - Material-UI component library
   - Interactive visualizations
   - Responsive design
   - React Router for navigation

3. **RAG-based Guidance System**
   - Contextual recommendations
   - Educational content integration
   - Next-step suggestions
   - Statistical interpretation assistance

4. **Enhanced Data Validation**
   - Comprehensive validation rules
   - Statistical validity checks
   - Data quality assessment
   - Format detection and conversion

5. **Report Generation**
   - PDF, HTML, and DOCX formats
   - Publication-quality graphics
   - Statistical interpretation
   - Custom templating

## Getting Started

See [README.md](./README.md) for setup instructions and [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions.

## Implementation Status

See [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) for the current implementation status.

## Migration Approach

See [MIGRATION_APPROACH.md](./MIGRATION_APPROACH.md) for details on the migration approach.