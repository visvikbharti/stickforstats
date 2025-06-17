import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import DistributionAnimation from '../../../components/probability_distributions/educational/DistributionAnimation';

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

describe('DistributionAnimation Component', () => {
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
  });

  test('renders without crashing', async () => {
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    expect(screen.getByText(/Normal Distribution/i)).toBeInTheDocument();
  });

  test('shows loading state initially', async () => {
    render(<DistributionAnimation type="NORMAL" />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    await waitFor(() => {
      // Since we're using client-side calculations, check if distribution parameters are initialized
      expect(screen.getByText(/Mean \(μ\): 0/i)).toBeInTheDocument();
      expect(screen.getByText(/Standard Deviation \(σ\): 1/i)).toBeInTheDocument();
    });
  });

  test('initializes distribution data on mount', async () => {
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    // Check that default parameters were used
    expect(screen.getByText(/Mean \(μ\): 0/i)).toBeInTheDocument();
    expect(screen.getByText(/Standard Deviation \(σ\): 1/i)).toBeInTheDocument();
  });

  test('updates parameters when sliders are adjusted', async () => {
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText(/Mean \(μ\): 0/i)).toBeInTheDocument();
    });
    
    // Find and move the mean slider
    const meanSlider = screen.getByRole('slider', { name: /mean/i });
    fireEvent.change(meanSlider, { target: { value: 2 } });
    
    // Check if the UI updates with new parameter value
    await waitFor(() => {
      expect(screen.getByText(/Mean \(μ\): 2/i)).toBeInTheDocument();
    });
  });

  test('plays animation when play button is clicked', async () => {
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    // Wait for initial load
    await waitFor(() => {
      expect(calculatePmfPdf).toHaveBeenCalled();
    });
    
    // Click play button
    const playButton = screen.getByRole('button', { name: /play/i });
    fireEvent.click(playButton);
    
    // Animation state should change to "playing"
    await waitFor(() => {
      // Since we're using a setTimeout in the component, we need to wait for state to update
      expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
    });
  });

  test('pauses animation when pause button is clicked', async () => {
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    // Wait for initial load
    await waitFor(() => {
      expect(calculatePmfPdf).toHaveBeenCalled();
    });
    
    // Click play button
    const playButton = screen.getByRole('button', { name: /play/i });
    fireEvent.click(playButton);
    
    // Wait for play state
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
    });
    
    // Click pause button
    const pauseButton = screen.getByRole('button', { name: /pause/i });
    fireEvent.click(pauseButton);
    
    // Animation state should change to "paused"
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument();
    });
  });

  test('resets animation when reset button is clicked', async () => {
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    // Wait for initial load
    await waitFor(() => {
      expect(calculatePmfPdf).toHaveBeenCalled();
    });
    
    // Click play button to start
    const playButton = screen.getByRole('button', { name: /play/i });
    fireEvent.click(playButton);
    
    // Wait for play state
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
    });
    
    // Click reset button
    const resetButton = screen.getByRole('button', { name: /reset/i });
    fireEvent.click(resetButton);
    
    // Animation should reset
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument();
      // Check for initial explanation text being present (first animation step)
      expect(screen.getByText(/The Normal distribution is characterized by its bell-shaped curve/i)).toBeInTheDocument();
    });
  });

  test('renders parameter controls for the Normal distribution', async () => {
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    // Parameter sliders should be present
    expect(screen.getByText(/Mean \(μ\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Standard Deviation \(σ\)/i)).toBeInTheDocument();
    
    // Sliders should be interactive
    const meanSlider = screen.getByRole('slider', { name: /mean/i });
    const stdSlider = screen.getByRole('slider', { name: /standard deviation/i });
    
    expect(meanSlider).toBeInTheDocument();
    expect(stdSlider).toBeInTheDocument();
  });

  test('renders different parameter controls for Binomial distribution', async () => {
    await act(async () => {
      render(<DistributionAnimation type="BINOMIAL" />);
    });
    
    // Parameter sliders should be present
    expect(screen.getByText(/Number of Trials \(n\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Success Probability \(p\)/i)).toBeInTheDocument();
  });

  test('advances to sample generation step during animation', async () => {
    // Mock timers
    jest.useFakeTimers();
    
    await act(async () => {
      render(<DistributionAnimation type="NORMAL" />);
    });
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText(/Normal Distribution/i)).toBeInTheDocument();
    });
    
    // Click play button to start
    const playButton = screen.getByRole('button', { name: /play/i });
    await act(async () => {
      fireEvent.click(playButton);
    });
    
    // Advance to step 3 (sample generation step) by running timers
    await act(async () => {
      jest.advanceTimersByTime(2000); // First step
      jest.advanceTimersByTime(2000); // Second step
      jest.advanceTimersByTime(2000); // Third step (sample generation)
    });
    
    // Check if we're on the sample generation step by checking for text
    await waitFor(() => {
      expect(screen.getByText(/Now let's generate random samples/i)).toBeInTheDocument();
    });
    
    // Restore real timers
    jest.useRealTimers();
  });
});