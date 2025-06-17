# DOE API Reference

This document provides comprehensive documentation for the Design of Experiments (DOE) API, including endpoints, request/response formats, WebSocket communication, and example usage.

## Table of Contents

1. [REST API Endpoints](#rest-api-endpoints)
   - [Experiment Management](#experiment-management)
   - [Design Management](#design-management)
   - [Analysis Operations](#analysis-operations)
   - [Data Operations](#data-operations)
2. [WebSocket API](#websocket-api)
   - [Connection Setup](#connection-setup)
   - [Message Types](#message-types)
   - [Progress Updates](#progress-updates)
   - [Error Handling](#error-handling)
3. [Data Models](#data-models)
   - [Experiment](#experiment)
   - [Factor](#factor)
   - [Response](#response)
   - [Design](#design)
   - [Result](#result)
4. [Example Usage](#example-usage)
   - [Creating a New Experiment](#creating-a-new-experiment)
   - [Generating a Design](#generating-a-design)
   - [Analyzing Results](#analyzing-results)
   - [Using WebSockets](#using-websockets)
5. [Error Codes](#error-codes)
6. [Rate Limits](#rate-limits)

## REST API Endpoints

Base URL: `/api/doe`

### Experiment Management

#### Create Experiment

- **URL**: `/experiments/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "name": "Protein Expression Optimization",
    "description": "Factorial design to optimize protein expression in E. coli",
    "experimentType": "factorial"
  }
  ```
- **Response**: 
  ```json
  {
    "id": "exp-123",
    "name": "Protein Expression Optimization",
    "description": "Factorial design to optimize protein expression in E. coli",
    "experimentType": "factorial",
    "created": "2023-08-15T10:30:00Z",
    "updated": "2023-08-15T10:30:00Z",
    "userId": "user-456"
  }
  ```
- **Status Codes**:
  - `201 Created`: Experiment created successfully
  - `400 Bad Request`: Invalid request data
  - `401 Unauthorized`: Authentication required

#### Get Experiment

- **URL**: `/experiments/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Experiment ID
- **Response**: 
  ```json
  {
    "id": "exp-123",
    "name": "Protein Expression Optimization",
    "description": "Factorial design to optimize protein expression in E. coli",
    "experimentType": "factorial",
    "created": "2023-08-15T10:30:00Z",
    "updated": "2023-08-15T10:30:00Z",
    "userId": "user-456",
    "designs": [
      {
        "id": "design-789",
        "name": "Initial Factorial Design",
        "designType": "factorial",
        "created": "2023-08-15T10:35:00Z"
      }
    ]
  }
  ```
- **Status Codes**:
  - `200 OK`: Experiment retrieved successfully
  - `404 Not Found`: Experiment not found
  - `401 Unauthorized`: Authentication required

#### Update Experiment

- **URL**: `/experiments/{id}/`
- **Method**: `PATCH`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Experiment ID
- **Request Body**:
  ```json
  {
    "name": "Updated Experiment Name",
    "description": "Updated description"
  }
  ```
- **Response**: 
  ```json
  {
    "id": "exp-123",
    "name": "Updated Experiment Name",
    "description": "Updated description",
    "experimentType": "factorial",
    "created": "2023-08-15T10:30:00Z",
    "updated": "2023-08-15T10:40:00Z",
    "userId": "user-456"
  }
  ```
- **Status Codes**:
  - `200 OK`: Experiment updated successfully
  - `400 Bad Request`: Invalid request data
  - `404 Not Found`: Experiment not found
  - `401 Unauthorized`: Authentication required

#### Delete Experiment

- **URL**: `/experiments/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Experiment ID
- **Response**: No content
- **Status Codes**:
  - `204 No Content`: Experiment deleted successfully
  - `404 Not Found`: Experiment not found
  - `401 Unauthorized`: Authentication required

#### List Experiments

- **URL**: `/experiments/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Params**:
  - `page` [int] - Page number for pagination
  - `page_size` [int] - Number of results per page
  - `search` [string] - Search term for experiment name/description
  - `type` [string] - Filter by experiment type
  - `sort` [string] - Sort field (created, updated, name)
  - `order` [string] - Sort order (asc, desc)
- **Response**: 
  ```json
  {
    "count": 10,
    "next": "/api/doe/experiments/?page=2&page_size=5",
    "previous": null,
    "results": [
      {
        "id": "exp-123",
        "name": "Protein Expression Optimization",
        "description": "Factorial design to optimize protein expression in E. coli",
        "experimentType": "factorial",
        "created": "2023-08-15T10:30:00Z",
        "updated": "2023-08-15T10:30:00Z"
      },
      // More experiments...
    ]
  }
  ```
- **Status Codes**:
  - `200 OK`: Experiments retrieved successfully
  - `401 Unauthorized`: Authentication required

### Design Management

#### Generate Design

- **URL**: `/experiments/{id}/designs/`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Experiment ID
- **Request Body**:
  ```json
  {
    "designType": "factorial",
    "factors": [
      {
        "name": "Temperature",
        "low": 25,
        "high": 37,
        "units": "°C"
      },
      {
        "name": "IPTG",
        "low": 0.1,
        "high": 1.0,
        "units": "mM"
      },
      {
        "name": "OD600",
        "low": 0.6,
        "high": 1.2,
        "units": ""
      }
    ],
    "responses": [
      {
        "name": "Protein Yield",
        "units": "mg/L"
      }
    ],
    "centerPoints": 2,
    "replicates": 1
  }
  ```
- **Response**: 
  ```json
  {
    "id": "design-789",
    "experimentId": "exp-123",
    "designType": "factorial",
    "factors": [
      {
        "name": "Temperature",
        "low": 25,
        "high": 37,
        "units": "°C"
      },
      // More factors...
    ],
    "responses": [
      {
        "name": "Protein Yield",
        "units": "mg/L"
      }
    ],
    "runs": [
      {
        "runOrder": 1,
        "stdOrder": 1,
        "Temperature_coded": -1,
        "IPTG_coded": -1,
        "OD600_coded": -1,
        "Temperature_natural": 25,
        "IPTG_natural": 0.1,
        "OD600_natural": 0.6
      },
      // More runs...
    ],
    "properties": {
      "centerPoints": 2,
      "replicates": 1,
      "resolution": "Full",
      "df": 4
    },
    "created": "2023-08-15T10:35:00Z"
  }
  ```
- **Status Codes**:
  - `201 Created`: Design generated successfully
  - `400 Bad Request`: Invalid request data
  - `404 Not Found`: Experiment not found
  - `401 Unauthorized`: Authentication required

#### Get Design

- **URL**: `/designs/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Design ID
- **Response**: 
  ```json
  {
    "id": "design-789",
    "experimentId": "exp-123",
    "designType": "factorial",
    "factors": [
      // Factors...
    ],
    "responses": [
      // Responses...
    ],
    "runs": [
      // Runs...
    ],
    "properties": {
      "centerPoints": 2,
      "replicates": 1,
      "resolution": "Full",
      "df": 4
    },
    "created": "2023-08-15T10:35:00Z"
  }
  ```
- **Status Codes**:
  - `200 OK`: Design retrieved successfully
  - `404 Not Found`: Design not found
  - `401 Unauthorized`: Authentication required

#### Get Latest Design

- **URL**: `/experiments/{id}/designs/latest/`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Experiment ID
- **Response**: Same as Get Design
- **Status Codes**:
  - `200 OK`: Design retrieved successfully
  - `404 Not Found`: Design not found or no designs for experiment
  - `401 Unauthorized`: Authentication required

#### Update Experimental Results

- **URL**: `/experiments/{id}/results/`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Experiment ID
- **Request Body**:
  ```json
  {
    "results": [
      {
        "runOrder": 1,
        "Protein Yield": 120.5
      },
      {
        "runOrder": 2,
        "Protein Yield": 95.2
      },
      // More run results...
    ]
  }
  ```
- **Response**: 
  ```json
  {
    "id": "design-789",
    "experimentId": "exp-123",
    "designType": "factorial",
    "factors": [
      // Factors...
    ],
    "responses": [
      // Responses...
    ],
    "runs": [
      {
        "runOrder": 1,
        "stdOrder": 1,
        "Temperature_coded": -1,
        "IPTG_coded": -1,
        "OD600_coded": -1,
        "Temperature_natural": 25,
        "IPTG_natural": 0.1,
        "OD600_natural": 0.6,
        "Protein Yield": 120.5
      },
      // More runs with results...
    ],
    "properties": {
      // Properties...
    },
    "created": "2023-08-15T10:35:00Z",
    "updated": "2023-08-15T11:00:00Z"
  }
  ```
- **Status Codes**:
  - `200 OK`: Results updated successfully
  - `400 Bad Request`: Invalid request data
  - `404 Not Found`: Experiment or design not found
  - `401 Unauthorized`: Authentication required

### Analysis Operations

#### Analyze Design

- **URL**: `/designs/{id}/analyze/`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Design ID
- **Request Body**:
  ```json
  {
    "responseVar": "Protein Yield",
    "modelType": "quadratic",
    "selectedFactors": ["Temperature", "IPTG", "OD600"],
    "confidenceLevel": 0.95
  }
  ```
- **Response**: 
  ```json
  {
    "modelSummary": {
      "r_squared": 0.92,
      "adj_r_squared": 0.89,
      "rmse": 10.5,
      "press": 456.7
    },
    "coefficients": {
      "intercept": 125.3,
      "Temperature": -42.1,
      "IPTG": 18.7,
      "OD600": 5.2,
      "Temperature:IPTG": -15.3,
      "Temperature^2": -8.9
    },
    "effects": [
      {
        "factor": "Temperature",
        "effect": -84.2,
        "stdError": 12.3,
        "pValue": 0.0012,
        "lowerCI": -108.5,
        "upperCI": -59.9
      },
      // More effects...
    ],
    "anova": {
      "df_model": 5,
      "df_residual": 10,
      "df_total": 15,
      "ss_model": 25362.4,
      "ss_residual": 2104.5,
      "ss_total": 27466.9,
      "ms_model": 5072.48,
      "ms_residual": 210.45,
      "f_value": 24.1,
      "p_value": 0.00003
    }
  }
  ```
- **Status Codes**:
  - `200 OK`: Analysis completed successfully
  - `400 Bad Request`: Invalid request data or missing response values
  - `404 Not Found`: Design not found
  - `401 Unauthorized`: Authentication required

#### Get Effect Plots

- **URL**: `/designs/{id}/plots/effects/`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Design ID
- **Request Body**:
  ```json
  {
    "responseVar": "Protein Yield",
    "modelType": "quadratic"
  }
  ```
- **Response**: 
  ```json
  [
    {
      "factor": "Temperature",
      "effect": -84.2,
      "standardized": -6.84,
      "pValue": 0.0012,
      "lowerCI": -108.5,
      "upperCI": -59.9
    },
    // More effect data...
  ]
  ```
- **Status Codes**:
  - `200 OK`: Plot data retrieved successfully
  - `400 Bad Request`: Invalid request data
  - `404 Not Found`: Design not found
  - `401 Unauthorized`: Authentication required

#### Get Interaction Plots

- **URL**: `/designs/{id}/plots/interactions/`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Design ID
- **Request Body**:
  ```json
  {
    "responseVar": "Protein Yield",
    "modelType": "quadratic"
  }
  ```
- **Response**: 
  ```json
  [
    {
      "factors": ["Temperature", "IPTG"],
      "data": [
        {
          "Temperature": -1,
          "IPTG": -1,
          "response": 120.5
        },
        // More data points...
      ],
      "pValue": 0.0342,
      "interpretation": "Temperature and IPTG show significant interaction. The effect of IPTG is stronger at lower temperatures."
    },
    // More interaction data...
  ]
  ```
- **Status Codes**:
  - `200 OK`: Plot data retrieved successfully
  - `400 Bad Request`: Invalid request data
  - `404 Not Found`: Design not found
  - `401 Unauthorized`: Authentication required

#### Get Residual Plots

- **URL**: `/designs/{id}/plots/residuals/`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Design ID
- **Request Body**:
  ```json
  {
    "responseVar": "Protein Yield",
    "modelType": "quadratic"
  }
  ```
- **Response**: 
  ```json
  {
    "predicted_vs_actual": [
      {
        "run": 1,
        "predicted": 118.3,
        "actual": 120.5,
        "residual": 2.2
      },
      // More data points...
    ],
    "residuals_vs_predicted": [
      {
        "run": 1,
        "predicted": 118.3,
        "residual": 2.2
      },
      // More data points...
    ],
    "normal_probability": [
      {
        "run": 1,
        "residual": 2.2,
        "quantile": -1.2
      },
      // More data points...
    ],
    "residual_histogram": [
      {
        "bin": -15,
        "frequency": 1
      },
      // More histogram bins...
    ],
    "residuals_vs_run": [
      {
        "run": 1,
        "residual": 2.2
      },
      // More data points...
    ],
    "leverage": [
      {
        "run": 1,
        "leverage": 0.25
      },
      // More data points...
    ],
    "cooks_distance": [
      {
        "run": 1,
        "cooksd": 0.05
      },
      // More data points...
    ],
    "critical_values": {
      "leverage": 0.5,
      "cooks_d": 0.5
    }
  }
  ```
- **Status Codes**:
  - `200 OK`: Plot data retrieved successfully
  - `400 Bad Request`: Invalid request data
  - `404 Not Found`: Design not found
  - `401 Unauthorized`: Authentication required

#### Get Optimization Results

- **URL**: `/designs/{id}/optimize/`
- **Method**: `POST`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Design ID
- **Request Body**:
  ```json
  {
    "responseVar": "Protein Yield",
    "modelType": "quadratic",
    "goal": "maximize",
    "constraints": [
      {
        "factor": "Temperature",
        "min": -1,
        "max": 0.5
      },
      {
        "factor": "IPTG",
        "min": -0.5,
        "max": 1
      }
    ]
  }
  ```
- **Response**: 
  ```json
  {
    "settings": {
      "Temperature": -0.8,
      "IPTG": 1.0,
      "OD600": 0.2
    },
    "predicted": 189.3,
    "lowerCI": 175.1,
    "upperCI": 203.5,
    "desirability": 0.92,
    "naturalSettings": {
      "Temperature": 27.4,
      "IPTG": 1.0,
      "OD600": 0.9
    }
  }
  ```
- **Status Codes**:
  - `200 OK`: Optimization completed successfully
  - `400 Bad Request`: Invalid request data
  - `404 Not Found`: Design not found
  - `401 Unauthorized`: Authentication required

### Data Operations

#### Export Experiment

- **URL**: `/experiments/{id}/export/`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Params**: 
  - `id` [string] - Experiment ID
- **Query Params**:
  - `format` [string] - Export format (csv, excel, json)
- **Response**: File download
- **Status Codes**:
  - `200 OK`: Export completed successfully
  - `400 Bad Request`: Invalid format
  - `404 Not Found`: Experiment not found
  - `401 Unauthorized`: Authentication required

#### Import Experiment

- **URL**: `/import/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `file` [file] - Experiment file (CSV, Excel, or JSON)
- **Response**: 
  ```json
  {
    "id": "exp-456",
    "name": "Imported Experiment",
    "experimentType": "factorial",
    "factors": 3,
    "responses": 1,
    "runs": 8
  }
  ```
- **Status Codes**:
  - `201 Created`: Import completed successfully
  - `400 Bad Request`: Invalid file format or data
  - `401 Unauthorized`: Authentication required

#### Generate Sample Dataset

- **URL**: `/samples/{type}/`
- **Method**: `GET`
- **Auth Required**: Yes
- **URL Params**: 
  - `type` [string] - Sample dataset type (factorial, response_surface, etc.)
- **Response**: 
  ```json
  {
    "name": "Sample Protein Expression Experiment",
    "description": "Sample factorial design for protein expression optimization",
    "designType": "factorial",
    "factors": [
      // Factors...
    ],
    "responses": [
      // Responses...
    ],
    "runs": [
      // Runs with results...
    ]
  }
  ```
- **Status Codes**:
  - `200 OK`: Sample dataset generated successfully
  - `400 Bad Request`: Invalid dataset type
  - `401 Unauthorized`: Authentication required

## WebSocket API

### Connection Setup

- **WebSocket URL**: `/ws/doe/{experiment_id}/`
- **Authentication**: Include authorization header or token in connection request

### Message Types

#### Outgoing Messages (Client to Server)

##### Request Status

```json
{
  "type": "request_status",
  "tasks": ["design_generation", "analysis", "optimization"]
}
```

##### Request Analysis

```json
{
  "type": "request_analysis",
  "data": {
    "designId": "design-789",
    "responseVar": "Protein Yield",
    "modelType": "quadratic",
    "selectedFactors": ["Temperature", "IPTG", "OD600"],
    "confidenceLevel": 0.95
  }
}
```

##### Generate Design

```json
{
  "type": "generate_design",
  "data": {
    "designType": "factorial",
    "factors": [
      {
        "name": "Temperature",
        "low": 25,
        "high": 37,
        "units": "°C"
      },
      // More factors...
    ],
    "responses": [
      {
        "name": "Protein Yield",
        "units": "mg/L"
      }
    ],
    "centerPoints": 2,
    "replicates": 1
  }
}
```

##### Optimize Response

```json
{
  "type": "optimize",
  "data": {
    "designId": "design-789",
    "responseVar": "Protein Yield",
    "modelType": "quadratic",
    "goal": "maximize",
    "constraints": [
      {
        "factor": "Temperature",
        "min": -1,
        "max": 0.5
      },
      // More constraints...
    ]
  }
}
```

#### Incoming Messages (Server to Client)

##### Progress Update

```json
{
  "type": "progress_update",
  "task_type": "design_generation",
  "status": "in_progress",
  "percent": 45,
  "step": "Generating Design Matrix",
  "message": "Creating factorial design with 3 factors",
  "details": "Processing factor combinations",
  "items_processed": 4,
  "total_items": 10,
  "timestamp": "2023-08-15T10:36:00Z"
}
```

##### Task Complete

```json
{
  "type": "task_complete",
  "task_type": "design_generation",
  "status": "completed",
  "result": {
    "id": "design-789",
    "experimentId": "exp-123",
    "designType": "factorial",
    "factors": [
      // Factors...
    ],
    "responses": [
      // Responses...
    ],
    "runs": [
      // Runs...
    ],
    "properties": {
      // Properties...
    },
    "summary": "Created factorial design with 8 runs and 3 factors"
  },
  "timestamp": "2023-08-15T10:37:00Z"
}
```

##### Task Error

```json
{
  "type": "task_error",
  "task_type": "analysis",
  "status": "error",
  "error": {
    "message": "Analysis failed: missing response values",
    "details": "The following runs are missing response values: 3, 5, 7"
  },
  "timestamp": "2023-08-15T10:45:00Z"
}
```

##### Notification

```json
{
  "type": "notification",
  "notification_type": "info",
  "message": "Analysis will take approximately 2 minutes",
  "details": "Complex model with many factors",
  "timestamp": "2023-08-15T10:40:00Z"
}
```

### Progress Updates

Progress updates are sent by the server during long-running operations such as design generation, analysis, and optimization. The `percent` field indicates the completion percentage (0-100). The `step` field indicates the current stage of the operation.

### Error Handling

If an error occurs during a WebSocket operation, the server sends a `task_error` message with error details. The client should handle these errors appropriately and provide feedback to the user.

## Data Models

### Experiment

```json
{
  "id": "exp-123",
  "name": "Protein Expression Optimization",
  "description": "Factorial design to optimize protein expression in E. coli",
  "experimentType": "factorial",
  "created": "2023-08-15T10:30:00Z",
  "updated": "2023-08-15T10:30:00Z",
  "userId": "user-456",
  "designs": [
    // Design references...
  ]
}
```

### Factor

```json
{
  "name": "Temperature",
  "low": 25,
  "high": 37,
  "units": "°C",
  "description": "Growth temperature",
  "type": "numeric",
  "centerPoint": 31
}
```

### Response

```json
{
  "name": "Protein Yield",
  "units": "mg/L",
  "description": "Total protein yield",
  "goal": "maximize",
  "lowerBound": 0,
  "upperBound": null,
  "target": null,
  "weight": 1
}
```

### Design

```json
{
  "id": "design-789",
  "experimentId": "exp-123",
  "designType": "factorial",
  "factors": [
    // Factors...
  ],
  "responses": [
    // Responses...
  ],
  "runs": [
    {
      "runOrder": 1,
      "stdOrder": 1,
      "Temperature_coded": -1,
      "IPTG_coded": -1,
      "OD600_coded": -1,
      "Temperature_natural": 25,
      "IPTG_natural": 0.1,
      "OD600_natural": 0.6,
      "Protein Yield": 120.5
    },
    // More runs...
  ],
  "properties": {
    "centerPoints": 2,
    "replicates": 1,
    "resolution": "Full",
    "df": 4
  },
  "created": "2023-08-15T10:35:00Z",
  "updated": "2023-08-15T11:00:00Z"
}
```

### Result

```json
{
  "modelSummary": {
    "r_squared": 0.92,
    "adj_r_squared": 0.89,
    "rmse": 10.5,
    "press": 456.7
  },
  "coefficients": {
    "intercept": 125.3,
    "Temperature": -42.1,
    "IPTG": 18.7,
    "OD600": 5.2,
    "Temperature:IPTG": -15.3,
    "Temperature^2": -8.9
  },
  "effects": [
    {
      "factor": "Temperature",
      "effect": -84.2,
      "stdError": 12.3,
      "pValue": 0.0012,
      "lowerCI": -108.5,
      "upperCI": -59.9
    },
    // More effects...
  ],
  "anova": {
    "df_model": 5,
    "df_residual": 10,
    "df_total": 15,
    "ss_model": 25362.4,
    "ss_residual": 2104.5,
    "ss_total": 27466.9,
    "ms_model": 5072.48,
    "ms_residual": 210.45,
    "f_value": 24.1,
    "p_value": 0.00003
  }
}
```

## Example Usage

### Creating a New Experiment

```javascript
async function createExperiment() {
  const experimentData = {
    name: 'Protein Expression Optimization',
    description: 'Factorial design to optimize protein expression in E. coli',
    experimentType: 'factorial'
  };
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/doe/experiments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(experimentData)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create experiment: ${response.status}`);
    }
    
    const experiment = await response.json();
    console.log('Created experiment:', experiment);
    return experiment;
  } catch (error) {
    console.error('Error creating experiment:', error);
    throw error;
  }
}
```

### Generating a Design

```javascript
async function generateDesign(experimentId) {
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
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/doe/experiments/${experimentId}/designs/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(designParams)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to generate design: ${response.status}`);
    }
    
    const design = await response.json();
    console.log('Generated design:', design);
    return design;
  } catch (error) {
    console.error('Error generating design:', error);
    throw error;
  }
}
```

### Analyzing Results

```javascript
async function analyzeDesign(designId) {
  const analysisParams = {
    responseVar: 'Protein Yield',
    modelType: 'quadratic',
    selectedFactors: ['Temperature', 'IPTG', 'OD600'],
    confidenceLevel: 0.95
  };
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/doe/designs/${designId}/analyze/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(analysisParams)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to analyze design: ${response.status}`);
    }
    
    const results = await response.json();
    console.log('Analysis results:', results);
    return results;
  } catch (error) {
    console.error('Error analyzing design:', error);
    throw error;
  }
}
```

### Using WebSockets

```javascript
function setupWebSocket(experimentId) {
  const wsUrl = `${WS_BASE_URL}/ws/doe/${experimentId}/`;
  const socket = new WebSocket(wsUrl);
  
  socket.onopen = () => {
    console.log('WebSocket connected');
    
    // Request status updates
    socket.send(JSON.stringify({
      type: 'request_status',
      tasks: ['design_generation', 'analysis', 'optimization']
    }));
  };
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Received WebSocket message:', data);
      
      switch (data.type) {
        case 'progress_update':
          updateProgressUI(data);
          break;
        case 'task_complete':
          handleTaskComplete(data);
          break;
        case 'task_error':
          handleTaskError(data);
          break;
        case 'notification':
          showNotification(data);
          break;
        default:
          console.log('Unhandled WebSocket message type:', data.type);
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
    }
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  socket.onclose = (event) => {
    console.log('WebSocket closed:', event.code, event.reason);
  };
  
  // Function to send design generation request
  function requestDesignGeneration(designParams) {
    socket.send(JSON.stringify({
      type: 'generate_design',
      data: designParams
    }));
  }
  
  // Function to send analysis request
  function requestAnalysis(analysisParams) {
    socket.send(JSON.stringify({
      type: 'request_analysis',
      data: analysisParams
    }));
  }
  
  return {
    socket,
    requestDesignGeneration,
    requestAnalysis
  };
}
```

## Error Codes

- `401` - Unauthorized: Authentication required
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource not found
- `400` - Bad Request: Invalid request data
- `422` - Unprocessable Entity: Request data validation failed
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: Service temporarily unavailable

## Rate Limits

- **Standard Users**: 
  - 100 requests per minute
  - 5 concurrent operations
- **Premium Users**: 
  - 500 requests per minute
  - 20 concurrent operations

Rate limit headers are included in API responses:
- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining requests in the current window
- `X-RateLimit-Reset`: Time (in seconds) until the rate limit resets