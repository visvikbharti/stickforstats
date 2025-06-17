import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { MemoryRouter } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';
import CalculatorDashboard from '../../../components/confidence_intervals/calculators/CalculatorDashboard';

// Mock dependencies
jest.mock('axios');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useSearchParams: () => {
    const setSearchParams = jest.fn();
    return [new URLSearchParams({ project: 'project-1' }), setSearchParams];
  }
}));

// Mock child components
jest.mock('../../../components/confidence_intervals/calculators/SampleBasedCalculator', () => ({
  __esModule: true,
  default: ({ project, projectData, onSaveResult }) => (
    <div data-testid="mock-sample-calculator">
      Sample-Based Calculator
      <button onClick={() => onSaveResult({ id: 'new-result-id', interval_type: 'MEAN_T', result: { lower: 10, upper: 20 } })}>
        Save Result
      </button>
      <div>Project ID: {project?.id}</div>
      <div>Project Data: {projectData?.length || 0} items</div>
    </div>
  )
}));

jest.mock('../../../components/confidence_intervals/calculators/ParameterBasedCalculator', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-parameter-calculator">Parameter-Based Calculator</div>
}));

jest.mock('../../../components/confidence_intervals/calculators/BootstrapCalculator', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-bootstrap-calculator">Bootstrap Calculator</div>
}));

jest.mock('../../../components/confidence_intervals/calculators/BayesianCalculator', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-bayesian-calculator">Bayesian Calculator</div>
}));

jest.mock('../../../components/confidence_intervals/calculators/DifferenceCalculator', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-difference-calculator">Difference Calculator</div>
}));

jest.mock('../../../components/confidence_intervals/visualizations/IntervalVisualization', () => ({
  __esModule: true,
  default: ({ result }) => (
    <div data-testid="mock-interval-visualization">
      Visualization for {result.interval_type}
      <div>Lower: {result.result.lower}</div>
      <div>Upper: {result.result.upper}</div>
    </div>
  )
}));

