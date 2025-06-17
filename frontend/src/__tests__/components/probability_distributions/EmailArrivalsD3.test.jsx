import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EmailArrivalsD3 from '../../../components/probability_distributions/simulations/EmailArrivalsD3';
import { renderD3Simulation } from './D3SimulationTest';

describe('EmailArrivalsD3 Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock window.requestAnimationFrame
    window.requestAnimationFrame = jest.fn(callback => {
      callback();
      return 1;
    });
    
    // Mock Element.getBoundingClientRect
    Element.prototype.getBoundingClientRect = jest.fn(() => {
      return {
        width: 600,
        height: 300,
        top: 0,
        left: 0,
        bottom: 0,
        right: 0,
        x: 0,
        y: 0
      };
    });
    
    // Set up mocks for clientWidth and clientHeight
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', {
      configurable: true,
      value: 600
    });
    
    Object.defineProperty(HTMLElement.prototype, 'clientHeight', {
      configurable: true,
      value: 300
    });
  });
  
  test('renders component with parameter controls', () => {
    renderD3Simulation(EmailArrivalsD3);
    
    expect(screen.getByText(/Simulation Parameters/i)).toBeInTheDocument();
    expect(screen.getByText(/Average Email Arrival Rate/i)).toBeInTheDocument();
    expect(screen.getByText(/Workday Length/i)).toBeInTheDocument();
    expect(screen.getByText(/Server Daily Capacity/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Run Simulation/i })).toBeInTheDocument();
  });
  
  test('shows advanced visualization settings when toggled', async () => {
    renderD3Simulation(EmailArrivalsD3);
    
    const settingsButton = screen.getByRole('button', { name: /Show Visualization Settings/i });
    expect(settingsButton).toBeInTheDocument();
    
    // Toggle settings
    fireEvent.click(settingsButton);
    
    // Settings should now be visible
    await waitFor(() => {
      expect(screen.getByText(/Show Animations/i)).toBeInTheDocument();
      expect(screen.getByText(/Show Data Points/i)).toBeInTheDocument();
      expect(screen.getByText(/Show Legend/i)).toBeInTheDocument();
    });
    
    // Toggle settings again to hide
    fireEvent.click(settingsButton);
    
    // Wait for animation to complete
    await waitFor(() => {
      expect(screen.queryByText(/Show Animations/i)).not.toBeInTheDocument();
    });
  });
  
  test('shows educational content about Poisson distribution', () => {
    renderD3Simulation(EmailArrivalsD3);
    
    expect(screen.getByText(/Poisson Process Model/i)).toBeInTheDocument();
    expect(screen.getByText(/The Poisson distribution models random events/i)).toBeInTheDocument();
    
    // Check if KaTeX formulas are rendered
    expect(screen.getAllByTestId('block-math').length).toBeGreaterThan(0);
  });
  
  test('runs simulation when button is clicked', async () => {
    const { runSimulation } = renderD3Simulation(EmailArrivalsD3);
    
    // No simulation data initially
    expect(screen.getByText(/No Simulation Data/i)).toBeInTheDocument();
    
    // Run simulation
    await runSimulation();
    
    // Wait for simulation to complete and results to be shown
    await waitFor(() => {
      expect(screen.getByText(/Simulation Results/i)).toBeInTheDocument();
    });
  });
  
  test('can update simulation parameters', async () => {
    const setSimulationResult = jest.fn();
    const { changeSlider } = renderD3Simulation(EmailArrivalsD3, { 
      setSimulationResult 
    });
    
    // Change parameter values
    changeSlider('arrival-rate-slider', 30);
    changeSlider('workday-length-slider', 12);
    changeSlider('server-capacity-slider', 400);
    
    // Run simulation with new parameters
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    fireEvent.click(runButton);
    
    // Verify simulation was run with new parameters
    expect(setSimulationResult).toHaveBeenCalled();
  });
  
  test('displays warnings when capacity is likely to be exceeded', async () => {
    // Create a simulation result with high probability of exceeding capacity
    const mockResult = {
      hourly_arrivals: [25, 30, 18, 22, 28, 35, 21, 27],
      total_arrivals: 206,
      k_values: Array.from({ length: 300 }, (_, i) => i),
      theoretical_pmf: Array.from({ length: 300 }, () => 0.005),
      theoretical_cdf: Array.from({ length: 300 }, (_, i) => i / 300),
      observed_pmf: Array.from({ length: 300 }, () => 0),
      daily_rate: 200,
      exceeds_capacity: true
    };
    
    renderD3Simulation(EmailArrivalsD3, { result: mockResult });
    
    // Warning should be displayed
    await waitFor(() => {
      expect(screen.getByText(/the server capacity was exceeded/i)).toBeInTheDocument();
    });
  });
  
  test('can reset simulation', async () => {
    const setSimulationResult = jest.fn();
    // Start with a result already set
    const mockResult = {
      hourly_arrivals: [20, 18, 22, 19, 21, 23, 17, 20],
      total_arrivals: 160,
      k_values: Array.from({ length: 300 }, (_, i) => i),
      theoretical_pmf: Array.from({ length: 300 }, () => 0.005),
      theoretical_cdf: Array.from({ length: 300 }, (_, i) => i / 300),
      observed_pmf: Array.from({ length: 300 }, () => 0),
      daily_rate: 160,
      exceeds_capacity: false
    };
    
    renderD3Simulation(EmailArrivalsD3, {
      setSimulationResult,
      result: mockResult
    });
    
    // Simulation results should be visible
    expect(screen.getByText(/Simulation Results/i)).toBeInTheDocument();
    
    // Find and click the reset button
    const resetButton = screen.getByRole('button', { name: /Reset/i });
    fireEvent.click(resetButton);
    
    // setSimulationResult should be called with null to reset
    expect(setSimulationResult).toHaveBeenCalledWith(null);
  });
});