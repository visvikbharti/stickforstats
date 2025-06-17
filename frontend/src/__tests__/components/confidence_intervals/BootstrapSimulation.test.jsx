import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import BootstrapSimulation from '../../../components/confidence_intervals/simulations/BootstrapSimulation';
import { MathJaxContext } from 'better-react-mathjax';

// Mock recharts
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="mock-responsive-container">{children}</div>,
  BarChart: ({ children }) => <div data-testid="mock-bar-chart">{children}</div>,
  LineChart: ({ children }) => <div data-testid="mock-line-chart">{children}</div>,
  ScatterChart: ({ children }) => <div data-testid="mock-scatter-chart">{children}</div>,
  Histogram: ({ children }) => <div data-testid="mock-histogram">{children}</div>,
  Bar: () => <div data-testid="mock-bar">Bar</div>,
  Line: () => <div data-testid="mock-line">Line</div>,
  Scatter: () => <div data-testid="mock-scatter">Scatter</div>,
  XAxis: () => <div data-testid="mock-xaxis">XAxis</div>,
  YAxis: () => <div data-testid="mock-yaxis">YAxis</div>,
  CartesianGrid: () => <div data-testid="mock-cartesian-grid">CartesianGrid</div>,
  Tooltip: () => <div data-testid="mock-tooltip">Tooltip</div>,
  Legend: () => <div data-testid="mock-legend">Legend</div>,
  ReferenceLine: () => <div data-testid="mock-reference-line">ReferenceLine</div>,
}));

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.OPEN;
    this.listeners = {};
    
    // Simulate connection established immediately
    setTimeout(() => {
      if (this.listeners.open) {
        this.listeners.open.forEach(callback => callback());
      }
    }, 0);
  }
  
  addEventListener(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }
  
  removeEventListener(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }
  
  send(data) {
    this.lastSentData = data;
    // Simulate server response on send
    setTimeout(() => {
      this.simulateMessage({ 
        type: 'simulation_update', 
        progress: 15, 
        status: 'running' 
      });
    }, 50);
  }
  
  close() {
    if (this.listeners.close) {
      this.listeners.close.forEach(callback => callback({ code: 1000 }));
    }
  }
  
  simulateMessage(data) {
    if (this.listeners.message) {
      const event = { data: JSON.stringify(data) };
      this.listeners.message.forEach(callback => callback(event));
    }
  }
  
  simulateError(error) {
    if (this.listeners.error) {
      this.listeners.error.forEach(callback => callback(error));
    }
  }
  
  simulateClose(code = 1000) {
    if (this.listeners.close) {
      this.listeners.close.forEach(callback => callback({ code }));
    }
  }
  
  // For legacy event handlers
  set onopen(callback) {
    this.addEventListener('open', callback);
  }
  
  set onmessage(callback) {
    this.addEventListener('message', callback);
  }
  
  set onerror(callback) {
    this.addEventListener('error', callback);
  }
  
  set onclose(callback) {
    this.addEventListener('close', callback);
  }
}

// Mock global WebSocket
global.WebSocket = MockWebSocket;
global.WebSocket.OPEN = 1;
global.WebSocket.CLOSED = 3;

