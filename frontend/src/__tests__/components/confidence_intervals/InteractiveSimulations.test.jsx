import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import InteractiveSimulations from '../../../components/confidence_intervals/simulations/InteractiveSimulations';
import { MathJaxContext } from 'better-react-mathjax';

// Mock child components
jest.mock('../../../components/confidence_intervals/simulations/CoverageSimulation', () => ({
  __esModule: true,
  default: ({ projectId }) => <div data-testid="mock-coverage-simulation">Coverage Simulation (Project ID: {projectId})</div>
}));

jest.mock('../../../components/confidence_intervals/simulations/SampleSizeSimulation', () => ({
  __esModule: true,
  default: ({ projectId }) => <div data-testid="mock-sample-size-simulation">Sample Size Simulation (Project ID: {projectId})</div>
}));

jest.mock('../../../components/confidence_intervals/simulations/BootstrapSimulation', () => ({
  __esModule: true,
  default: ({ projectId }) => <div data-testid="mock-bootstrap-simulation">Bootstrap Simulation (Project ID: {projectId})</div>
}));

jest.mock('../../../components/confidence_intervals/simulations/TransformationSimulation', () => ({
  __esModule: true,
  default: ({ projectId }) => <div data-testid="mock-transformation-simulation">Transformation Simulation (Project ID: {projectId})</div>
}));

jest.mock('../../../components/confidence_intervals/simulations/NonNormalitySimulation', () => ({
  __esModule: true,
  default: ({ projectId }) => <div data-testid="mock-non-normality-simulation">Non-normality Simulation (Project ID: {projectId})</div>
}));

// Mock axios
jest.mock('axios');

