# DOE Module Critical Fixes

This document outlines the immediate fixes needed for the most critical issues identified in the DOE module testing. These fixes should be implemented first to ensure basic functionality.

## 1. Fix Missing Analysis.jsx Component

The Analysis component is referenced in DoePage.jsx but was not found in our implementation. Create this component:

```jsx
// src/components/doe/Analysis.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';

// Import visualization components
import EffectPlot from './visualizations/EffectPlot';
import InteractionPlot from './visualizations/InteractionPlot';
import ResidualDiagnostics from './visualizations/ResidualDiagnostics';
import { fetchAnalysisData } from '../../services/doeService';

/**
 * Analysis component for DOE module
 * Provides tools for analyzing experimental results
 */
function Analysis({ content }) {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Fetch analysis data when component mounts
  useEffect(() => {
    const loadAnalysisData = async () => {
      try {
        setLoading(true);
        const data = await fetchAnalysisData();
        setAnalysisData(data);
        setLoading(false);
      } catch (err) {
        console.error('Error loading analysis data:', err);
        setError('Failed to load analysis data. Please try again.');
        setLoading(false);
      }
    };
    
    loadAnalysisData();
  }, []);
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Analysis & Interpretation
      </Typography>
      
      <Typography variant="body1" paragraph>
        Analyze your experimental results to identify significant factors, 
        interactions, and optimize your process. This section provides tools 
        for comprehensive analysis of your Design of Experiments data.
      </Typography>
      
      <Paper elevation={0} variant="outlined" sx={{ p: 3, mb: 4 }}>
        {content?.introduction && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Introduction to DOE Analysis
            </Typography>
            <Typography variant="body1">
              {content.introduction}
            </Typography>
          </Box>
        )}
        
        {/* This would be populated with actual data in a production environment */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" gutterBottom>
            Please select an experiment to analyze from the Design Builder tab, 
            or use one of our sample datasets to explore the analysis tools.
          </Typography>
        </Box>
        
        {/* Sample visualization components */}
        <Typography variant="h6" gutterBottom>
          Sample Analysis Tools
        </Typography>
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>
            Effect Plot
          </Typography>
          <Box sx={{ height: 300 }}>
            {analysisData ? (
              <EffectPlot data={analysisData.effects} />
            ) : (
              <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Typography color="text.secondary">
                  Select an experiment to view effect plots
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>
            Interaction Plot
          </Typography>
          <Box sx={{ height: 300 }}>
            {analysisData ? (
              <InteractionPlot data={analysisData.interactions} />
            ) : (
              <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Typography color="text.secondary">
                  Select an experiment to view interaction plots
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>
            Residual Diagnostics
          </Typography>
          <Box sx={{ height: 300 }}>
            {analysisData ? (
              <ResidualDiagnostics data={analysisData.residuals} />
            ) : (
              <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Typography color="text.secondary">
                  Select an experiment to view residual diagnostics
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}

export default Analysis;
```

## 2. Fix Image Paths in DesignTypes.jsx

Update the image paths in DesignTypes.jsx to use existing assets or create placeholders:

```jsx
// Update around line 808-861 in DesignTypes.jsx
const DESIGN_TYPE_CARDS = [
  {
    title: 'Factorial Designs',
    description: 'Full and fractional factorial designs for screening experiments',
    // Update path to use a placeholder or existing image
    image: '/static/images/doe/factorial_design.png',
    tab: 0
  },
  {
    title: 'Response Surface Designs',
    description: 'Optimize process parameters with response surface methodology',
    // Update path to use a placeholder or existing image
    image: '/static/images/doe/response_surface.png',
    tab: 1
  },
  // ... update other card images similarly
];

// Add a fallback for images that fail to load
const handleImageError = (e) => {
  e.target.src = '/static/images/placeholder.png';
};

// Then in the CardMedia component, add the error handler
<CardMedia
  component="img"
  height="140"
  image={card.image}
  alt={card.title}
  onError={handleImageError}
/>
```

## 3. Fix Form Validation in DesignBuilder

Enhance form validation in DesignBuilder.jsx:

```jsx
// Update around line 91-110 in DesignBuilder.jsx
const [formErrors, setFormErrors] = useState({
  experimentName: '',
  factors: [],
  responses: []
});

// Add a validation function
const validateForm = () => {
  const errors = {
    experimentName: '',
    factors: [],
    responses: []
  };
  
  // Validate experiment name
  if (!experimentName.trim()) {
    errors.experimentName = 'Experiment name is required';
  }
  
  // Validate factors
  if (factors.length === 0) {
    setError('At least one factor is required');
    return false;
  }
  
  // Validate each factor
  factors.forEach((factor, index) => {
    const factorErrors = {};
    if (!factor.name.trim()) {
      factorErrors.name = 'Factor name is required';
    }
    if (factor.type === 'numeric') {
      if (isNaN(factor.low) || isNaN(factor.high)) {
        factorErrors.range = 'Low and high values must be numbers';
      } else if (parseFloat(factor.low) >= parseFloat(factor.high)) {
        factorErrors.range = 'High value must be greater than low value';
      }
    }
    errors.factors[index] = factorErrors;
  });
  
  // Validate responses
  if (responses.length === 0) {
    setError('At least one response is required');
    return false;
  }
  
  // Validate each response
  responses.forEach((response, index) => {
    const responseErrors = {};
    if (!response.name.trim()) {
      responseErrors.name = 'Response name is required';
    }
    errors.responses[index] = responseErrors;
  });
  
  setFormErrors(errors);
  
  // Check if there are any errors
  const hasExperimentNameError = !!errors.experimentName;
  const hasFactorErrors = errors.factors.some(factor => Object.keys(factor).length > 0);
  const hasResponseErrors = errors.responses.some(response => Object.keys(response).length > 0);
  
  return !hasExperimentNameError && !hasFactorErrors && !hasResponseErrors;
};

// Update submitDesign function to use validation
const submitDesign = () => {
  if (!validateForm()) {
    return;
  }
  
  // Rest of the submission logic...
};
```

