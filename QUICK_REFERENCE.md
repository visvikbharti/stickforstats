# StickForStats Quick Reference Guide

This document provides a quick reference for common operations in the StickForStats Django/React application.

## Development Setup

### Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Run Celery Worker
```bash
# In a separate terminal
celery -A stickforstats worker -l INFO
```

### Run Celery Beat
```bash
# In a separate terminal
celery -A stickforstats beat -l INFO
```

## Testing

### Run Backend Tests
```bash
# Run all tests
./run_tests.sh

# Run specific app tests
python manage.py test stickforstats.core

# Run with coverage
coverage run --source='stickforstats' manage.py test
coverage report
coverage html
```

### Run Frontend Tests
```bash
# Navigate to frontend directory
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

### Run Integration Tests
```bash
# Start the server
python manage.py runserver

# In another terminal
python test_integration.py --base-url http://localhost:8000
```

## Common Development Tasks

### Create New Django App
```bash
python manage.py startapp newapp
```

### Create New Migration
```bash
python manage.py makemigrations
```

### Generate Schema Graph
```bash
python manage.py graph_models -a -o schema.png
```

### Create New React Component
```bash
# Navigate to frontend directory
cd frontend

# Create component directory
mkdir -p src/components/new_component

# Create component files
touch src/components/new_component/NewComponent.jsx
touch src/components/new_component/NewComponent.test.jsx
touch src/components/new_component/styles.js
```

## API Reference

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Dataset Endpoints
- `GET /api/datasets/` - List datasets
- `POST /api/datasets/` - Create dataset
- `GET /api/datasets/{id}/` - Get dataset details
- `PUT /api/datasets/{id}/` - Update dataset
- `DELETE /api/datasets/{id}/` - Delete dataset
- `POST /api/datasets/upload/` - Upload dataset file

### Analysis Endpoints
- `GET /api/analyses/` - List analyses
- `POST /api/analyses/` - Create analysis
- `GET /api/analyses/{id}/` - Get analysis details
- `PUT /api/analyses/{id}/` - Update analysis
- `DELETE /api/analyses/{id}/` - Delete analysis
- `GET /api/analyses/{id}/results/` - Get analysis results
- `GET /api/analyses/{id}/visualizations/` - Get analysis visualizations

### Statistical Analysis Endpoints
- `POST /api/statistics/descriptive/` - Descriptive statistics
- `POST /api/statistics/correlation/` - Correlation analysis
- `POST /api/statistics/regression/` - Regression analysis
- `POST /api/statistics/anova/` - ANOVA analysis
- `POST /api/statistics/machine-learning/` - Machine learning analysis
- `POST /api/statistics/time-series/` - Time series analysis
- `POST /api/statistics/bayesian/` - Bayesian analysis

### Workflow Endpoints
- `GET /api/workflows/` - List workflows
- `POST /api/workflows/` - Create workflow
- `GET /api/workflows/{id}/` - Get workflow details
- `PUT /api/workflows/{id}/` - Update workflow
- `DELETE /api/workflows/{id}/` - Delete workflow
- `POST /api/workflows/{id}/execute/` - Execute workflow
- `GET /api/workflows/{id}/steps/` - Get workflow steps
- `POST /api/workflows/{id}/steps/` - Add workflow step

### Module-Specific Endpoints

#### SQC Analysis
- `GET /api/sqc-analysis/control-charts/` - List control charts
- `POST /api/sqc-analysis/control-charts/` - Create control chart
- `GET /api/sqc-analysis/process-capability/` - Get process capability analysis
- `POST /api/sqc-analysis/acceptance-sampling/` - Create acceptance sampling plan

#### DOE Analysis
- `GET /api/doe-analysis/designs/` - List experimental designs
- `POST /api/doe-analysis/designs/` - Create experimental design
- `GET /api/doe-analysis/analyses/` - List design analyses
- `POST /api/doe-analysis/analyses/` - Create design analysis

#### PCA Analysis
- `GET /api/pca-analysis/configurations/` - List PCA configurations
- `POST /api/pca-analysis/configurations/` - Create PCA configuration
- `GET /api/pca-analysis/results/` - List PCA results
- `POST /api/pca-analysis/analyses/` - Perform PCA analysis

#### Probability Distributions
- `GET /api/probability-distributions/distributions/` - List probability distributions
- `POST /api/probability-distributions/calculate/{distribution}/` - Calculate distribution properties

#### Confidence Intervals
- `GET /api/confidence-intervals/` - List confidence interval analyses
- `POST /api/confidence-intervals/calculate/` - Calculate confidence interval

## Database Schema

### Core Tables
- `auth_user` - User accounts
- `core_dataset` - Dataset information
- `core_analysissession` - Analysis session tracking
- `core_analysisresult` - Analysis results
- `core_visualization` - Visualization data
- `core_workflow` - Workflow definition
- `core_workflowstep` - Workflow steps

### Module-Specific Tables
- `sqc_analysis_*` - SQC Analysis tables
- `doe_analysis_*` - DOE Analysis tables
- `pca_analysis_*` - PCA Analysis tables
- `probability_distributions_*` - Probability Distributions tables
- `confidence_intervals_*` - Confidence Intervals tables

## Common Debugging Tips

### Django Server
- Check logs in `logs/stickforstats.log`
- Use Django Debug Toolbar for query analysis
- Run `python manage.py check` for configuration issues

### React Application
- Check browser console for errors
- Use React DevTools for component debugging
- Check network tab for API request issues

### Database Issues
- Run `python manage.py dbshell` to access database directly
- Check for missing migrations with `python manage.py showmigrations`
- Analyze query performance with EXPLAIN

## Deployment Commands

### Docker Deployment
```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop containers
docker-compose down
```

### Production Deployment Checklist
- Set `DEBUG=False` in settings
- Configure proper database settings
- Set up static file serving
- Configure HTTPS
- Set appropriate ALLOWED_HOSTS
- Configure email settings
- Set up proper logging
- Configure Celery for production

## Common URLs
- Admin interface: `/admin/`
- API documentation: `/api/docs/`
- Frontend application: `/`
- User dashboard: `/dashboard/`

## Helpful Resources
- Django documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- React documentation: https://reactjs.org/docs/getting-started.html
- Material-UI components: https://mui.com/components/
- Plotly documentation: https://plotly.com/javascript/
- Celery documentation: https://docs.celeryproject.org/