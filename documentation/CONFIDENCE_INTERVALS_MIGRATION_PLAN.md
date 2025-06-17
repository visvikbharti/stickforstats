# Confidence Intervals Module Migration Plan

## Overview

This document outlines the comprehensive plan for migrating the Confidence Intervals module from Streamlit to our Django/React architecture. The migration will maintain feature parity while leveraging the advantages of the new architecture for improved performance, interactivity, and user experience.

## Current State Analysis

The existing Streamlit-based Confidence Intervals module includes:

1. **Theoretical Foundations**
   - Formal definitions of confidence intervals
   - Essential properties (coverage, precision, etc.)
   - Visualizations of coverage properties

2. **Interactive Simulations**
   - Coverage Properties: Demonstrates actual coverage of intervals
   - Sample Size Effects: Shows how sample size affects interval width
   - Bootstrapping: Illustrates bootstrap confidence intervals
   - Transformations: Shows effects of transformations on intervals
   - Non-normality Impact: Demonstrates robustness to non-normality

3. **Advanced Methods**
   - Bayesian credible intervals
   - Bootstrap methods
   - Profile likelihood methods

4. **Real-world Applications**
   - Clinical trials analysis
   - A/B testing examples
   - Environmental monitoring
   - Manufacturing quality control

5. **Mathematical Proofs**
   - Derivations of common interval formulas
   - Optimality properties
   - Statistical theory

6. **Educational Visualizations**
   - Coverage animation
   - Interval construction process
   - Distribution visualizations

## Django Backend Structure

The Django backend is already partially implemented with models and services:

1. **Models**
   - `ConfidenceIntervalProject`: Project metadata
   - `IntervalData`: Sample data for calculations
   - `IntervalResult`: Calculation results
   - `SimulationResult`: Simulation results
   - `EducationalResource`: Educational content

2. **Services**
   - `IntervalService`: Calculations for various interval types
   - `BootstrapService`: Bootstrap simulation methods

3. **API Endpoints**
   - Project management
   - Data management
   - Calculation operations
   - Simulation controls
   - Educational resources

## React Frontend Structure

The React frontend has foundational components but requires completion:

1. **Core Components**
   - `ConfidenceIntervalsPage`: Main container (implemented)
   - Tab navigation system (implemented)

2. **Calculators**
   - `CalculatorDashboard`: Main calculator interface (partial)
   - `SampleBasedCalculator`: For sample data calculations (partial)
   - `BootstrapCalculator`: For bootstrap methods (partial)

3. **Educational Components**
   - `TheoryFoundations`: For theoretical content (partial)
   - Missing components for other educational sections

4. **Visualizations**
   - `IntervalVisualization`: Basic interval visualization (implemented)
   - `CoverageAnimation`: For coverage simulation (partial)
   - `IntervalConstructionAnimation`: Construction process (partial)

5. **Simulations**
   - `InteractiveSimulations`: Main simulations container (missing)
   - Individual simulation components (missing)

## Implementation Phases

### Phase 1: Core Educational Components

#### 1.1. Theory Foundations
- Implement the theoretical foundations page with definitions, properties, and basic visualizations
- Create interactive coverage visualization component
- Develop duality visualization (hypothesis testing vs. confidence intervals)

#### 1.2. Mathematical Derivations
- Implement derivations of common interval types
- Create interactive demonstrations for each interval type
- Implement visualization of the mathematical foundation of each method

#### 1.3. Interpretation Section
- Develop correct interpretations of confidence intervals
- Create multi-interval visualization to demonstrate the frequentist framework
- Implement Bayesian vs. Frequentist comparison visualizations

### Phase 2: Interactive Simulations

#### 2.1. Coverage Properties Simulation
- Implement simulation controls for interval type selection
- Create visualization of coverage results
- Develop parameter controls and reporting components

#### 2.2. Sample Size Effects Simulation
- Implement sample size range controls
- Create visualizations for both coverage and width vs. sample size
- Develop logarithmic visualization of the 1/√n relationship

#### 2.3. Bootstrap Simulation
- Implement bootstrap controls (method, sample size, etc.)
- Create bootstrap distribution visualization
- Develop comparison with parametric methods

#### 2.4. Non-normality Impact
- Implement distribution selection controls
- Create visualization of intervals under different distributions
- Develop robustness metrics display

### Phase 3: Advanced Methods

#### 3.1. Bayesian Methods
- Implement prior selection controls
- Create posterior and credible interval visualizations
- Develop comparison with frequentist intervals

#### 3.2. Profile Likelihood
- Implement profile likelihood calculation
- Create visualization of likelihood function and interval
- Develop comparison with standard methods

#### 3.3. Bootstrap Variants
- Implement BCa and percentile bootstrap methods
- Create visualization of different bootstrap methods
- Develop performance comparison metrics

### Phase 4: Applications and Integration

#### 4.1. Real-world Applications
- Implement clinical trials example
- Create A/B testing simulation
- Develop environmental and manufacturing examples

#### 4.2. WebSocket Integration
- Implement real-time progress updates for long-running simulations
- Create user notification system for simulation completion
- Develop cancellation mechanism for simulations

