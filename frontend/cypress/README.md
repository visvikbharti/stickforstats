# End-to-End Testing with Cypress

This directory contains end-to-end tests for the StickForStats platform using Cypress. These tests verify that the entire application functions correctly from a user's perspective, testing multiple modules and their integration.

## Test Structure

The tests are organized by module and functionality:

- `authentication.cy.js` - Tests user authentication (login, logout)
- `dataset-management.cy.js` - Tests dataset upload, management, and deletion
- `sqc-analysis.cy.js` - Tests SQC Analysis module functionality
- `probability-distributions.cy.js` - Tests Probability Distributions module functionality
- `cross-module-integration.cy.js` - Tests cross-module workflows and integration

## Running Tests

### Prerequisites

1. Ensure the backend server is running at http://localhost:8000
2. Ensure the frontend development server is running at http://localhost:3000
3. Make sure test users exist in the database (see fixtures/users.json)

### Running Tests in the Cypress UI

To open Cypress in interactive mode:

```bash
cd frontend
npm run cy:open
```

This opens the Cypress Test Runner, where you can select and run individual tests.

### Running Tests Headlessly

To run all tests in headless mode:

```bash
cd frontend
npm run cy:run
```

To run a specific test file:

```bash
cd frontend
npx cypress run --spec "cypress/e2e/authentication.cy.js"
```

### Running with the Frontend Dev Server

To start the frontend server and run Cypress tests in one command:

```bash
cd frontend
npm run test:e2e
```

## Test Data

- Test data is stored in the `fixtures` directory
- `test_data.csv` - Sample dataset for testing
- `users.json` - Test user credentials

## Additional Notes

1. The tests use custom commands defined in `support/commands.js`:
   - `cy.login()` - Logs in a user via the API directly
   - `cy.uploadFile()` - Handles file uploads in tests
   - `cy.exists()` - Checks if an element exists without failing

2. Tests assume the following:
   - The backend is configured with proper test data
   - Test users are available in the system
   - API endpoints match those defined in the test configuration

## Troubleshooting

If tests fail, check the following:

1. Ensure both backend and frontend servers are running
2. Verify test users exist in the database
3. Check network requests in the Cypress logs for API errors
4. Verify that selectors (data-testid attributes) match those in the application
5. Increase timeouts for operations that may take longer (like analysis computations)

## Adding New Tests

When adding new tests:

1. Follow the existing patterns for page structure and test organization
2. Use data-testid attributes for element selection to ensure resilience
3. Mock network requests where appropriate using Cypress interceptors
4. Use the custom commands to simplify common operations
5. Group related tests in describe blocks
6. Keep tests independent of each other