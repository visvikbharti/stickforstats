import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TestCalculator from '../../../components/probability_distributions/TestCalculator';

// Mock the notistack provider
jest.mock('notistack', () => ({
  SnackbarProvider: ({ children }) => children,
  useSnackbar: () => ({
    enqueueSnackbar: jest.fn(),
  }),
}));

// Mock the theme provider
jest.mock('@mui/material/styles', () => ({
  ...jest.requireActual('@mui/material/styles'),
  ThemeProvider: ({ children }) => children,
}));

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
    scaleLinear: jest.fn(() => ({
      domain: jest.fn(() => ({
        range: jest.fn()
      })),
      range: jest.fn()
    })),
    axisBottom: jest.fn(() => ({
      tickFormat: jest.fn(() => ({
        ticks: jest.fn()
      }))
    })),
    axisLeft: jest.fn(() => ({
      tickFormat: jest.fn(() => ({
        ticks: jest.fn()
      }))
    })),
    line: jest.fn(() => ({
      x: jest.fn(() => ({
        y: jest.fn(() => ({
          curve: jest.fn()
        }))
      }))
    })),
    curveBasis: jest.fn()
  };
});

describe('TestCalculator Component', () => {
  beforeEach(() => {
    // Mock localStorage
    const localStorageMock = {
      getItem: jest.fn(() => null),
      setItem: jest.fn(),
      clear: jest.fn()
    };
    global.localStorage = localStorageMock;
    
    // Mock Element.getBoundingClientRect
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

    // Mock window.matchMedia for the useMediaQuery hook
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(), // deprecated
        removeListener: jest.fn(), // deprecated
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
  });

  test('renders without crashing', () => {
    render(<TestCalculator />);
    expect(screen.getByText(/Probability Calculator/i)).toBeInTheDocument();
  });

  test('displays tutorial on initial load', () => {
    render(<TestCalculator />);
    expect(screen.getByText(/Welcome to the Probability Calculator/i)).toBeInTheDocument();
    expect(screen.getByText(/This tool helps you calculate and visualize probabilities/i)).toBeInTheDocument();
  });

  test('can navigate through tutorial steps', async () => {
    render(<TestCalculator />);
    
    // Check initial step
    expect(screen.getByText(/Welcome to the Probability Calculator/i)).toBeInTheDocument();
    
    // Navigate to next step
    const nextButton = screen.getByRole('button', { name: /Next/i });
    fireEvent.click(nextButton);
    
    // Check next step content
    await waitFor(() => {
      expect(screen.getByText(/Step 1: Select a Distribution/i)).toBeInTheDocument();
    });
    
    // Navigate to the third step
    fireEvent.click(nextButton);
    
    // Check third step content
    await waitFor(() => {
      expect(screen.getByText(/Step 2: Adjust Parameters/i)).toBeInTheDocument();
    });
  });

  test('can close tutorial', () => {
    render(<TestCalculator />);
    
    // Check tutorial is shown
    expect(screen.getByText(/Welcome to the Probability Calculator/i)).toBeInTheDocument();
    
    // Close tutorial
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    // Check tutorial is closed
    expect(screen.queryByText(/Welcome to the Probability Calculator/i)).not.toBeInTheDocument();
  });

  test('allows changing distribution type', () => {
    render(<TestCalculator />);
    
    // Close the tutorial first
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    // Find the select component
    const selectElement = screen.getByLabelText(/distribution type/i);
    
    // Open the dropdown
    fireEvent.mouseDown(selectElement);
    
    // Select a different distribution
    const binomialOption = screen.getByRole('option', { name: /binomial/i });
    fireEvent.click(binomialOption);
    
    // Check if parameters have been updated for binomial
    expect(screen.getByText(/Number of trials/i)).toBeInTheDocument();
  });

  test('can display tutorial again after closing', () => {
    render(<TestCalculator />);
    
    // Close the tutorial first
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    // Show tutorial again
    const tutorialButton = screen.getByRole('button', { name: /Show tutorial/i });
    fireEvent.click(tutorialButton);
    
    // Check tutorial is shown again
    expect(screen.getByText(/Welcome to the Probability Calculator/i)).toBeInTheDocument();
  });
});