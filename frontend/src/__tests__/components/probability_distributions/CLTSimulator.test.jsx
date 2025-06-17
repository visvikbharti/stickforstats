import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import CLTSimulator from '../../../components/probability_distributions/educational/CLTSimulator';

// Mock D3.js as it's not available in jsdom environment
jest.mock('d3', () => {
  const originalD3 = jest.requireActual('d3');
  return {
    ...originalD3,
    select: jest.fn(() => ({
      selectAll: jest.fn(() => ({
        remove: jest.fn()
      })),
      append: jest.fn(() => ({
        attr: jest.fn(() => ({
          attr: jest.fn(() => ({
            attr: jest.fn(() => ({
              attr: jest.fn(() => ({
                attr: jest.fn(() => ({
                  style: jest.fn()
                }))
              }))
            }))
          })),
        data: jest.fn(() => ({
          enter: jest.fn(() => ({
            append: jest.fn(() => ({
              attr: jest.fn(() => ({
                attr: jest.fn(() => ({
                  attr: jest.fn(() => ({
                    attr: jest.fn(() => ({
                      attr: jest.fn(() => ({
                        attr: jest.fn()
                      }))
                    }))
                  }))
                }))
              }))
            }))
          })),
        datum: jest.fn(() => ({
          attr: jest.fn(() => ({
            attr: jest.fn(() => ({
              attr: jest.fn(() => ({
                attr: jest.fn()
              }))
            }))
          }))
        })),
        call: jest.fn()
      }))
    })),
    scaleBand: jest.fn(() => ({
      domain: jest.fn(() => ({
        range: jest.fn(() => ({
          padding: jest.fn()
        }))
      })),
      bandwidth: jest.fn(() => 10)
    })),
    scaleLinear: jest.fn(() => ({
      domain: jest.fn(() => ({
        range: jest.fn()
      })),
      range: jest.fn()
    })),
    axisBottom: jest.fn(() => ({
      tickSize: jest.fn(() => ({
        tickPadding: jest.fn(() => ({
          ticks: jest.fn()
        }))
      }))
    })),
    axisLeft: jest.fn(() => ({
      tickSize: jest.fn(() => ({
        tickPadding: jest.fn(() => ({
          ticks: jest.fn()
        }))
      }))
    })),
    line: jest.fn(() => ({
      x: jest.fn(() => ({
        y: jest.fn(() => ({
          curve: jest.fn()
        }))
      }))
    })),
    area: jest.fn(() => ({
      x: jest.fn(() => ({
        y0: jest.fn(() => ({
          y1: jest.fn(() => ({
            curve: jest.fn()
          }))
        }))
      }))
    })),
    curveBasis: jest.fn()
  };
});

describe('CLTSimulator Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    
    // Mock Element.getBoundingClientRect to support D3.js
    Element.prototype.getBoundingClientRect = jest.fn(() => {
      return {
        width: 500,
        height: 300,
        top: 0,
        left: 0,
        bottom: 0,
        right: 0
      };
    });
    
    // Mock ResizeObserver
    global.ResizeObserver = jest.fn().mockImplementation(() => ({
      observe: jest.fn(),
      unobserve: jest.fn(),
      disconnect: jest.fn()
    }));
    
    // Mock requestAnimationFrame
    global.requestAnimationFrame = jest.fn(cb => setTimeout(cb, 0));
    
    // Mock for timers
    jest.useFakeTimers();
  });
  
  afterEach(() => {
    jest.useRealTimers();
  });
  
  test('renders without crashing', () => {
    render(<CLTSimulator />);
    expect(screen.getByText(/Central Limit Theorem Simulator/i)).toBeInTheDocument();
  });
  
  test('displays simulation controls', () => {
    render(<CLTSimulator />);
    expect(screen.getByLabelText(/Distribution Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Sample Size/i)).toBeInTheDocument();
    expect(screen.getByText(/Number of Samples/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Run Simulation/i })).toBeInTheDocument();
  });
  
  test('allows changing distribution type', () => {
    render(<CLTSimulator />);
    const select = screen.getByLabelText(/Distribution Type/i);
    
    // Open the select dropdown
    fireEvent.mouseDown(select);
    
    // Find and select the Normal distribution option
    const option = screen.getByText(/Normal/i);
    fireEvent.click(option);
    
    // The select should now show the new value
    expect(select).toHaveTextContent(/Normal/i);
  });
  
  test('runs simulation when button is clicked', async () => {
    // Arrange
    render(<CLTSimulator />);
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    
    // Act
    fireEvent.click(runButton);
    
    // Wait for loading state
    expect(screen.getByText(/Simulation in progress/i)).toBeInTheDocument();
    
    // Fast-forward timers to complete the simulation
    act(() => {
      jest.advanceTimersByTime(5000);
    });
    
    // Assert
    await waitFor(() => {
      expect(screen.queryByText(/Simulation in progress/i)).not.toBeInTheDocument();
    });
  });
  
  test('reset button clears simulation results', async () => {
    // Arrange
    render(<CLTSimulator />);
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    
    // Act - run simulation
    fireEvent.click(runButton);
    
    // Fast-forward timers to complete the simulation
    act(() => {
      jest.advanceTimersByTime(5000);
    });
    
    // Wait for simulation to complete
    await waitFor(() => {
      expect(screen.queryByText(/Simulation in progress/i)).not.toBeInTheDocument();
    });
    
    // Find and click the reset button
    const resetButton = screen.getByRole('button', { name: /Reset/i });
    fireEvent.click(resetButton);
    
    // Assert
    expect(screen.getByText(/Run the simulation to see the original distribution/i)).toBeInTheDocument();
    expect(screen.getByText(/Run the simulation to see the sampling distribution/i)).toBeInTheDocument();
  });
  
  test('shows mathematical formula', () => {
    render(<CLTSimulator />);
    
    // Check that the Central Limit Theorem formula section is present
    expect(screen.getByText(/Central Limit Theorem \(CLT\) states/i)).toBeInTheDocument();
    expect(screen.getByText(/Where:/i)).toBeInTheDocument();
    expect(screen.getByText(/is the sample mean/i)).toBeInTheDocument();
    expect(screen.getByText(/is the population mean/i)).toBeInTheDocument();
    expect(screen.getByText(/is the population standard deviation/i)).toBeInTheDocument();
    expect(screen.getByText(/is the sample size/i)).toBeInTheDocument();
  });
  
  test('displays simulation results after completion', async () => {
    // Arrange
    render(<CLTSimulator />);
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    
    // Act
    fireEvent.click(runButton);
    
    // Fast-forward timers to complete the simulation
    act(() => {
      jest.advanceTimersByTime(5000);
    });
    
    // Assert
    await waitFor(() => {
      expect(screen.queryByText(/Original Distribution/i)).toBeInTheDocument();
      expect(screen.queryByText(/Sampling Distribution of the Mean/i)).toBeInTheDocument();
    });
  });
});