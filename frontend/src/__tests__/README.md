# Testing Guide for StickForStats Frontend

## Overview
This directory contains all test files for the StickForStats frontend. We use Jest as our test runner and React Testing Library for testing React components.

## Directory Structure
```
__tests__/
  ├── api/                  # Tests for API integration
  ├── components/           # Tests for React components
  │   ├── confidence_intervals/
  │   ├── probability_distributions/
  │   ├── pca/
  │   ├── sqc/
  │   └── ...
  ├── hooks/               # Tests for custom hooks
  ├── setup/               # Test setup files
  │   ├── fileMock.js      # Mock for file imports
  │   ├── setupTests.js    # Jest setup file
  │   └── styleMock.js     # Mock for style imports
  └── README.md            # This file
```

## Running Tests
You can run tests using the provided scripts in `package.json`:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

Alternatively, use the `run_tests.sh` script:

```bash
# Run all tests
./run_tests.sh

# Run tests in watch mode
./run_tests.sh watch

# Run tests with coverage
./run_tests.sh coverage

# Run tests for a specific module
./run_tests.sh probability
```

## Writing Tests

### Component Tests
For React components, we use React Testing Library. Here's a basic template:

```jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import YourComponent from '../../../components/path/to/YourComponent';

describe('YourComponent', () => {
  test('renders correctly', () => {
    render(<YourComponent />);
    expect(screen.getByText(/expected text/i)).toBeInTheDocument();
  });

  test('handles user interaction', () => {
    render(<YourComponent />);
    fireEvent.click(screen.getByRole('button', { name: /click me/i }));
    expect(screen.getByText(/clicked/i)).toBeInTheDocument();
  });
});
```

### API Tests
For API integration tests, we mock Axios responses:

```jsx
import axios from 'axios';
import { yourApiFunction } from '../../api/yourApiModule';

jest.mock('axios');

describe('API Integration', () => {
  test('makes the correct API call', async () => {
    const mockData = { result: 'success' };
    axios.get.mockResolvedValue({ data: mockData });
    
    const result = await yourApiFunction();
    
    expect(axios.get).toHaveBeenCalledWith('/expected/endpoint');
    expect(result).toEqual(mockData);
  });
});
```

## Mocking Dependencies
Common dependencies are mocked in `setupTests.js`:

- MathJax (for mathematical formulas)
- Chart.js (for visualizations)
- Axios (for API calls)

For component-specific mocks, define them in your test file:

```jsx
jest.mock('../../components/SomeComponent', () => {
  return {
    __esModule: true,
    default: () => <div data-testid="mocked-component">Mocked Content</div>
  };
});
```

## Best Practices

1. **Test behavior, not implementation** - Focus on what the component does, not how it's built.
2. **Use semantic queries** - Prefer `getByRole`, `getByLabelText`, etc., over `getByTestId`.
3. **Test essential functions** - You don't need to test every line of code, focus on critical paths.
4. **Use explicit assertions** - Make your test expectations clear and specific.
5. **Keep tests independent** - Each test should run in isolation without depending on other tests.
6. **Mock external dependencies** - Use Jest mocks for API calls, complex libraries, etc.
7. **Use setup and cleanup** - Use `beforeEach`, `afterEach` for common setup/teardown.

## Coverage Goals
We aim for at least 70% test coverage across all modules, with higher coverage for critical components like data processing and visualization.