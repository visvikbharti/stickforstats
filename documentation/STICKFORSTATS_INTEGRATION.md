# StickForStats: Module Integration Guide

## Introduction

This document provides detailed instructions for integrating all migrated statistical modules with the core StickForStats platform. These modules were migrated from standalone Streamlit applications to React/Django components that work together as part of a unified statistical analysis platform.

## Prerequisites

Before starting the integration process, ensure you have:

1. Access to the core StickForStats repository
2. All migrated modules (SQC, DOE, PCA, Probability Distributions, Confidence Intervals)
3. Python 3.9+ and Node.js 16+
4. Docker and Docker Compose (optional but recommended)

## Integration Steps

### 1. Setup Development Environment

```bash
# Clone the StickForStats repository
git clone https://github.com/yourusername/stickforstats.git
cd stickforstats

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Backend Integration

#### 2.1 Copy Module Packages

Copy each module's Django app directory to the StickForStats project:

```bash
cp -r new_project/stickforstats/sqc_analysis/ stickforstats/
cp -r new_project/stickforstats/doe_analysis/ stickforstats/
cp -r new_project/stickforstats/pca_analysis/ stickforstats/
cp -r new_project/stickforstats/probability_distributions/ stickforstats/
cp -r new_project/stickforstats/confidence_intervals/ stickforstats/
```

#### 2.2 Register Apps in Settings

Add the modules to the `INSTALLED_APPS` list in `stickforstats/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'stickforstats.sqc_analysis',
    'stickforstats.doe_analysis',
    'stickforstats.pca_analysis',
    'stickforstats.probability_distributions',
    'stickforstats.confidence_intervals',
]
```

#### 2.3 Update URL Configuration

Include the module URLs in the main `urls.py`:

```python
# stickforstats/urls.py
from django.urls import path, include

urlpatterns = [
    # ... existing URLs
    path('api/sqc/', include('stickforstats.sqc_analysis.api.urls')),
    path('api/doe/', include('stickforstats.doe_analysis.api.urls')),
    path('api/pca/', include('stickforstats.pca_analysis.api.urls')),
    path('api/distributions/', include('stickforstats.probability_distributions.api.urls')),
    path('api/confidence-intervals/', include('stickforstats.confidence_intervals.api.urls')),
]
```

#### 2.4 Update WebSocket Routing

Add the WebSocket consumers to the `routing.py` file:

```python
# stickforstats/routing.py
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from stickforstats.sqc_analysis.routing import websocket_urlpatterns as sqc_websocket_urlpatterns
from stickforstats.doe_analysis.routing import websocket_urlpatterns as doe_websocket_urlpatterns
from stickforstats.pca_analysis.routing import websocket_urlpatterns as pca_websocket_urlpatterns
from stickforstats.probability_distributions.routing import websocket_urlpatterns as prob_websocket_urlpatterns
from stickforstats.confidence_intervals.routing import websocket_urlpatterns as ci_websocket_urlpatterns

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            sqc_websocket_urlpatterns +
            doe_websocket_urlpatterns +
            pca_websocket_urlpatterns +
            prob_websocket_urlpatterns +
            ci_websocket_urlpatterns
        )
    ),
})
```

#### 2.5 Run Database Migrations

Apply the database migrations for all modules:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Frontend Integration

#### 3.1 Copy React Components

Copy the React components for each module:

```bash
# Create directory structure if it doesn't exist
mkdir -p frontend/src/components/sqc
mkdir -p frontend/src/components/doe
mkdir -p frontend/src/components/pca
mkdir -p frontend/src/components/probability_distributions
mkdir -p frontend/src/components/confidence_intervals