describe('InteractiveSimulations Component', () => {
  const mockProjects = [
    { id: 'project-1', name: 'Test Project 1' },
    { id: 'project-2', name: 'Test Project 2' }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default axios mock behavior
    axios.post.mockResolvedValue({
      data: {
        id: 'new-project-id',
        name: 'New Test Project',
        description: 'Project for confidence interval simulations',
        settings: { default_confidence_level: 0.95 }
      }
    });
  });
  
  const renderComponent = (props = {}) => {
    return render(
      <MathJaxContext>
        <InteractiveSimulations {...props} />
      </MathJaxContext>
    );
  };
  
  test('renders the component title and description', () => {
    renderComponent();
    
    expect(screen.getByText(/Interactive Simulations/i)).toBeInTheDocument();
    expect(screen.getByText(/These simulations allow you to explore/i)).toBeInTheDocument();
  });
  
  test('renders all simulation tabs', () => {
    renderComponent();
    
    expect(screen.getByText(/Coverage Properties/i)).toBeInTheDocument();
    expect(screen.getByText(/Sample Size Effects/i)).toBeInTheDocument();
    expect(screen.getByText(/Bootstrap Methods/i)).toBeInTheDocument();
    expect(screen.getByText(/Transformations/i)).toBeInTheDocument();
    expect(screen.getByText(/Non-normality Impact/i)).toBeInTheDocument();
  });
  
  test('shows message when no projects are available', () => {
    renderComponent({ projects: [] });
    
    expect(screen.getByText(/You don't have any projects yet/i)).toBeInTheDocument();
    expect(screen.getByText(/Please select or create a project/i)).toBeInTheDocument();
  });
  
  test('allows project selection when projects are available', () => {
    renderComponent({ projects: mockProjects });
    
    // Check if project select dropdown exists
    expect(screen.getByLabelText(/Select Project/i)).toBeInTheDocument();
    
    // Check if project items are in dropdown
    const projectSelect = screen.getByLabelText(/Select Project/i);
    expect(projectSelect).toBeInTheDocument();
    
    // Check if the first project is selected by default (useEffect behavior)
    expect(screen.getByText(/Coverage Simulation \(Project ID: project-1\)/i)).toBeInTheDocument();
    
    // Change selected project
    fireEvent.change(projectSelect, { target: { value: 'project-2' } });
    
    // Check if the simulation shows the new project ID
    expect(screen.getByText(/Coverage Simulation \(Project ID: project-2\)/i)).toBeInTheDocument();
  });
  
  test('creates a new project when button is clicked', async () => {
    renderComponent({ projects: mockProjects });
    
    // Click the create project button
    fireEvent.click(screen.getByText(/Create New Project/i));
    
    // Check if the API was called with the correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        '/api/confidence-intervals/projects/',
        expect.objectContaining({
          name: expect.stringContaining('Confidence Interval Simulations'),
          description: 'Project for confidence interval simulations',
          settings: { default_confidence_level: 0.95 }
        })
      );
    });
    
    // Check if the new project is used
    expect(screen.getByText(/Coverage Simulation \(Project ID: new-project-id\)/i)).toBeInTheDocument();
  });
  
  test('handles errors when creating a project', async () => {
    // Setup axios to return an error
    const errorMessage = 'API error';
    axios.post.mockRejectedValueOnce(new Error(errorMessage));
    
    renderComponent({ projects: mockProjects });
    
    // Click the create project button
    fireEvent.click(screen.getByText(/Create New Project/i));
    
    // Check if error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Failed to create a new project/i)).toBeInTheDocument();
    });
  });
  
  test('changes simulation when tabs are clicked', () => {
    renderComponent({ projects: mockProjects });
    
    // Default first tab (Coverage Properties) should be active
    expect(screen.getByText(/Coverage Simulation \(Project ID: project-1\)/i)).toBeInTheDocument();
    
    // Educational context for Coverage Properties should be visible
    expect(screen.getByText(/About Coverage Properties/i)).toBeInTheDocument();
    expect(screen.getByText(/Coverage Properties is one of the most important characteristics/i)).toBeInTheDocument();
    
    // Click the Sample Size Effects tab
    fireEvent.click(screen.getByText(/Sample Size Effects/i));
    
    // Sample Size simulation should now be visible
    expect(screen.getByText(/Sample Size Simulation \(Project ID: project-1\)/i)).toBeInTheDocument();
    
    // Educational context should be updated
    expect(screen.getByText(/About Sample Size Effects/i)).toBeInTheDocument();
    expect(screen.getByText(/Sample Size Effects demonstrate how the width/i)).toBeInTheDocument();
    
    // Click the Bootstrap Methods tab
    fireEvent.click(screen.getByText(/Bootstrap Methods/i));
    
    // Bootstrap simulation should now be visible
    expect(screen.getByText(/Bootstrap Simulation \(Project ID: project-1\)/i)).toBeInTheDocument();
    
    // Educational context should be updated
    expect(screen.getByText(/About Bootstrap Methods/i)).toBeInTheDocument();
    expect(screen.getByText(/Bootstrap Methods allow you to construct confidence intervals/i)).toBeInTheDocument();
    
    // Click the Transformations tab
    fireEvent.click(screen.getByText(/Transformations/i));
    
    // Transformation simulation should now be visible
    expect(screen.getByText(/Transformation Simulation \(Project ID: project-1\)/i)).toBeInTheDocument();
    
    // Educational context should be updated
    expect(screen.getByText(/About Transformations/i)).toBeInTheDocument();
    expect(screen.getByText(/Transformations can be used to construct confidence intervals/i)).toBeInTheDocument();
    
    // Click the Non-normality Impact tab
    fireEvent.click(screen.getByText(/Non-normality Impact/i));
    
    // Non-normality simulation should now be visible
    expect(screen.getByText(/Non-normality Simulation \(Project ID: project-1\)/i)).toBeInTheDocument();
    
    // Educational context should be updated
    expect(screen.getByText(/About Non-normality Impact/i)).toBeInTheDocument();
    expect(screen.getByText(/Non-normality Impact explores how departures from normality/i)).toBeInTheDocument();
  });
});