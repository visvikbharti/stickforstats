import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import SampleSizeSimulation from '../../../components/confidence_intervals/simulations/SampleSizeSimulation';
import { MathJaxContext } from 'better-react-mathjax';

// Mock recharts
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="mock-responsive-container">{children}</div>,
  LineChart: ({ children }) => <div data-testid="mock-line-chart">{children}</div>,
  ScatterChart: ({ children }) => <div data-testid="mock-scatter-chart">{children}</div>,
  Line: () => <div data-testid="mock-line">Line</div>,
  Scatter: () => <div data-testid="mock-scatter">Scatter</div>,
  XAxis: () => <div data-testid="mock-xaxis">XAxis</div>,
  YAxis: () => <div data-testid="mock-yaxis">YAxis</div>,
  CartesianGrid: () => <div data-testid="mock-cartesian-grid">CartesianGrid</div>,
  Tooltip: () => <div data-testid="mock-tooltip">Tooltip</div>,
  Legend: () => <div data-testid="mock-legend">Legend</div>,
  ReferenceLine: () => <div data-testid="mock-reference-line">ReferenceLine</div>,
  Label: () => <div data-testid="mock-label">Label</div>,
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
        progress: 10, 
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

describe('SampleSizeSimulation Component', () => {
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
        <SampleSizeSimulation projectId={projectId} {...props} />
      </MathJaxContext>
    );
  };
  
  test('renders the basic UI elements', () => {
    renderComponent();
    
    // Check if title and description are rendered
    expect(screen.getByText(/Sample Size Effects Simulation/i)).toBeInTheDocument();
    expect(screen.getByText(/This simulation demonstrates how sample size affects/i)).toBeInTheDocument();
    
    // Check if form elements are rendered
    expect(screen.getByLabelText(/Interval Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Distribution Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Confidence Level/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Minimum Sample Size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Maximum Sample Size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Sample Size Step/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Number of Simulations per Sample Size/i)).toBeInTheDocument();
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
  
  test('handles interval type change', () => {
    renderComponent();
    
    // Get the select element for interval type
    const intervalTypeSelect = screen.getByLabelText(/Interval Type/i);
    
    // Change value to a different interval type
    fireEvent.change(intervalTypeSelect, { target: { value: 'PROPORTION_WILSON' } });
    
    // Check if proportion method selection appears
    expect(screen.getByLabelText(/Proportion Method/i)).toBeInTheDocument();
    
    // Now change to a non-proportion type
    fireEvent.change(intervalTypeSelect, { target: { value: 'MEAN_T' } });
    
    // Check that proportion method is no longer visible
    expect(screen.queryByLabelText(/Proportion Method/i)).not.toBeInTheDocument();
  });
  
  test('handles distribution type change and shows appropriate parameters', () => {
    renderComponent();
    
    // Get the select element for distribution type
    const distributionTypeSelect = screen.getByLabelText(/Distribution Type/i);
    
    // Change to different distribution types and check for specific parameters
    
    // Normal distribution
    fireEvent.change(distributionTypeSelect, { target: { value: 'NORMAL' } });
    expect(screen.getByText(/Mean/i)).toBeInTheDocument();
    expect(screen.getByText(/Standard Deviation/i)).toBeInTheDocument();
    
    // T-distribution
    fireEvent.change(distributionTypeSelect, { target: { value: 'T' } });
    expect(screen.getByText(/Degrees of Freedom/i)).toBeInTheDocument();
    
    // Binomial distribution
    fireEvent.change(distributionTypeSelect, { target: { value: 'BINOMIAL' } });
    expect(screen.getByText(/Success Probability/i)).toBeInTheDocument();
  });
  
  test('validates sample size parameters', () => {
    renderComponent();
    
    // Test minimum sample size validation
    const minSampleSizeInput = screen.getByLabelText(/Minimum Sample Size/i);
    fireEvent.change(minSampleSizeInput, { target: { value: '200' } });
    // Validation should prevent this value from being set since it's > max
    
    // Test maximum sample size validation
    const maxSampleSizeInput = screen.getByLabelText(/Maximum Sample Size/i);
    fireEvent.change(maxSampleSizeInput, { target: { value: '400' } });
    
    // Now min should accept a higher value
    fireEvent.change(minSampleSizeInput, { target: { value: '150' } });
    expect(minSampleSizeInput.value).toBe('150');
    
    // Test sample size step validation
    const stepInput = screen.getByLabelText(/Sample Size Step/i);
    fireEvent.change(stepInput, { target: { value: '25' } });
    expect(stepInput.value).toBe('25');
  });
  
  test('sends correct parameters when running simulation', async () => {
    renderComponent();
    
    // Set up parameters
    fireEvent.change(screen.getByLabelText(/Interval Type/i), { target: { value: 'MEAN_T' } });
    fireEvent.change(screen.getByLabelText(/Distribution Type/i), { target: { value: 'NORMAL' } });
    
    // Set sample size parameters
    fireEvent.change(screen.getByLabelText(/Minimum Sample Size/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/Maximum Sample Size/i), { target: { value: '200' } });
    fireEvent.change(screen.getByLabelText(/Sample Size Step/i), { target: { value: '20' } });
    
    // Set number of simulations
    fireEvent.change(screen.getByLabelText(/Number of Simulations per Sample Size/i), { target: { value: '300' } });
    
    // Click Run Simulation button
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    await waitFor(() => {
      // Check that WebSocket sent the correct data
      const sentData = JSON.parse(mockWebSocket.lastSentData);
      expect(sentData.action).toBe('start_sample_size_simulation');
      expect(sentData.params.project_id).toBe(projectId);
      expect(sentData.params.interval_type).toBe('MEAN_T');
      expect(sentData.params.distribution).toBe('NORMAL');
      expect(sentData.params.min_sample_size).toBe(10);
      expect(sentData.params.max_sample_size).toBe(200);
      expect(sentData.params.sample_size_step).toBe(20);
      expect(sentData.params.n_simulations).toBe(300);
    });
  });
  
  test('updates progress when receiving WebSocket messages', async () => {
    renderComponent();
    
    // Click Run Simulation button to start
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Simulate progress updates
    act(() => {
      mockWebSocket.simulateMessage({ 
        type: 'simulation_update', 
        progress: 35, 
        status: 'running' 
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/35%/)).toBeInTheDocument();
    });
    
    // Simulate more progress
    act(() => {
      mockWebSocket.simulateMessage({ 
        type: 'simulation_update', 
        progress: 85, 
        status: 'running' 
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/85%/)).toBeInTheDocument();
    });
  });
  
  test('displays results when simulation completes', async () => {
    renderComponent();
    
    // Click Run Simulation button to start
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Simulate simulation completion with results
    const mockResults = {
      sample_sizes: [10, 20, 30, 40, 50],
      coverages: [0.92, 0.93, 0.94, 0.945, 0.95],
      avg_widths: [1.25, 0.9, 0.7, 0.63, 0.56],
      theoretical_widths: [1.23, 0.87, 0.71, 0.62, 0.55]
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
      expect(screen.getByText(/Coverage Probability vs. Sample Size/i)).toBeInTheDocument();
      expect(screen.getByText(/Average Interval Width vs. Sample Size/i)).toBeInTheDocument();
      expect(screen.getByText(/Log-Log Plot/i)).toBeInTheDocument();
      
      // Check for detailed results table
      expect(screen.getByText(/Detailed Results/i)).toBeInTheDocument();
      
      // Check for interpretation section
      expect(screen.getByText(/Interpretation/i)).toBeInTheDocument();
      expect(screen.getByText(/Effect on Coverage Probability/i)).toBeInTheDocument();
      expect(screen.getByText(/Effect on Interval Width/i)).toBeInTheDocument();
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
        message: 'Failed to run simulation due to server error' 
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to run simulation due to server error/i)).toBeInTheDocument();
    });
  });
  
  test('shows error when no project is selected', () => {
    // Render with no projectId
    render(
      <MathJaxContext>
        <SampleSizeSimulation projectId={null} />
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