#### 4.3. Project Management
- Implement project saving and loading
- Create history tracking for interval calculations
- Develop export functionality for results

## Component Implementation Details

### 1. Interactive Coverage Visualization

```jsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, Slider, Select, MenuItem, Button, Paper } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CoverageVisualization = ({ 
  intervalType = 'MEAN_T',
  confidenceLevel = 0.95,
  sampleSize = 30,
  onRunSimulation = () => {},
  simulationResult = null,
  isLoading = false
}) => {
  // Implementation details...
};
```

### 2. Sample Size Effects Component

```jsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, Slider, Select, MenuItem, Button, Paper, Grid } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SampleSizeEffects = ({
  intervalType = 'MEAN_T',
  confidenceLevel = 0.95,
  minSampleSize = 5,
  maxSampleSize = 100,
  onRunSimulation = () => {},
  simulationResult = null,
  isLoading = false
}) => {
  // Implementation details...
};
```

### 3. Bootstrap Simulation Component

```jsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, Slider, Select, MenuItem, Button, Paper, Grid } from '@mui/material';
import { Histogram, DensityPlot } from './visualization-components';

const BootstrapSimulation = ({
  statistic = 'MEAN',
  method = 'PERCENTILE',
  sampleSize = 30,
  resamples = 1000,
  distribution = 'NORMAL',
  onRunSimulation = () => {},
  simulationResult = null,
  isLoading = false
}) => {
  // Implementation details...
};
```

## API Integration

### 1. Calculation API

```javascript
// probabilityDistributionsApi.js
export const calculateConfidenceInterval = async (params) => {
  try {
    const response = await axios.post('/api/confidence-intervals/calculate/calculate/', params);
    return response.data;
  } catch (error) {
    console.error('Error calculating confidence interval:', error);
    throw error;
  }
};
```

### 2. Simulation API

```javascript
// confidenceIntervalsApi.js
export const runCoverageSimulation = async (params) => {
  try {
    const response = await axios.post('/api/confidence-intervals/calculate/coverage_simulation/', params);
    return response.data;
  } catch (error) {
    console.error('Error running coverage simulation:', error);
    throw error;
  }
};
```

### 3. WebSocket Integration

```javascript
// useConfidenceIntervalSimulation.js
import { useState, useEffect, useCallback } from 'react';

export const useConfidenceIntervalSimulation = (projectId) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState('');
  
  useEffect(() => {
    // WebSocket connection setup...
  }, [projectId]);
  
  // Implementation details...
};
```

## Data Flow

1. **User Interaction**
   - User selects simulation type and parameters
   - Frontend validates and prepares request

2. **API Request**
   - React component calls appropriate API endpoint
   - Parameters are sent to the backend

3. **Backend Processing**
   - Django view receives request and validates
   - Calls appropriate service method
   - For simulations, creates background task

4. **WebSocket Updates**
   - Backend sends progress updates via WebSocket
   - Frontend updates UI with progress

5. **Result Rendering**
   - Backend sends final result
   - Frontend renders visualization and metrics

## Testing Strategy

1. **Unit Tests**
   - Test individual calculation methods
   - Test visualization components
   - Test API integration

2. **Integration Tests**
   - Test full workflow from UI to backend to database
   - Test WebSocket communication

3. **Visual Regression Tests**
   - Compare visualization outputs with expected results
   - Verify simulation visualizations

## Migration Timeline

| Phase | Component | Estimated Duration |
|-------|-----------|-------------------|
| 1.1 | Theory Foundations | 2 days |
| 1.2 | Mathematical Derivations | 2 days |
| 1.3 | Interpretation Section | 1 day |
| 2.1 | Coverage Properties Simulation | 2 days |
| 2.2 | Sample Size Effects Simulation | 2 days |
| 2.3 | Bootstrap Simulation | 2 days |
| 2.4 | Non-normality Impact | 1 day |
| 3.1 | Bayesian Methods | 2 days |
| 3.2 | Profile Likelihood | 1 day |
| 3.3 | Bootstrap Variants | 1 day |
| 4.1 | Real-world Applications | 2 days |
| 4.2 | WebSocket Integration | 1 day |
| 4.3 | Project Management | 1 day |
| - | Testing and Refinement | 2 days |
| **Total** | | **22 days** |

## Completion Criteria

The migration will be considered complete when:

1. All features from the original Streamlit app are available and functioning
2. All interactive simulations provide the same or better educational value
3. Test suite passes with >90% coverage
4. UI is responsive and provides a good user experience
5. Documentation is complete and accurate

## Enhancements Over Streamlit Version

1. **Performance Improvements**
   - Faster calculations with pre-compiled Python vs. Streamlit's recomputation
   - Efficient chart rendering with Chart.js versus Plotly
   - Reduced latency with API-driven architecture

2. **User Experience Enhancements**
   - More responsive UI with React's virtual DOM
   - Better state management and navigation
   - Project saving and loading capabilities

3. **Visualization Improvements**
   - Interactive parameter controls with real-time updates
   - Smoother animations for educational concepts
   - More consistent styling and theming

4. **Architectural Advantages**
   - Separation of concerns with backend calculation logic
   - Reusability of components across modules
   - Better scalability with Django's mature ecosystem