describe('CalculatorDashboard Component', () => {
  const mockProjects = [
    { id: 'project-1', name: 'Test Project 1', description: 'First test project' },
    { id: 'project-2', name: 'Test Project 2', description: 'Second test project' }
  ];
  
  const mockProjectData = [
    { id: 'data-1', name: 'Sample Dataset 1', data_type: 'NUMERIC' },
    { id: 'data-2', name: 'Binary Dataset', data_type: 'CATEGORICAL' }
  ];
  
  const mockResults = [
    {
      id: 'result-1',
      interval_type: 'MEAN_T',
      result: {
        confidence_level: 0.95,
        mean: 25,
        lower: 20,
        upper: 30
      }
    },
    {
      id: 'result-2',
      interval_type: 'PROPORTION_WILSON',
      result: {
        confidence_level: 0.99,
        proportion: 0.7,
        lower: 0.65,
        upper: 0.75
      }
    }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/confidence-intervals/data/')) {
        return Promise.resolve({ data: mockProjectData });
      }
      if (url.includes('/api/confidence-intervals/results/')) {
        return Promise.resolve({ data: mockResults });
      }
      return Promise.resolve({ data: [] });
    });
    
    axios.post.mockResolvedValue({ data: { id: 'new-result' } });
    axios.delete.mockResolvedValue({ data: {} });
  });
  
  const renderComponent = (props = {}) => {
    return render(
      <MemoryRouter>
        <SnackbarProvider>
          <CalculatorDashboard
            projects={mockProjects}
            {...props}
          />
        </SnackbarProvider>
      </MemoryRouter>
    );
  };
  
  test('renders the dashboard title and description', () => {
    renderComponent();
    
    expect(screen.getByText(/Confidence Interval Calculators/i)).toBeInTheDocument();
    expect(screen.getByText(/Use these calculators to compute confidence intervals/i)).toBeInTheDocument();
  });
  
  test('renders project selection dropdown with projects', () => {
    renderComponent();
    
    const projectSelect = screen.getByLabelText(/Project/i);
    expect(projectSelect).toBeInTheDocument();
    
    // First project should be selected by default (from URL param)
    expect(projectSelect.value).toBe('project-1');
    expect(screen.getByText(/First test project/i)).toBeInTheDocument();
  });
  
  test('fetches project data and results when project is selected', async () => {
    renderComponent();
    
    // Wait for API calls to complete
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/confidence-intervals/data/?project=project-1');
      expect(axios.get).toHaveBeenCalledWith('/api/confidence-intervals/results/?project=project-1');
    });
    
    // Check that project data was passed to the calculator
    expect(screen.getByText(/Project Data: 2 items/i)).toBeInTheDocument();
    
    // Check that results are displayed
    expect(screen.getByText(/Visualization for MEAN_T/i)).toBeInTheDocument();
    expect(screen.getByText(/Upper: 30/i)).toBeInTheDocument();
  });
  
  test('changes calculator type when tabs are clicked', async () => {
    renderComponent();
    
    // Default is Sample-Based Calculator
    expect(screen.getByTestId('mock-sample-calculator')).toBeInTheDocument();
    
    // Click on Parameter-Based Calculator tab
    fireEvent.click(screen.getByText(/Parameter-Based/i));
    expect(screen.getByTestId('mock-parameter-calculator')).toBeInTheDocument();
    
    // Click on Bootstrap Calculator tab
    fireEvent.click(screen.getByText(/Bootstrap/i));
    expect(screen.getByTestId('mock-bootstrap-calculator')).toBeInTheDocument();
    
    // Click on Bayesian Calculator tab
    fireEvent.click(screen.getByText(/Bayesian/i));
    expect(screen.getByTestId('mock-bayesian-calculator')).toBeInTheDocument();
    
    // Click on Differences Calculator tab
    fireEvent.click(screen.getByText(/Differences/i));
    expect(screen.getByTestId('mock-difference-calculator')).toBeInTheDocument();
  });
  
  test('changes project and updates data when project selection changes', async () => {
    renderComponent();
    
    // Change to second project
    fireEvent.change(screen.getByLabelText(/Project/i), { target: { value: 'project-2' } });
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/confidence-intervals/data/?project=project-2');
      expect(axios.get).toHaveBeenCalledWith('/api/confidence-intervals/results/?project=project-2');
    });
    
    // Project description should update
    expect(screen.getByText(/Second test project/i)).toBeInTheDocument();
  });
  
  test('adds new result when calculator saves a result', async () => {
    renderComponent();
    
    // Wait for initial data load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
    
    // Trigger save result from mock calculator
    fireEvent.click(screen.getByText(/Save Result/i));
    
    // Check that the new result is added to the list
    expect(screen.getByText(/Visualization for MEAN_T/i)).toBeInTheDocument();
  });
  
  test('removes result when Remove button is clicked', async () => {
    renderComponent();
    
    // Wait for initial data load
    await waitFor(() => {
      expect(screen.getAllByText(/Remove/i).length).toBeGreaterThan(0);
    });
    
    // Click the first Remove button
    fireEvent.click(screen.getAllByText(/Remove/i)[0]);
    
    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith('/api/confidence-intervals/results/result-1/');
    });
  });
  
  test('handles API errors gracefully', async () => {
    // Mock API error
    axios.get.mockRejectedValueOnce(new Error('API error'));
    
    renderComponent();
    
    // Wait for API call to fail
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalled();
    });
    
    // Component should still render without crashing
    expect(screen.getByText(/Confidence Interval Calculators/i)).toBeInTheDocument();
  });
  
  test('shows message when no projects are available', () => {
    renderComponent({ projects: [] });
    
    expect(screen.getByLabelText(/Project/i)).toBeDisabled();
    expect(screen.getByText(/Please select or create a project to start calculations/i)).toBeInTheDocument();
  });
});