# Design of Experiments (DOE) Module Documentation

This document provides comprehensive documentation for the Design of Experiments (DOE) module, including component architecture, data flow, implementation details, and usage guides.

## Table of Contents

1. [Overview](#overview)
2. [Components Architecture](#components-architecture)
3. [Data Flow](#data-flow)
4. [Key Components](#key-components)
   - [Page Components](#page-components)
   - [Visualization Components](#visualization-components)
   - [WebSocket Integration](#websocket-integration)
   - [Responsive Utilities](#responsive-utilities)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Testing](#testing)
8. [Style Guide](#style-guide)
9. [Known Issues and Limitations](#known-issues-and-limitations)
10. [Future Improvements](#future-improvements)

## Overview

The Design of Experiments (DOE) module provides a comprehensive set of tools for designing, analyzing, and optimizing experimental designs in biotechnology and pharmaceutical applications. The module follows an educational structure with sections on fundamentals, design types, analysis methods, and case studies, along with an interactive design builder for creating and analyzing custom experimental designs.

### Key Features

- Interactive educational content on DOE principles
- Comprehensive design builder for creating factorial, fractional factorial, response surface, and screening designs
- Real-time analysis with WebSocket integration
- Interactive visualizations for design matrices, effect plots, interaction plots, and response surfaces
- Case studies showcasing DOE applications in biotechnology
- Responsive design that works on mobile, tablet, and desktop screens

## Components Architecture

The DOE module follows a hierarchical component structure:

```
DoePage
├── ResponsiveDoePage (wrapper)
├── Introduction
├── Fundamentals
├── DesignTypes
├── Analysis
├── CaseStudies
└── DesignBuilder
    ├── DesignMatrix
    ├── DesignBuilder3D
    ├── EffectPlot
    ├── InteractionPlot
    ├── ResponseSurfacePlot
    ├── ContourPlot
    ├── ResidualDiagnostics
    └── DOEWebSocketIntegration
```

### Component Layers

1. **Top-level container**: `DoePage` - Handles routing and main module structure
2. **Educational components**: Introduction, Fundamentals, DesignTypes, Analysis, CaseStudies
3. **Interactive tool**: DesignBuilder
4. **Visualization components**: Various plots and visualizations
5. **Integration components**: WebSocket integration for real-time updates
6. **Responsive components**: Responsive wrappers and utilities

## Data Flow

Data flows through the DOE module in the following manner:

1. **User Input**:
   - Design parameters (factors, responses, design type)
   - Analysis parameters (model type, significance level)
   - Optimization criteria

2. **Backend Processing**:
   - Design matrix generation
   - Statistical analysis
   - Model fitting
   - Optimization

3. **Real-time Updates**:
   - Progress updates via WebSockets
   - Incremental result delivery

4. **Visualization**:
   - Rendering of design matrix
   - Effect plots
   - Interaction plots
   - Residual diagnostics
   - Response surface/contour plots

5. **User Interaction**:
   - Selection of design points
   - Adjustment of parameters
   - Export of results

## Key Components

### Page Components

#### DoePage

The main container component for the DOE module. It handles routing between different sections and maintains global state.

```jsx
function DoePage() {
  // State management for tabs, user data, and content
  const [tabIndex, setTabIndex] = useState(0);
  const [user, setUser] = useState(null);
  const [content, setContent] = useState(null);

  // Tab definitions
  const tabs = [
    { label: "Introduction", icon: <InfoIcon /> },
    { label: "Fundamental Concepts", icon: <SchoolIcon /> },
    { label: "Design Types", icon: <CategoryIcon /> },
    { label: "Analysis & Interpretation", icon: <AssessmentIcon /> },
    { label: "Case Studies", icon: <CasesIcon /> },
    { label: "Design Builder", icon: <BuildIcon /> }
  ];

  // The component renders different content based on the selected tab
}
```

#### ResponsiveDoePage

A responsive wrapper component that provides adaptive layout for different screen sizes.

```jsx
function ResponsiveDoePage({
  children,
  tabs,
  activeTab,
  onTabChange,
  title
}) {
  // Responsive rendering with sidebar navigation on desktop,
  // bottom tabs on mobile, and adaptive content areas
}
```

#### Introduction

Educational component introducing DOE concepts with interactive examples.

#### Fundamentals

Educational component explaining fundamental DOE concepts with interactive visualizations.

#### DesignTypes

Component showcasing different types of experimental designs with interactive examples.

#### Analysis

Component for analyzing experimental designs with interactive visualizations.

#### CaseStudies

Component presenting real-world case studies of DOE applications in biotechnology.

#### DesignBuilder

Interactive tool for creating and analyzing experimental designs.

### Visualization Components

#### DesignMatrix

Visualizes the experimental design matrix with responsive layout for different screen sizes.

```jsx
function DesignMatrix({
  designMatrix,
  factors,
  responses,
  designType,
  onRunSelect,
  onExport
}) {
  // Renders a tabular or grid view of the experimental design matrix
  // with options for displaying coded/uncoded values, filtering, and exporting
}
```

#### DesignBuilder3D

3D visualization of the experimental design space.

```jsx
function DesignBuilder3D({
  designMatrix,
  factors,
  designType,
  onRunSelect
}) {
  // Creates a 3D visualization of the design space using Three.js/React Three Fiber
  // Allows for interactive exploration of the design points
}
```

#### EffectPlot

Visualizes the main effects of factors on the response variable.

```jsx
function EffectPlot({
  data,
  showConfidence,
  confidenceLevel,
  significanceLevel,
  onFactorSelect
}) {
  // Creates bar charts of factor effects with options for
  // confidence intervals, significance testing, and Pareto charts
}
```

#### InteractionPlot

Visualizes interactions between factors.

```jsx
function InteractionPlot({
  data,
  factors,
  responseVar,
  responseUnits,
  showConfidence,
  onInteractionSelect
}) {
  // Creates line plots showing how the effect of one factor
  // depends on the level of another factor
}
```

#### ResponseSurfacePlot

3D visualization of the response surface for quadratic models.

```jsx
function ResponseSurfacePlot({
  data,
  factors,
  model,
  responseVar,
  optimum
}) {
  // Creates a 3D surface plot showing the predicted response
  // across the design space
}
```

#### ContourPlot

2D contour visualization of the response surface.

```jsx
function ContourPlot({
  model,
  factors,
  responseVar,
  optimum,
  onPointSelect
}) {
  // Creates a 2D contour plot showing lines of equal response
  // across the design space
}
```

#### ResidualDiagnostics

Diagnostic plots for assessing model assumptions.

```jsx
function ResidualDiagnostics({
  data,
  factors,
  responseVar,
  model
}) {
  // Creates diagnostic plots for model validation:
  // - Predicted vs Actual
  // - Residuals vs Predicted
  // - Normal Probability
  // - Residual Histogram
  // - Residuals vs Run Order
  // - Leverage
  // - Cook's Distance
}
```

### WebSocket Integration

#### DOEWebSocketIntegration

Component for managing WebSocket connections and real-time updates.

```jsx
function DOEWebSocketIntegration({
  experimentId,
  onDesignGenerated,
  onAnalysisComplete,
  onOptimizationComplete,
  activeTask
}) {
  // Handles WebSocket connection for real-time updates during
  // design generation, analysis, and optimization
}
```

#### ProgressTracker

Component for displaying real-time progress of DOE operations.

```jsx
function ProgressTracker({
  status,
  progress,
  taskType,
  error,
  onComplete
}) {
  // Displays progress information with steps, percentage complete,
  // and status messages
}
```

#### useDOEWebSocket

Custom hook for WebSocket connection management.

```jsx
function useDOEWebSocket(experimentId, onMessage, onStatusChange) {
  // Custom hook that provides WebSocket connection utilities:
  // - Connection status
  // - Message sending
  // - Connection management
  // - Task-specific request methods
}
```

### Responsive Utilities

#### ResponsiveUtils

Utilities for responsive design.

```jsx
// Custom hooks for responsive design
const useIsMobile = () => {
  // Returns true if current screen is mobile sized
};

const useIsTablet = () => {
  // Returns true if current screen is tablet sized
};

const useIsDesktop = () => {
  // Returns true if current screen is desktop sized
};

// Components for responsive rendering
function ResponsiveView({ mobileContent, tabletContent, desktopContent }) {
  // Renders different content based on screen size
}

function MobileOnly({ children }) {
  // Only renders content on mobile screens
}

function TabletOnly({ children }) {
  // Only renders content on tablet screens
}

function DesktopOnly({ children }) {
  // Only renders content on desktop screens
}

function NotMobile({ children }) {
  // Only renders content on non-mobile screens
}

function ResponsiveGrid({ 
  children, 
  mobileColumns, 
  tabletColumns, 
  desktopColumns,
  spacing
}) {
  // Creates a responsive grid with configurable columns
}
```

#### responsiveStyles

Utility functions for responsive styling.

```jsx
// Responsive spacing
export const responsiveSpacing = (theme, multiplier = 1) => ({
  xs: theme.spacing(1 * multiplier),
  sm: theme.spacing(1.5 * multiplier),
  md: theme.spacing(2 * multiplier),
  lg: theme.spacing(2.5 * multiplier),
  xl: theme.spacing(3 * multiplier),
});

// Responsive typography sizing
export const responsiveTypography = (theme) => ({
  h1: {
    fontSize: {
      xs: '1.75rem',
      sm: '2rem',
      md: '2.25rem',
      lg: '2.5rem'
    }
  },
  // Other typography variants...
});

// Other responsive style utilities...
```

## API Reference

### DOE Service API

The DOE module interacts with the backend API through the `doeService.js` module, which provides the following functions:

#### Experiment Management

- `createExperiment(experimentData)` - Create a new DOE experiment
- `fetchExperiment(experimentId)` - Fetch experiment details
- `updateExperiment(experimentId, updateData)` - Update experiment details
- `deleteExperiment(experimentId)` - Delete an experiment
- `fetchExperiments(params)` - Fetch list of user's experiments

#### Design Generation

- `generateDesign(experimentId, designParams)` - Generate a new design matrix
- `fetchDesignMatrix(experimentId)` - Fetch design matrix for an experiment

#### Result Management

- `updateExperimentalResults(experimentId, resultsData)` - Update experimental results

#### Analysis

- `analyzeDesign(analysisParams)` - Analyze experimental design
- `fetchEffectPlots(designId, responseVar, modelType)` - Fetch effect plots for analysis
- `fetchInteractionPlots(designId, responseVar, modelType)` - Fetch interaction plots for analysis
- `fetchResidualPlots(designId, responseVar, modelType)` - Fetch residual plots for analysis
- `fetchOptimizationResults(designId, responseVar, modelType)` - Fetch optimization results

#### Import/Export

- `exportExperiment(experimentId, format)` - Export experiment data
- `importExperiment(file)` - Import experiment data
- `generateSampleDataset(datasetType)` - Generate sample dataset

#### WebSocket

- `initializeWebSocket(experimentId, onMessage, onStatusChange)` - Initialize WebSocket for real-time DOE analysis

### WebSocket Message Types

WebSocket communication uses the following message types:

#### Incoming Messages (from server)

- `progress_update` - Progress update for ongoing tasks
- `task_complete` - Task completed successfully
- `task_error` - Error occurred during task execution
- `notification` - General notification

#### Outgoing Messages (to server)

- `request_status` - Request status updates for ongoing tasks
- `request_analysis` - Request to run analysis
- `generate_design` - Request to generate a design
- `optimize` - Request to run optimization

## Usage Examples

### Creating a New Experiment

```jsx
// Example of creating a new DOE experiment
const handleCreateExperiment = async () => {
  try {
    const experimentData = {
      name: 'Protein Expression Optimization',
      description: 'Factorial design to optimize protein expression in E. coli',
      experimentType: 'factorial'
    };
    
    const newExperiment = await createExperiment(experimentData);
    setExperimentId(newExperiment.id);
  } catch (error) {
    console.error('Error creating experiment:', error);
  }
};
```

### Generating a Design

```jsx
// Example of generating a factorial design
const handleGenerateDesign = async () => {
  const designParams = {
    designType: 'factorial',
    factors: [
      { name: 'Temperature', low: 25, high: 37, units: '°C' },
      { name: 'IPTG', low: 0.1, high: 1.0, units: 'mM' },
      { name: 'OD600', low: 0.6, high: 1.2, units: '' }
    ],
    responses: [
      { name: 'Protein Yield', units: 'mg/L' }
    ],
    centerPoints: 2,
    replicates: 1
  };
  
  // Option 1: Using REST API
  const design = await generateDesign(experimentId, designParams);
  
  // Option 2: Using WebSocket for real-time updates
  const wsResult = requestDesignGeneration(designParams);
};
```

### Analyzing Results

```jsx
// Example of analyzing experimental results
const handleAnalyzeResults = async () => {
  const analysisParams = {
    designId: 'design-123',
    responseVar: 'Protein Yield',
    modelType: 'quadratic',
    confidenceLevel: 0.95
  };
  
  // Option 1: Using REST API
  const analysisResults = await analyzeDesign(analysisParams);
  
  // Option 2: Using WebSocket for real-time updates
  const wsResult = requestAnalysisUpdate(analysisParams);
};
```

### Using Responsive Components

```jsx
// Example of using responsive components
function MyComponent() {
  const isMobile = useIsMobile();
  
  return (
    <Box>
      <ResponsiveView
        mobileContent={<SimplifiedView />}
        tabletContent={<StandardView />}
        desktopContent={<EnhancedView />}
      />
      
      <ResponsiveGrid
        mobileColumns={1}
        tabletColumns={2}
        desktopColumns={3}
        spacing={2}
      >
        <Item>Item 1</Item>
        <Item>Item 2</Item>
        <Item>Item 3</Item>
      </ResponsiveGrid>
    </Box>
  );
}
```

## Testing

The DOE module includes tests for components and services. Tests are located in the `__tests__` directory within each component folder.

### Component Testing

We use Jest and React Testing Library for component testing:

```jsx
// Example test for EffectPlot component
import { render, screen, fireEvent } from '@testing-library/react';
import EffectPlot from '../EffectPlot';

describe('EffectPlot', () => {
  const mockData = [
    { factor: 'Temperature', effect: 10.5, pValue: 0.02 },
    { factor: 'pH', effect: -5.2, pValue: 0.04 },
    { factor: 'Time', effect: 2.1, pValue: 0.18 }
  ];
  
  it('renders effect plot with data', () => {
    render(<EffectPlot data={mockData} />);
    expect(screen.getByText('Temperature')).toBeInTheDocument();
    expect(screen.getByText('pH')).toBeInTheDocument();
    expect(screen.getByText('Time')).toBeInTheDocument();
  });
  
  // Additional tests...
});
```

### Service Testing

We use Jest for service testing:

```jsx
// Example test for DOE service
import {
  createExperiment,
  fetchExperiment
} from '../doeService';

// Mock fetch function
global.fetch = jest.fn();

describe('doeService', () => {
  beforeEach(() => {
    fetch.mockClear();
  });
  
  it('creates experiment successfully', async () => {
    const mockResponse = { id: '123', name: 'Test Experiment' };
    fetch.mockImplementationOnce(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    }));
    
    const result = await createExperiment({ name: 'Test Experiment' });
    expect(result).toEqual(mockResponse);
    expect(fetch).toHaveBeenCalledTimes(1);
  });
  
  // Additional tests...
});
```

## Style Guide

The DOE module follows a consistent style guide to ensure maintainability and readability:

### Component Structure

1. **Imports**: Group imports by type (React, Material-UI, custom components, etc.)
2. **Component declaration**: Use function components with TypeScript props interface
3. **State declarations**: Group state declarations at the beginning of the component
4. **Effects and callbacks**: Place effects and callbacks after state declarations
5. **Helper functions**: Define helper functions before the return statement
6. **Return statement**: Keep the JSX clean and readable with appropriate indentation
7. **Prop types**: Define prop types at the end of the file

### Naming Conventions

1. **Components**: PascalCase (e.g., `EffectPlot`, `DesignBuilder`)
2. **Functions**: camelCase (e.g., `handleTabChange`, `fetchDesignMatrix`)
3. **Variables**: camelCase (e.g., `designMatrix`, `factorList`)
4. **Constants**: UPPER_CASE (e.g., `MAX_FACTORS`, `DEFAULT_CONFIDENCE_LEVEL`)
5. **Files**: PascalCase for components, camelCase for utilities and services

### CSS Styling

1. Use Material-UI's `sx` prop for component styling
2. Use responsive spacing and typography defined in `responsiveStyles.js`
3. Use theme colors and avoid hardcoded color values
4. Use spacing units from the theme (e.g., `theme.spacing(2)`) rather than fixed pixel values

## Known Issues and Limitations

1. **Large Design Matrices**: Performance may degrade with very large design matrices (>100 runs)
2. **3D Visualizations**: 3D visualizations require WebGL support and may not work on all mobile devices
3. **Complex Interactions**: The visualization of higher-order interactions (>2 factors) is limited
4. **WebSocket Reconnection**: WebSocket reconnection logic may not handle all network failure scenarios
5. **Offline Mode**: The module does not currently support offline operation

## Future Improvements

1. **Enhanced Optimization**: Implement multi-objective optimization for response optimization
2. **Design Space Explorer**: Add an interactive design space explorer for visualizing factor constraints
3. **Custom Design Generation**: Support for custom design generation with specific constraints
4. **Power Analysis**: Add power analysis for experimental designs
5. **Data Import Enhancements**: Improve data import capabilities with better error handling and validation
6. **Augmented Designs**: Support for augmenting existing designs with additional runs
7. **Mobile Optimization**: Further optimize the mobile experience for data entry and visualization
8. **Offline Support**: Implement offline capabilities with local storage and synchronization
9. **Collaborative Editing**: Add real-time collaborative editing of experimental designs
10. **Machine Learning Integration**: Integrate machine learning methods for analyzing complex response surfaces