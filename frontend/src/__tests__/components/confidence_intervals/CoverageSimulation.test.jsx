import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import CoverageSimulation from '../../../components/confidence_intervals/simulations/CoverageSimulation';
import { MathJaxContext } from 'better-react-mathjax';
import axios from 'axios';

// Mock dependencies
jest.mock('axios');
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="mock-responsive-container">{children}</div>,
  BarChart: ({ children }) => <div data-testid="mock-bar-chart">{children}</div>,
  LineChart: ({ children }) => <div data-testid="mock-line-chart">{children}</div>,
  ComposedChart: ({ children }) => <div data-testid="mock-composed-chart">{children}</div>,
  Bar: () => <div data-testid="mock-bar">Bar</div>,
  Line: () => <div data-testid="mock-line">Line</div>,
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

describe('CoverageSimulation Component', () => {
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
        <CoverageSimulation projectId={projectId} {...props} />
      </MathJaxContext>
    );
  };
  
  test('renders the basic UI elements', () => {
    renderComponent();
    
    // Check if title and description are rendered
    expect(screen.getByText(/Coverage Properties Simulation/i)).toBeInTheDocument();
    expect(screen.getByText(/This simulation allows you to explore/i)).toBeInTheDocument();
    
    // Check if form elements are rendered
    expect(screen.getByLabelText(/Interval Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Distribution Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Confidence Level/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Sample Size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Number of Simulations/i)).toBeInTheDocument();
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
    
    // Now change to a variance type
    fireEvent.change(intervalTypeSelect, { target: { value: 'VARIANCE' } });
    
    // Check if equivariance option appears
    expect(screen.getByLabelText(/Use Equivariance/i)).toBeInTheDocument();
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
  
  test('sends correct parameters when running simulation', async () => {
    renderComponent();
    
    // Set up parameters
    fireEvent.change(screen.getByLabelText(/Interval Type/i), { target: { value: 'MEAN_T' } });
    fireEvent.change(screen.getByLabelText(/Distribution Type/i), { target: { value: 'NORMAL' } });
    
    // Find the Sample Size input and change it
    const sampleSizeInput = screen.getByLabelText(/Sample Size/i);
    fireEvent.change(sampleSizeInput, { target: { value: '50' } });
    
    // Find the Number of Simulations input and change it
    const numSimulationsInput = screen.getByLabelText(/Number of Simulations/i);
    fireEvent.change(numSimulationsInput, { target: { value: '500' } });
    
    // Click Run Simulation button
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    await waitFor(() => {
      // Check that WebSocket sent the correct data
      const sentData = JSON.parse(mockWebSocket.lastSentData);
      expect(sentData.action).toBe('start_coverage_simulation');
      expect(sentData.params.project_id).toBe(projectId);
      expect(sentData.params.interval_type).toBe('MEAN_T');
      expect(sentData.params.distribution).toBe('NORMAL');
      expect(sentData.params.sample_size).toBe(50);
      expect(sentData.params.n_simulations).toBe(500);
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
        progress: 25, 
        status: 'running' 
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/25%/)).toBeInTheDocument();
    });
    
    // Simulate more progress
    act(() => {
      mockWebSocket.simulateMessage({ 
        type: 'simulation_update', 
        progress: 75, 
        status: 'running' 
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/75%/)).toBeInTheDocument();
    });
  });
  
  test('displays results when simulation completes', async () => {
    renderComponent();
    
    // Click Run Simulation button to start
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Simulate simulation completion with results
    const mockResults = {
      coverage_rate: 0.942,
      mean_interval_width: 0.8534,
      median_interval_width: 0.8201,
      intervals_containing_true_param: 942,
      width_histogram: [
        { bin_center: 0.7, count: 25 },
        { bin_center: 0.8, count: 150 },
        { bin_center: 0.9, count: 750 },
        { bin_center: 1.0, count: 75 }
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
      expect(screen.getByText(/Coverage Comparison/i)).toBeInTheDocument();
      expect(screen.getByText(/Interval Widths Distribution/i)).toBeInTheDocument();
      
      // Check for specific result values
      expect(screen.getByText(/Actual Coverage: 94.2%/i)).toBeInTheDocument();
      expect(screen.getByText(/Average Interval Width: 0.8534/i)).toBeInTheDocument();
      expect(screen.getByText(/Median Interval Width: 0.8201/i)).toBeInTheDocument();
      expect(screen.getByText(/Number of Intervals Containing True Parameter: 942/i)).toBeInTheDocument();
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
  
  test('handles WebSocket unexpected close', async () => {
    renderComponent();
    
    // Click Run Simulation button to start
    fireEvent.click(screen.getByText(/Run Simulation/i));
    
    // Simulate unexpected WebSocket close
    act(() => {
      mockWebSocket.simulateClose(1006); // 1006 is abnormal closure
    });
    
    await waitFor(() => {
      expect(screen.getByText(/WebSocket connection closed unexpectedly/i)).toBeInTheDocument();
    });
  });
  
  test('shows error when no project is selected', () => {
    // Render with no projectId
    render(
      <MathJaxContext>
        <CoverageSimulation projectId={null} />
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