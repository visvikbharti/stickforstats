# StickForStats MainApp API Documentation

This document provides information about the API endpoints available in the StickForStats MainApp module, focusing on the core statistical analysis, reporting, and workflow management functionality.

## Authentication

All API endpoints require authentication. Authentication is handled via Django's authentication system. Include an authentication token in the request header:

```
Authorization: Token <your-token>
```

## Base URL

All API paths are relative to: `/api/v1/mainapp/`

## Statistical Analysis Endpoints

### Statistical Tests

```
GET/POST /statistical-tests/
```

Perform various statistical tests on datasets.

#### Request Body

```json
{
  "test_type": "normality|t_test|anova|chi_square|correlation",
  "parameters": {
    // Test-specific parameters
  }
}
```

#### Example: T-Test

```json
{
  "test_type": "t_test",
  "parameters": {
    "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
    "variable": "height",
    "group_variable": "gender",
    "alpha": 0.05,
    "equal_var": true
  }
}
```

### Advanced Analysis

```
GET/POST /advanced-analysis/
```

Perform advanced statistical analyses.

#### Request Body

```json
{
  "analysis_type": "clustering|factor_analysis|time_series",
  "parameters": {
    // Analysis-specific parameters
  }
}
```

### Bayesian Analysis

```
GET/POST /bayesian-analysis/
```

Perform Bayesian statistical analyses.

#### Request Body

```json
{
  "analysis_type": "bayesian_t_test|bayesian_correlation|bayesian_regression|bayesian_anova",
  "parameters": {
    // Analysis-specific parameters
  }
}
```

## Report Generation Endpoints

### Generate Report

```
POST /reports/generate/
```

Generate a report based on analysis results.

#### Request Body

```json
{
  "title": "My Analysis Report",
  "description": "Comprehensive analysis of dataset XYZ",
  "analyses": [
    { /* Analysis result 1 */ },
    { /* Analysis result 2 */ }
  ],
  "format": "pdf",
  "include_visualizations": true,
  "include_raw_data": false
}
```

### List Reports

```
GET /reports/
```

List all reports for the current user.

#### Query Parameters

- `limit` (optional): Maximum number of reports to return (default: 20)

### Get Report Details

```
GET /reports/{report_id}/
```

Get details for a specific report.

#### Query Parameters

- `download` (optional): Set to "true" to download the report file

## Workflow Management Endpoints

### List and Create Workflows

```
GET /workflows/
POST /workflows/
```

List all workflows for the current user or create a new workflow.

#### Query Parameters (GET)

- `include_public` (optional): Include public workflows (default: false)
- `include_templates` (optional): Include template workflows (default: false)
- `status` (optional): Filter by workflow status

#### Request Body (POST)

```json
{
  "name": "My Workflow",
  "description": "Analysis workflow for project XYZ",
  "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
  "metadata": {
    "project": "Project XYZ",
    "tags": ["regression", "quality-control"]
  },
  "is_template": false,
  "is_public": false
}
```

### Workflow Details

```
GET /workflows/{id}/
PUT /workflows/{id}/
DELETE /workflows/{id}/
```

Retrieve, update, or delete a specific workflow.

#### Request Body (PUT)

```json
{
  "name": "Updated Workflow Name",
  "description": "Updated description",
  "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
  "metadata": {
    "project": "Project XYZ",
    "tags": ["regression", "quality-control"]
  },
  "is_template": false,
  "is_public": false,
  "status": "active"
}
```

### Workflow Steps

```
GET /workflows/{workflow_id}/steps/
POST /workflows/{workflow_id}/steps/
```

List all steps for a workflow or add a new step.

#### Request Body (POST)

```json
{
  "name": "Data Preprocessing",
  "description": "Clean and prepare data for analysis",
  "step_type": "data_preprocessing",
  "order": 1,
  "configuration": {
    "processing_type": "clean",
    "cleaning_options": {
      "handle_missing": true,
      "handle_outliers": true,
      "remove_duplicates": true
    }
  },
  "is_required": true,
  "timeout_seconds": 3600,
  "depends_on_ids": []
}
```

### Workflow Step Details

```
GET /workflows/{workflow_id}/steps/{id}/
PUT /workflows/{workflow_id}/steps/{id}/
DELETE /workflows/{workflow_id}/steps/{id}/
```

Retrieve, update, or delete a specific workflow step.

### Execute Workflow

```
POST /workflows/{workflow_id}/execute/
```

Start workflow execution.

#### Request Body

```json
{
  "execute_from_step": 0
}
```

### Workflow Execution Status

```
GET /workflows/{workflow_id}/execution-status/
DELETE /workflows/{workflow_id}/execution-status/
```

Get the current execution status or cancel the execution.

### Update Step Status

```
PUT /workflows/{workflow_id}/steps/{step_id}/status/
```

Update the status of a workflow step.

#### Request Body

```json
{
  "status": "pending|in_progress|completed|failed|skipped",
  "error_message": "Optional error message if status is failed"
}
```

### Clone Workflow

```
POST /workflows/{workflow_id}/clone/
```

Create a copy of an existing workflow.

#### Request Body

```json
{
  "name": "Copy of My Workflow",
  "include_sessions": false
}
```

### Export Workflow

```
GET /workflows/{workflow_id}/export/
```

Export a workflow to a JSON file.

#### Query Parameters

- `include_data` (optional): Include dataset data in the export (default: false)

### Import Workflow

```
POST /workflows/import/
```

Import a workflow from a JSON file.

#### Request Body (multipart/form-data)

```
file: [JSON file]
import_data: true/false
```

### Execution History

```
GET /workflows/execution-history/
```

Get execution history for the current user's workflows.

#### Query Parameters

- `limit` (optional): Maximum number of history items to return (default: 20)

## Common Response Formats

### Success Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My Workflow",
  ...
}
```

### Error Response

```json
{
  "error": "Error message describing what went wrong"
}
```

## HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully
- `400 Bad Request`: Request is invalid
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Authenticated user doesn't have permission
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Supported Step Types

- `data_loading`: Load data from a source
- `data_preprocessing`: Clean, transform, or prepare data
- `visualization`: Create data visualizations
- `statistical_test`: Perform statistical tests
- `machine_learning`: Train, evaluate, or apply ML models
- `advanced_statistics`: Perform advanced statistical analyses
- `report_generation`: Generate reports
- `time_series`: Analyze time series data
- `bayesian`: Perform Bayesian analyses

## Filtering and Pagination

Most list endpoints support filtering via query parameters and pagination.

### Common Query Parameters

- `limit`: Maximum number of items to return
- `offset`: Offset for pagination

## Notes for Frontend Developers

1. Use the workflow API to create and manage analysis workflows
2. Monitor workflow execution status using the status endpoint
3. For long-running analyses, implement polling or WebSocket connections
4. Use the session and report APIs to retrieve and display analysis results
5. Follow the error responses to handle issues gracefully

## Example: Creating and Executing a Workflow

1. Create a workflow:
   ```
   POST /workflows/
   ```

2. Add steps to the workflow:
   ```
   POST /workflows/{workflow_id}/steps/
   ```

3. Execute the workflow:
   ```
   POST /workflows/{workflow_id}/execute/
   ```

4. Check execution status:
   ```
   GET /workflows/{workflow_id}/execution-status/
   ```

5. Retrieve results:
   ```
   GET /workflows/{workflow_id}/
   ```

6. Generate a report:
   ```
   POST /reports/generate/
   ```