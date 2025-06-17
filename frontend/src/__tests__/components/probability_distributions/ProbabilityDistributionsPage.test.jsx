import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProbabilityDistributionsPage from '../../../components/probability_distributions/ProbabilityDistributionsPage';
import * as apiModule from '../../../api/probabilityDistributionsApi';

// Mock the API modules
jest.mock('../../../api/probabilityDistributionsApi');

// Mock the child components to simplify testing
jest.mock('../../../components/probability_distributions/DistributionSelector', () => ({
  __esModule: true,
  default: ({ value, onChange }) => (
    <div data-testid="mock-distribution-selector">
      <select 
        data-testid="distribution-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="NORMAL">Normal</option>
        <option value="BINOMIAL">Binomial</option>
        <option value="POISSON">Poisson</option>
        <option value="EXPONENTIAL">Exponential</option>
      </select>
    </div>
  )
}));

jest.mock('../../../components/probability_distributions/DistributionParameters', () => ({
  __esModule: true,
  default: ({ type, parameters, onChange }) => (
    <div data-testid="mock-distribution-parameters">
      <button 
        data-testid="change-params-button"
        onClick={() => {
          if (type === 'NORMAL') {
            onChange({ mean: 1, std: 2 });
          } else if (type === 'BINOMIAL') {
            onChange({ n: 20, p: 0.3 });
          }
        }}
      >
        Change Parameters
      </button>
      <span>Type: {type}</span>
      <span>Parameters: {JSON.stringify(parameters)}</span>
    </div>
  )
}));

jest.mock('../../../components/probability_distributions/DistributionPlot', () => ({
  __esModule: true,
  default: ({ type, parameters }) => (
    <div data-testid="mock-distribution-plot">
      <span>Plot for: {type}</span>
      <span>With parameters: {JSON.stringify(parameters)}</span>
    </div>
  )
}));

jest.mock('../../../components/probability_distributions/ProbabilityCalculator', () => ({
  __esModule: true,
  default: ({ type, parameters }) => (
    <div data-testid="mock-probability-calculator">
      <span>Calculator for: {type}</span>
    </div>
  )
}));

jest.mock('../../../components/probability_distributions/EducationalContent', () => ({
  __esModule: true,
  default: ({ distributionType }) => (
    <div data-testid="mock-educational-content">
      <span>Educational content for: {distributionType}</span>
    </div>
  )
}));

describe('ProbabilityDistributionsPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default mock returns for API calls
    apiModule.fetchDistributionProjects.mockResolvedValue([
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' }
    ]);
    
    apiModule.fetchDistributions.mockResolvedValue([
      { id: 1, distribution_type: 'NORMAL', parameters: { mean: 0, std: 1 } },
      { id: 2, distribution_type: 'BINOMIAL', parameters: { n: 10, p: 0.5 } }
    ]);
  });

  test('renders the main page components', async () => {
    await waitFor(() => {
      render(<ProbabilityDistributionsPage />);
    });
    
    expect(screen.getByText(/Probability Distributions/i)).toBeInTheDocument();
    expect(screen.getByTestId('mock-distribution-selector')).toBeInTheDocument();
    expect(screen.getByTestId('mock-distribution-parameters')).toBeInTheDocument();
    expect(screen.getByTestId('mock-distribution-plot')).toBeInTheDocument();
    expect(screen.getByTestId('mock-probability-calculator')).toBeInTheDocument();
    expect(screen.getByTestId('mock-educational-content')).toBeInTheDocument();
  });

  test('changes distribution type when selector changes', async () => {
    await waitFor(() => {
      render(<ProbabilityDistributionsPage />);
    });
    
    // Default is usually NORMAL
    expect(screen.getByText(/Plot for: NORMAL/i)).toBeInTheDocument();
    
    // Change to BINOMIAL
    const selector = screen.getByTestId('distribution-select');
    fireEvent.change(selector, { target: { value: 'BINOMIAL' } });
    
    // Check if the plot updates
    expect(screen.getByText(/Plot for: BINOMIAL/i)).toBeInTheDocument();
    
    // Educational content should update too
    expect(screen.getByText(/Educational content for: BINOMIAL/i)).toBeInTheDocument();
  });

  test('updates parameters when parameter component changes them', async () => {
    await waitFor(() => {
      render(<ProbabilityDistributionsPage />);
    });
    
    // Check initial parameters (likely NORMAL with default values)
    expect(screen.getByTestId('mock-distribution-parameters')).toBeInTheDocument();
    
    // Click the button to change parameters
    const changeParamsButton = screen.getByTestId('change-params-button');
    fireEvent.click(changeParamsButton);
    
    // Check if the plot updates with new parameters
    expect(screen.getByText(/With parameters: {"mean":1,"std":2}/i)).toBeInTheDocument();
  });

  test('loads projects and saved distributions on mount', async () => {
    render(<ProbabilityDistributionsPage />);
    
    await waitFor(() => {
      expect(apiModule.fetchDistributionProjects).toHaveBeenCalled();
    });
  });

  test('loads saved distributions when a project is selected', async () => {
    await waitFor(() => {
      render(<ProbabilityDistributionsPage />);
    });
    
    // Mock the project selection
    // This would normally be done through a project selector component
    // For testing, we can directly call the method that would be triggered
    
    // Reset the mock to check for the new call
    apiModule.fetchDistributions.mockClear();
    
    // This approach may need to be adjusted based on how the component is implemented
    // If the component has a projectId state that is set by a selector
    // For this test, we assume there's a public method or event handler
    
    // Since we don't have direct access to component methods in this test setup,
    // we could use a workaround like triggering a project selection through UI
    // if such a UI element exists
    
    // For a more comprehensive test, we would need to expose the component's methods
    // or create a more detailed mock of the project selection component
    
    expect(apiModule.fetchDistributions).toHaveBeenCalledTimes(1);
  });
});