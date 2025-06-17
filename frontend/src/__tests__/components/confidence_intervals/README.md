# Confidence Intervals Module Test Suite

This directory contains the test suite for the Confidence Intervals module, covering all major components of both the user interface and core functionality.

## Test Structure

The test suite follows a component-based approach, with each React component having a corresponding test file. Tests are written using Jest and React Testing Library, focusing on both component rendering and interactive behavior.

### Main Components Tested

1. **Main Page**
   - `ConfidenceIntervalsPage.test.jsx`: Tests the main container component, tab navigation, and route handling.

2. **Simulation Components**
   - `CoverageSimulation.test.jsx`: Tests the coverage properties simulation component.
   - `SampleSizeSimulation.test.jsx`: Tests the sample size effects simulation component.
   - `BootstrapSimulation.test.jsx`: Tests the bootstrap methods simulation component.
   - `InteractiveSimulations.test.jsx`: Tests the container for all simulation components.

3. **Educational Components**
   - `TheoryFoundations.test.jsx`: Tests the theoretical foundations educational component.

4. **Calculator Components**
   - `CalculatorDashboard.test.jsx`: Tests the calculator dashboard and result management.

## Test Features

The test suite includes testing for several key features:

1. **Component Rendering**: Verifies that all components render correctly with their expected UI elements.

2. **User Interaction**: Tests user interactions like form submissions, tab switching, and button clicks.

3. **API Integration**: Tests API calls using mocked axios responses for data fetching and posting.

4. **WebSocket Communication**: Tests real-time communication using mocked WebSocket connections for simulations.

5. **MathJax Integration**: Tests rendering of mathematical formulas using MathJax.

6. **Route Navigation**: Tests navigation between different sections of the module.

7. **Error Handling**: Tests how components handle error states and display error messages.

## Running the Tests

Tests can be run using the provided `run_tests.sh` script in the `frontend` directory:

```bash
# Run all tests
./run_tests.sh

# Run only confidence intervals tests
./run_tests.sh confidence

# Run only simulation component tests
./run_tests.sh simulations

# Run only calculator component tests
./run_tests.sh calculators

# Run only educational component tests
./run_tests.sh education

# Run tests with coverage information
./run_tests.sh coverage

# Run tests in watch mode for development
./run_tests.sh watch
```

## Test Mocks

Several dependencies are mocked to isolate the components during testing:

1. **Axios**: API calls are mocked to return predefined responses.
2. **WebSocket**: WebSocket connections are mocked for testing real-time simulations.
3. **React Router**: Navigation functions and hooks are mocked for testing routing behavior.
4. **MathJax**: MathJax rendering is mocked to test components that display mathematical formulas.
5. **Chart Libraries**: Recharts and related visualization libraries are mocked to test chart components.

## Coverage Targets

The jest configuration sets a target of 70% coverage for:
- Statements
- Branches
- Functions
- Lines

## Future Improvements

Future improvements to the test suite could include:

1. End-to-end tests using Cypress or Playwright to test full user flows.
2. More comprehensive testing of edge cases, especially for data validation.
3. Performance testing for simulation components with large datasets.
4. Visual regression testing for chart and visualization components.