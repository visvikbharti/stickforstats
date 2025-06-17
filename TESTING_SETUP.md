# StickForStats Testing Setup

This document provides a quick overview of how to run the various tests that have been set up for the StickForStats migration project.

## Backend Tests

Backend tests are implemented using Django's test framework and pytest. They test the functionality of Django services, models, and API endpoints.

### Running Backend Tests

To run all backend tests:

```bash
# Navigate to the project root
cd /path/to/new_project

# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test stickforstats.mainapp

# Run a specific test file
python manage.py test stickforstats.mainapp.tests.test_report_generator_service

# Run with pytest (for more detailed reporting)
pytest stickforstats/
```

### Backend Test Coverage

To generate a coverage report:

```bash
coverage run --source='stickforstats' manage.py test
coverage report
coverage html  # Generates an HTML report in htmlcov/
```

## Frontend Tests

Frontend tests are implemented using Jest and React Testing Library. They test React components, hooks, and utilities.

### Running Frontend Tests

To run all frontend tests:

```bash
# Navigate to the frontend directory
cd /path/to/new_project/frontend

# Run all tests
npm test

# Run tests in watch mode (for development)
npm run test:watch

# Run with coverage
npm run test:coverage
```

## End-to-End Tests

End-to-end tests are implemented using Cypress. They test the complete user flows across the frontend and backend.

### Running E2E Tests

To run Cypress tests:

```bash
# Navigate to the project root
cd /path/to/new_project

# Open Cypress in interactive mode
cd frontend
npm run cy:open

# Run tests headlessly
npm run cy:run

# Run with both frontend and backend servers started automatically
npm run test:e2e
```

## Testing Workflow Components

The workflow management UI has unit tests for its components and end-to-end tests for user flows.

### Workflow Component Tests

- `WorkflowList.test.jsx`: Tests the workflow listing component
- `WorkflowDetail.test.jsx`: Tests the workflow detail view
- `WorkflowStepForm.test.jsx`: Tests the step form component
- `WorkflowExecution.test.jsx`: Tests the execution monitoring component

### Workflow E2E Tests

- `workflow.cy.js`: Tests complete workflow management flows including:
  - Listing workflows
  - Creating new workflows
  - Adding steps
  - Executing workflows
  - Filtering and searching

## Testing Report Generation Components

The report generation UI has unit tests for its components and end-to-end tests for user flows.

### Report Component Tests

- `ReportList.test.jsx`: Tests the report listing component
- `ReportGenerator.test.jsx`: Tests the report generation form
- `ReportViewer.test.jsx`: Tests the report viewing component

### Report E2E Tests

- `reports.cy.js`: Tests complete report generation flows including:
  - Listing reports
  - Generating new reports
  - Viewing report details
  - Downloading reports
  - Filtering and searching

## CI/CD Integration

The test suite is ready to be integrated with CI/CD pipelines. Sample GitHub Actions workflow files have been added to the repository.

### GitHub Actions Workflow

- `.github/workflows/tests.yml`: Runs backend and frontend tests on each push and pull request
- `.github/workflows/e2e.yml`: Runs end-to-end tests on scheduled intervals

## Test Data

Test fixtures are provided for:

- Sample users
- Sample workflows and steps
- Sample reports and analyses

These fixtures are automatically loaded during test setup.

## Next Steps

1. Increase test coverage for backend services
2. Add more comprehensive component tests for frontend
3. Expand end-to-end test scenarios
4. Implement visual regression testing