## 4. Fix WebSocket Routing Issues

Update the routing.py file to use string-based IDs:

```python
# Update in routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Update to use string patterns instead of int
    re_path(r'ws/doe/(?P<experiment_id>[^/]+)/$', consumers.DOEConsumer.as_asgi()),
]
```

## 5. Standardize Design Types

Create a consistent mapping between frontend and backend design types:

```python
# Add to a constants.py file
# Design type constants
FACTORIAL_DESIGN = 'FACTORIAL'
FRACTIONAL_FACTORIAL_DESIGN = 'FRACTIONAL_FACTORIAL'
RESPONSE_SURFACE_DESIGN = 'RESPONSE_SURFACE'
CENTRAL_COMPOSITE_DESIGN = 'CENTRAL_COMPOSITE'
BOX_BEHNKEN_DESIGN = 'BOX_BEHNKEN'
PLACKETT_BURMAN_DESIGN = 'PLACKETT_BURMAN'
MIXTURE_DESIGN = 'MIXTURE'
CUSTOM_DESIGN = 'CUSTOM'

# Mapping between frontend and backend design types
DESIGN_TYPE_MAPPING = {
    'factorial': FACTORIAL_DESIGN,
    'fractional_factorial': FRACTIONAL_FACTORIAL_DESIGN,
    'response_surface': RESPONSE_SURFACE_DESIGN,
    'central_composite': CENTRAL_COMPOSITE_DESIGN,
    'box_behnken': BOX_BEHNKEN_DESIGN,
    'plackett_burman': PLACKETT_BURMAN_DESIGN,
    'mixture': MIXTURE_DESIGN,
    'custom': CUSTOM_DESIGN,
}

# Reverse mapping for frontend display
DESIGN_TYPE_DISPLAY = {v: k.replace('_', ' ').title() for k, v in DESIGN_TYPE_MAPPING.items()}
```

Then update the models.py file to use these constants:

```python
# Update in models.py
from .constants import (
    FACTORIAL_DESIGN, FRACTIONAL_FACTORIAL_DESIGN, RESPONSE_SURFACE_DESIGN,
    CENTRAL_COMPOSITE_DESIGN, BOX_BEHNKEN_DESIGN, PLACKETT_BURMAN_DESIGN,
    MIXTURE_DESIGN, CUSTOM_DESIGN
)

class ExperimentDesign(models.Model):
    DESIGN_TYPE_CHOICES = [
        (FACTORIAL_DESIGN, 'Factorial'),
        (FRACTIONAL_FACTORIAL_DESIGN, 'Fractional Factorial'),
        (RESPONSE_SURFACE_DESIGN, 'Response Surface'),
        (CENTRAL_COMPOSITE_DESIGN, 'Central Composite'),
        (BOX_BEHNKEN_DESIGN, 'Box-Behnken'),
        (PLACKETT_BURMAN_DESIGN, 'Plackett-Burman'),
        (MIXTURE_DESIGN, 'Mixture'),
        (CUSTOM_DESIGN, 'Custom'),
    ]
    
    design_type = models.CharField(
        max_length=50,
        choices=DESIGN_TYPE_CHOICES,
        default=FACTORIAL_DESIGN
    )
    # ... rest of the model
```

## 6. Implement Missing API Endpoints

Add the missing API endpoints in views.py:

```python
# Add to views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ExperimentDesign, ExperimentRun
from .serializers import (
    CreateExperimentDesignRequestSerializer,
    ExperimentDesignSerializer,
    AnalyzeDesignRequestSerializer
)
from .services.design_generator import generate_design
from .services.model_analyzer import analyze_design

class ExperimentDesignViewSet(viewsets.ModelViewSet):
    queryset = ExperimentDesign.objects.all()
    serializer_class = ExperimentDesignSerializer
    
    @action(detail=False, methods=['post'])
    def create_design(self, request):
        serializer = CreateExperimentDesignRequestSerializer(data=request.data)
        if serializer.is_valid():
            design_data = serializer.validated_data
            try:
                design = generate_design(
                    design_type=design_data['design_type'],
                    factors=design_data['factors'],
                    responses=design_data['responses'],
                    center_points=design_data.get('center_points', 0),
                    replicates=design_data.get('replicates', 1),
                    user=request.user
                )
                return Response(
                    ExperimentDesignSerializer(design).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        design = self.get_object()
        serializer = AnalyzeDesignRequestSerializer(data=request.data)
        if serializer.is_valid():
            analysis_data = serializer.validated_data
            try:
                results = analyze_design(
                    design=design,
                    response_var=analysis_data['response_var'],
                    model_type=analysis_data['model_type'],
                    selected_factors=analysis_data.get('selected_factors'),
                    confidence_level=analysis_data.get('confidence_level', 0.95)
                )
                return Response(results, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
```

## Next Steps After Critical Fixes

After implementing these critical fixes, we should:

1. Run the application to verify that the basic functionality works
2. Test the WebSocket connection for real-time updates
3. Test the design creation and analysis flows
4. Move on to the high-priority fixes identified in the debugging plan

By addressing these critical issues first, we can establish a working baseline for the DOE module before moving on to more comprehensive fixes and optimizations.