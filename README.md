# StickForStats Django Migration

A comprehensive Django-based statistical analysis platform migrated from the original Streamlit-based StickForStats platform.

## Project Overview

StickForStats is an advanced statistical analysis platform designed for scientists and industry professionals. This Django implementation unifies multiple statistical modules into a cohesive platform with enhanced capabilities:

- Core statistical analysis functionality
- Specialized statistical modules
  - Statistical Quality Control (SQC)
  - Design of Experiments (DOE)
  - Principal Component Analysis (PCA)
  - Probability Distributions
  - Confidence Interval Analysis
- Autonomous guidance system that recommends next analytical steps
- Educational components with interactive visualizations
- RAG-based LLM system for contextual assistance
- Comprehensive report generation

## Architecture

The application follows a modular architecture with:

- Django 4.2+ with Django REST Framework for API endpoints
- PostgreSQL database with pgvector for RAG implementation
- Asynchronous processing with Celery for computationally intensive operations
- WebSocket support for real-time updates
- Modern frontend with interactive visualizations
- Authentication with subscription tier management

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis (for Celery and WebSockets)
- Node.js and npm (for frontend development)

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/stickforstats-django.git
cd stickforstats-django
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up the database
```bash
python manage.py migrate
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

6. Build the frontend assets
```bash
cd frontend
npm install
npm run build
cd ..
```

7. Run the development server
```bash
python manage.py runserver
```

## Module Structure

Each statistical module is implemented as a separate Django app:

- `core`: Core functionality, authentication, and shared components
- `dashboard`: User dashboard and data management
- `sqc_analysis`: Statistical Quality Control module
- `doe_analysis`: Design of Experiments module
- `pca_analysis`: Principal Component Analysis module
- `probability_distributions`: Probability Distributions module
- `confidence_intervals`: Confidence Interval Analysis module
- `rag_system`: RAG-based LLM integration
- `reports`: Report generation and management
- `education`: Educational content and interactive tutorials

## Implementation Status

The migration project has been successfully completed. All modules have been migrated from Streamlit to the Django/React architecture and are fully functional.

See [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) for detailed status information and [MIGRATION_SUMMARY.md](./MIGRATION_SUMMARY.md) for a comprehensive overview of the migration project.

### Module-Specific Testing

Each module has dedicated test scripts to verify its functionality:

- Core: `test_core.py`
- Confidence Intervals: `test_confidence_intervals.py`
- Probability Distributions: `test_probability_distributions.py`
- PCA Analysis: `test_pca_analysis.py`
- SQC Analysis: `test_sqc_analysis.py`
- DOE Analysis: `test_doe_analysis.py`

A comprehensive integration test script is available at `test_integration.py` to validate the functionality of the entire system.

## Testing

Run tests with:

```bash
python manage.py test
```

For coverage reports:

```bash
coverage run --source='.' manage.py test
coverage report
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions and configuration options.

## License

This project is licensed under the MIT License - see the LICENSE file for details.