describe('BootstrapSimulation Component', () => {
  const projectId = 'test-project-123';
  let mockWebSocket;
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Reset WebSocket instance
    mockWebSocket = null;
    
    // Mock WebSocket constructor
    global.WebSocket = function(url) {
      mockWebSocket = new MockWebSocket(url);
      return mockWebSocket;
    };
    global.WebSocket.OPEN = 1;
    global.WebSocket.CLOSED = 3;
  });
  
  const renderComponent = (props = {}) => {
    return render(
      <MathJaxContext>
        <BootstrapSimulation projectId={projectId} {...props} />
      </MathJaxContext>
    );
  };
  
  test('renders the basic UI elements', () => {
    renderComponent();
    
    // Check if title and description are rendered
    expect(screen.getByText(/Bootstrap Confidence Intervals/i)).toBeInTheDocument();
    expect(screen.getByText(/Bootstrap methods allow you to construct confidence intervals/i)).toBeInTheDocument();
    
    // Check if form elements are rendered
    expect(screen.getByLabelText(/Parameter of Interest/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Bootstrap Method/i)).toBeInTheDocument();
    expect(screen.getByText(/Confidence Level/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Sample Size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Number of Bootstrap Samples/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Distribution Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Run Simulation/i)).toBeInTheDocument();
    
    // Check if mathematical background section is rendered
    expect(screen.getByText(/Mathematical Background/i)).toBeInTheDocument();
  });
  
  test('establishes WebSocket connection on mount', async () => {
    renderComponent();
    
    await waitFor(() => {
      // Check if WebSocket was initialized with the correct URL
      expect(mockWebSocket).toBeTruthy();
      expect(mockWebSocket.url).toContain(`/ws/confidence_intervals/simulation/${projectId}/`);
    });
  });
  
  test('handles parameter type change', () => {
    renderComponent();
    
    // Get the select element for parameter type
    const parameterTypeSelect = screen.getByLabelText(/Parameter of Interest/i);
    
    // Change value to a different parameter type
    fireEvent.change(parameterTypeSelect, { target: { value: 'MEDIAN' } });
    expect(parameterTypeSelect.value).toBe('MEDIAN');
    
    // Change to another parameter type
    fireEvent.change(parameterTypeSelect, { target: { value: 'SKEWNESS' } });
    expect(parameterTypeSelect.value).toBe('SKEWNESS');
  });
  
  test('handles bootstrap method change', () => {
    renderComponent();
    
    // Get the select element for bootstrap method
    const bootstrapMethodSelect = screen.getByLabelText(/Bootstrap Method/i);
    
    // Change value to a different method
    fireEvent.change(bootstrapMethodSelect, { target: { value: 'BASIC' } });
    expect(bootstrapMethodSelect.value).toBe('BASIC');
    
    // Check that the caption updates
    expect(screen.getByText(/Corrects some bias but may exceed parameter space/i)).toBeInTheDocument();
    
    // Change to another method
    fireEvent.change(bootstrapMethodSelect, { target: { value: 'BCA' } });
    expect(bootstrapMethodSelect.value).toBe('BCA');
    
    // Check that the caption updates
    expect(screen.getByText(/Best coverage for skewed distributions and small samples/i)).toBeInTheDocument();
  });
  
  test('handles distribution type change and shows appropriate parameters', () => {
    renderComponent();
    
    // Get the select element for distribution type
    const distributionTypeSelect = screen.getByLabelText(/Distribution Type/i);
    
    // Check normal distribution parameters (default)
    expect(screen.getByText(/Mean \(μ\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Standard Deviation \(σ\)/i)).toBeInTheDocument();
    
    // Change to different distribution types and check for specific parameters
    
    // T-distribution
    fireEvent.change(distributionTypeSelect, { target: { value: 'T' } });
    expect(screen.getByText(/Degrees of Freedom/i)).toBeInTheDocument();
    
    // Gamma distribution
    fireEvent.change(distributionTypeSelect, { target: { value: 'GAMMA' } });
    expect(screen.getByText(/Shape \(k\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Scale \(θ\)/i)).toBeInTheDocument();
    
    // Mixture distribution
    fireEvent.change(distributionTypeSelect, { target: { value: 'MIXTURE' } });
    expect(screen.getByText(/Weight of Component 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Mean of Component 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Mean of Component 2/i)).toBeInTheDocument();
    
    // User-defined data
    fireEvent.change(distributionTypeSelect, { target: { value: 'USER' } });
    expect(screen.getByText(/Enter comma-separated values/i)).toBeInTheDocument();
    expect(screen.getByText(/Enter at least 5 data points/i)).toBeInTheDocument();
  });
  
  test('validates user-defined data input', () => {
    renderComponent();
    
    // Switch to user-defined data
    const distributionTypeSelect = screen.getByLabelText(/Distribution Type/i);
    fireEvent.change(distributionTypeSelect, { target: { value: 'USER' } });
    
    // Get the input field
    const userDataInput = screen.getByLabelText(/Enter comma-separated values/i);
    
    // Enter invalid data (not enough values)
    fireEvent.change(userDataInput, { target: { value: '1, 2, 3' } });
    
    // Try to run the simulation
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Check for error message
    expect(screen.getByText(/Please provide at least 5 data points/i)).toBeInTheDocument();
    
    // Enter invalid data (non-numeric)
    fireEvent.change(userDataInput, { target: { value: '1, 2, 3, 4, abc, 6' } });
    
    // Try to run the simulation
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Check for error message
    expect(screen.getByText(/Invalid format/i)).toBeInTheDocument();
    
    // Enter valid data
    fireEvent.change(userDataInput, { target: { value: '1.2, 3.4, 5.6, 7.8, 9.0, 2.1, 4.3' } });
    
    // Clear previous errors
    renderComponent();
    fireEvent.change(distributionTypeSelect, { target: { value: 'USER' } });
    fireEvent.change(userDataInput, { target: { value: '1.2, 3.4, 5.6, 7.8, 9.0, 2.1, 4.3' } });
    
    // Try to run the simulation
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // No error should be shown
    expect(screen.queryByText(/Please provide at least 5 data points/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Invalid format/i)).not.toBeInTheDocument();
  });
  
  test('sends correct parameters when running simulation', async () => {
    renderComponent();
    
    // Set up parameters
    fireEvent.change(screen.getByLabelText(/Parameter of Interest/i), { target: { value: 'MEDIAN' } });
    fireEvent.change(screen.getByLabelText(/Bootstrap Method/i), { target: { value: 'PERCENTILE' } });
    fireEvent.change(screen.getByLabelText(/Distribution Type/i), { target: { value: 'NORMAL' } });
    
    // Set sample size and number of bootstraps
    fireEvent.change(screen.getByLabelText(/Sample Size/i), { target: { value: '50' } });
    fireEvent.change(screen.getByLabelText(/Number of Bootstrap Samples/i), { target: { value: '3000' } });
    
    // Click Run Simulation button
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    await waitFor(() => {
      // Check that WebSocket sent the correct data
      const sentData = JSON.parse(mockWebSocket.lastSentData);
      expect(sentData.action).toBe('start_bootstrap_simulation');
      expect(sentData.params.project_id).toBe(projectId);
      expect(sentData.params.parameter_type).toBe('MEDIAN');
      expect(sentData.params.bootstrap_method).toBe('PERCENTILE');
      expect(sentData.params.distribution).toBe('NORMAL');
      expect(sentData.params.sample_size).toBe(50);
      expect(sentData.params.n_bootstraps).toBe(3000);
      expect(sentData.params.dist_params).toEqual(expect.objectContaining({
        mean: expect.any(Number),
        std: expect.any(Number)
      }));
    });
  });
  
  test('displays results when simulation completes', async () => {
    renderComponent();
    
    // Click Run Simulation button to start
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Simulate simulation completion with results
    const mockResults = {
      observed_stat: 0.423,
      bootstrap_mean: 0.425,
      bootstrap_se: 0.089,
      ci_lower: 0.255,
      ci_upper: 0.591,
      true_param: 0.42,
      bootstrap_histogram: [
        { bin_center: 0.2, count: 10 },
        { bin_center: 0.3, count: 50 },
        { bin_center: 0.4, count: 150 },
        { bin_center: 0.5, count: 120 },
        { bin_center: 0.6, count: 45 },
        { bin_center: 0.7, count: 20 }
      ],
      percentiles: [
        { percentile: 2.5, value: 0.255 },
        { percentile: 5, value: 0.277 },
        { percentile: 25, value: 0.367 },
        { percentile: 50, value: 0.428 },
        { percentile: 75, value: 0.486 },
        { percentile: 95, value: 0.573 },
        { percentile: 97.5, value: 0.591 }
      ]
    };
    
    act(() => {
      mockWebSocket.simulateMessage({ 
        type: 'simulation_complete', 
        progress: 100, 
        status: 'complete',
        results: mockResults
      });
    });
    
    await waitFor(() => {
      // Check for results section
      expect(screen.getByText(/Simulation Results/i)).toBeInTheDocument();
      
      // Check for result metrics
      expect(screen.getByText(/Observed Mean/i)).toBeInTheDocument();
      expect(screen.getByText(/Bootstrap Mean/i)).toBeInTheDocument();
      expect(screen.getByText(/Bootstrap Standard Error/i)).toBeInTheDocument();
      expect(screen.getByText(/Bias/i)).toBeInTheDocument();
      
      // Check for specific values
      expect(screen.getByText(/0.4230/i)).toBeInTheDocument(); // observed_stat
      expect(screen.getByText(/0.4250/i)).toBeInTheDocument(); // bootstrap_mean
      expect(screen.getByText(/0.0890/i)).toBeInTheDocument(); // bootstrap_se
      
      // Check for CI bounds
      expect(screen.getByText(/Lower Bound: 0.2550/i)).toBeInTheDocument();
      expect(screen.getByText(/Upper Bound: 0.5910/i)).toBeInTheDocument();
      
      // Check for histogram
      expect(screen.getByText(/Bootstrap Distribution of Mean/i)).toBeInTheDocument();
      
      // Check for percentiles table
      expect(screen.getByText(/Bootstrap Percentiles/i)).toBeInTheDocument();
      expect(screen.getByText(/2.5%/i)).toBeInTheDocument();
      expect(screen.getByText(/97.5%/i)).toBeInTheDocument();
      
      // Check for interpretation
      expect(screen.getByText(/Interpretation/i)).toBeInTheDocument();
      expect(screen.getByText(/The percentile method simply uses the empirical percentiles/i)).toBeInTheDocument();
    });
  });
  
  test('handles WebSocket errors', async () => {
    renderComponent();
    
    // Click Run Simulation button to start
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Simulate a WebSocket error
    act(() => {
      mockWebSocket.simulateMessage({ 
        type: 'simulation_error', 
        message: 'Error in bootstrap simulation: insufficient memory' 
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Error in bootstrap simulation: insufficient memory/i)).toBeInTheDocument();
    });
  });
  
  test('shows error when no project is selected', () => {
    // Render with no projectId
    render(
      <MathJaxContext>
        <BootstrapSimulation projectId={null} />
      </MathJaxContext>
    );
    
    // Click Run Simulation button
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Check for error message
    expect(screen.getByText(/Please select a project before running a simulation/i)).toBeInTheDocument();
  });
  
  test('cleans up WebSocket on unmount', async () => {
    const { unmount } = renderComponent();
    
    // Create spy for WebSocket close method
    const closeSpy = jest.spyOn(mockWebSocket, 'close');
    
    // Unmount the component
    unmount();
    
    // Check if WebSocket was closed
    expect(closeSpy).toHaveBeenCalled();
  });
});