# Copy component files
cp -r new_project/frontend/src/components/sqc/* frontend/src/components/sqc/
cp -r new_project/frontend/src/components/doe/* frontend/src/components/doe/
cp -r new_project/frontend/src/components/pca/* frontend/src/components/pca/
cp -r new_project/frontend/src/components/probability_distributions/* frontend/src/components/probability_distributions/
cp -r new_project/frontend/src/components/confidence_intervals/* frontend/src/components/confidence_intervals/
```

#### 3.2 Update API Service Files

Copy the API services for each module:

```bash
# Copy API services
cp new_project/frontend/src/api/sqcApi.js frontend/src/api/
cp new_project/frontend/src/api/doeApi.js frontend/src/api/
cp new_project/frontend/src/api/pcaApi.js frontend/src/api/
cp new_project/frontend/src/api/probabilityDistributionsApi.js frontend/src/api/
cp new_project/frontend/src/api/confidenceIntervalsApi.js frontend/src/api/
```

#### 3.3 Update Main App Routing

Add routes for each module in the main App component:

```jsx
// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';

// Import module pages
import Dashboard from './components/dashboard/Dashboard';
import SQCAnalysisPage from './components/sqc/SQCAnalysisPage';
import DoePage from './components/doe/DoePage';
import PcaPage from './components/pca/PcaPage';
import ProbabilityDistributionsPage from './components/probability_distributions/ProbabilityDistributionsPage';
import ConfidenceIntervalsPage from './components/confidence_intervals/ConfidenceIntervalsPage';

function App() {
  return (
    <Router>
      <Navigation />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/sqc/*" element={<SQCAnalysisPage />} />
        <Route path="/doe/*" element={<DoePage />} />
        <Route path="/pca/*" element={<PcaPage />} />
        <Route path="/probability-distributions/*" element={<ProbabilityDistributionsPage />} />
        <Route path="/confidence-intervals/*" element={<ConfidenceIntervalsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
```

#### 3.4 Update Navigation Component

Add navigation links for each module:

```jsx
// frontend/src/components/Navigation.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';

const Navigation = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'white' }}>
          StickForStats
        </Typography>
        <Box>
          <Button color="inherit" component={Link} to="/sqc">SQC Analysis</Button>
          <Button color="inherit" component={Link} to="/doe">DOE Analysis</Button>
          <Button color="inherit" component={Link} to="/pca">PCA Analysis</Button>
          <Button color="inherit" component={Link} to="/probability-distributions">Probability Distributions</Button>
          <Button color="inherit" component={Link} to="/confidence-intervals">Confidence Intervals</Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;
```

### 4. Update Package Dependencies

Ensure all required dependencies are included in package.json and requirements.txt:

#### 4.1 Backend Dependencies

Add these to requirements.txt:

```
# Statistical packages
scipy>=1.10.0
numpy>=1.23.0
pandas>=1.5.0
scikit-learn>=1.2.0
statsmodels>=0.13.0
matplotlib>=3.6.0
seaborn>=0.12.0

# Django and DRF
django>=4.2.0
djangorestframework>=3.14.0
channels>=4.0.0
django-cors-headers>=3.13.0

# Asynchronous task processing
celery>=5.2.0
redis>=4.5.0

# WebSockets
channels_redis>=4.0.0
daphne>=4.0.0

# Additional utilities
python-dotenv>=1.0.0
whitenoise>=6.4.0
gunicorn>=20.1.0
```

#### 4.2 Frontend Dependencies

Add these to package.json:

```json
{
  "dependencies": {
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.11.16",
    "@mui/material": "^5.13.0",
    "axios": "^1.4.0",
    "chart.js": "^4.3.0",
    "d3": "^7.8.4",
    "mathjs": "^11.8.0",
    "notistack": "^3.0.1",
    "plotly.js": "^2.23.0",
    "react": "^18.2.0",
    "react-chartjs-2": "^5.2.0",
    "react-dom": "^18.2.0",
    "react-plotly.js": "^2.6.0",
    "react-router-dom": "^6.11.1",
    "react-syntax-highlighter": "^15.5.0",
    "react-table": "^7.8.0",
    "react-three-fiber": "^6.0.13",
    "recharts": "^2.6.0",
    "three": "^0.152.2"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.4.3",
    "jest": "^29.5.0",
    "jest-environment-jsdom": "^29.5.0",
    "vite": "^4.3.5",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
```

### 5. Static Files and Media

#### 5.1 Create Required Directories

Ensure the static files directories exist:

```bash
mkdir -p stickforstats/static/images/sqc
mkdir -p stickforstats/static/images/doe
mkdir -p stickforstats/static/images/pca
mkdir -p stickforstats/static/images/probability_distributions
mkdir -p stickforstats/static/images/confidence_intervals
```

#### 5.2 Copy Static Assets

Copy the static assets for each module:

```bash
cp -r new_project/frontend/public/static/images/sqc/* stickforstats/static/images/sqc/
cp -r new_project/frontend/public/static/images/doe/* stickforstats/static/images/doe/
cp -r new_project/frontend/public/static/images/pca/* stickforstats/static/images/pca/
cp -r new_project/frontend/public/static/images/probability_distributions/* stickforstats/static/images/probability_distributions/
cp -r new_project/frontend/public/static/images/confidence_intervals/* stickforstats/static/images/confidence_intervals/
```

### 6. Configuration

#### 6.1 Environment Variables

Create a `.env` file with the necessary configuration:

```
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DATABASE_URL=postgres://user:password@localhost:5432/stickforstats

# Redis settings
REDIS_URL=redis://localhost:6379/0

# Celery settings
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

#### 6.2 Update Settings

Update the settings to use the environment variables:

```python
# stickforstats/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'stickforstats'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Redis settings
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Celery settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
```

### 7. Testing the Integration

#### 7.1 Start the Development Server

```bash
# Start the Django development server
python manage.py runserver

# In a separate terminal, start the frontend development server
cd frontend
npm run dev
```

#### 7.2 Test Each Module

Verify that each module works correctly:

1. Navigate to each module's URL
2. Test basic functionality
3. Check that WebSocket connections work for real-time updates
4. Verify that data can be shared between modules

#### 7.3 Run Tests

Run the automated tests for each module:

```bash
# Backend tests
python manage.py test stickforstats.sqc_analysis
python manage.py test stickforstats.doe_analysis
python manage.py test stickforstats.pca_analysis
python manage.py test stickforstats.probability_distributions
python manage.py test stickforstats.confidence_intervals

# Frontend tests
cd frontend
npm test
```

### 8. Production Deployment

#### 8.1 Build Frontend Assets

```bash
cd frontend
npm run build
```

#### 8.2 Collect Static Files

```bash
python manage.py collectstatic
```

#### 8.3 Deploy with Docker

Use the Docker Compose configuration:

```bash
docker-compose up -d
```

## Module-Specific Integration Notes

### SQC Analysis

- Integrates with the core data management system
- Uses shared statistical utilities
- Provides control chart data that can be used in other modules

### DOE Analysis

- Integrates with the experiment tracking system
- Uses factor definitions that can be shared with other modules
- Can use response data from other analyses

### PCA Analysis

- Specialized for gene expression data
- Can integrate with other bioinformatics tools
- Uses shared data visualization components

### Probability Distributions

- Core module that provides distribution functions for other modules
- Integrates with data fitting tools
- Used by confidence intervals and hypothesis testing modules

### Confidence Intervals

- Builds on the probability distributions module
- Integrates with data analysis workflows
- Used in results interpretation across modules

## Troubleshooting

### Common Issues and Solutions

1. **Database Migration Conflicts**
   - Problem: Migration conflicts between modules
   - Solution: Reset migrations if needed and run `makemigrations` with specific apps

2. **WebSocket Connection Issues**
   - Problem: WebSocket connections failing
   - Solution: Check ASGI configuration and ensure Redis is running for Channels

3. **Static Files Not Found**
   - Problem: 404 errors for static files
   - Solution: Verify paths and run `collectstatic` again

4. **API Endpoint Conflicts**
   - Problem: Conflicting API endpoints
   - Solution: Use module-specific URL prefixes consistently

## Conclusion

This integration guide provides the steps needed to integrate all the migrated statistical modules into the core StickForStats platform. Following this guide should result in a fully functional, integrated statistical analysis platform that preserves all the features of the original Streamlit applications while providing a more modern, responsive, and scalable user experience.