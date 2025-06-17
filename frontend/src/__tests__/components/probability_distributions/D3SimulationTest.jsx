/**
 * Helper component for testing D3.js simulations
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock D3
jest.mock('d3', () => {
  const mockSelection = {
    attr: jest.fn().mockReturnThis(),
    style: jest.fn().mockReturnThis(),
    append: jest.fn().mockReturnThis(),
    text: jest.fn().mockReturnThis(),
    data: jest.fn().mockReturnThis(),
    enter: jest.fn().mockReturnThis(),
    exit: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    join: jest.fn().mockReturnThis(),
    selectAll: jest.fn().mockReturnThis(),
    select: jest.fn().mockReturnThis(),
    call: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    transition: jest.fn().mockReturnThis(),
    duration: jest.fn().mockReturnThis(),
    ease: jest.fn().mockReturnThis(),
    domain: jest.fn().mockReturnThis(),
    range: jest.fn().mockReturnThis(),
    ticks: jest.fn().mockReturnThis(),
    tickFormat: jest.fn().mockReturnThis(),
  };
  
  const d3Mock = {
    select: jest.fn(() => mockSelection),
    selectAll: jest.fn(() => mockSelection),
    scaleLinear: jest.fn(() => ({
      domain: jest.fn().mockReturnThis(),
      range: jest.fn().mockReturnThis(),
      ticks: jest.fn().mockReturnThis(),
      tickFormat: jest.fn().mockReturnThis(),
    })),
    scaleBand: jest.fn(() => ({
      domain: jest.fn().mockReturnThis(),
      range: jest.fn().mockReturnThis(),
      padding: jest.fn().mockReturnThis(),
      bandwidth: jest.fn(() => 20),
    })),
    axisBottom: jest.fn(() => jest.fn()),
    axisLeft: jest.fn(() => jest.fn()),
    line: jest.fn(() => jest.fn()),
    area: jest.fn(() => jest.fn()),
    curveCatmullRom: { alpha: jest.fn(() => jest.fn()) },
    max: jest.fn(() => 100),
    min: jest.fn(() => 0),
    extent: jest.fn(() => [0, 100]),
    randomUniform: jest.fn(() => jest.fn(() => 0.5)),
    randomPoisson: jest.fn(() => jest.fn(() => 5)),
    randomExponential: jest.fn(() => jest.fn(() => 0.2)),
    randomNormal: jest.fn(() => jest.fn(() => 10)),
    randomBinomial: jest.fn(() => jest.fn(() => 5)),
    drag: jest.fn(() => ({
      on: jest.fn().mockReturnThis(),
    })),
    brushX: jest.fn(() => ({
      on: jest.fn().mockReturnThis(),
    })),
    format: jest.fn(() => jest.fn(val => `${val}`)),
  };
  
  return d3Mock;
});

// Mock KaTeX
jest.mock('react-katex', () => ({
  InlineMath: jest.fn(({ math }) => <span data-testid="inline-math">{math}</span>),
  BlockMath: jest.fn(({ math }) => <div data-testid="block-math">{math}</div>),
}));

// Mock Framer Motion
jest.mock('framer-motion', () => ({
  motion: {
    div: jest.fn(props => <div {...props} />),
    svg: jest.fn(props => <svg {...props} />),
    path: jest.fn(props => <path {...props} />),
    circle: jest.fn(props => <circle {...props} />),
    rect: jest.fn(props => <rect {...props} />),
    g: jest.fn(props => <g {...props} />),
  },
  AnimatePresence: jest.fn(({ children }) => <>{children}</>),
}));

/**
 * Render a D3.js simulation component for testing
 * @param {React.Component} Component - The D3 simulation component to test 
 * @param {Object} props - Props to pass to the component
 * @returns {Object} - Testing utilities and additional helpers
 */
export const renderD3Simulation = (Component, props = {}) => {
  // Default props that simulate typical usage
  const defaultProps = {
    projectId: 'test-project',
    setLoading: jest.fn(),
    setError: jest.fn(),
    setSimulationResult: jest.fn(),
    result: null,
  };
  
  // Merge with provided props
  const mergedProps = { ...defaultProps, ...props };
  
  // Render the component
  const utils = render(<Component {...mergedProps} />);
  
  // Custom helper for triggering slider changes
  const changeSlider = (testId, value) => {
    const slider = screen.getByTestId(testId);
    fireEvent.change(slider, { target: { value } });
  };
  
  // Helper for running a simulation
  const runSimulation = async () => {
    const runButton = screen.getByTestId(/run-simulation-button/);
    fireEvent.click(runButton);
    
    await waitFor(() => {
      expect(mergedProps.setSimulationResult).toHaveBeenCalled();
    });
  };
  
  // Helper for checking if a chart exists
  const chartExists = (testId) => {
    const chart = screen.getByTestId(testId);
    return chart !== null;
  };
  
  // Helper for finding metric values
  const getMetricValue = (testId) => {
    const metric = screen.getByTestId(testId);
    return metric.textContent;
  };
  
  return {
    ...utils,
    changeSlider,
    runSimulation,
    chartExists,
    getMetricValue,
  };
};

export default renderD3Simulation;