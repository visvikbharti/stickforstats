import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import QualityControlD3 from '../../../components/probability_distributions/simulations/QualityControlD3';

// Mock D3.js as it's not available in jsdom environment
jest.mock('d3', () => {
  return {
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
                  style: jest.fn(),
                  on: jest.fn()
                }))
              }))
            }))
          })),
        append: jest.fn(() => ({
          attr: jest.fn(() => ({
            attr: jest.fn()
          }))
        })),
        selectAll: jest.fn(() => ({
          data: jest.fn(() => ({
            join: jest.fn(() => ({
              attr: jest.fn(() => ({
                attr: jest.fn(() => ({
                  attr: jest.fn(() => ({
                    attr: jest.fn(() => ({
                      attr: jest.fn(() => ({
                        on: jest.fn()
                      }))
                    }))
                  }))
                })),
                transition: jest.fn(() => ({
                  duration: jest.fn(() => ({
                    delay: jest.fn(() => ({
                      attr: jest.fn(() => ({
                        attr: jest.fn()
                      }))
                    }))
                  }))
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
          join: jest.fn(() => ({
            attr: jest.fn(() => ({
              attr: jest.fn()
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
        call: jest.fn(),
        style: jest.fn(() => ({
          attr: jest.fn()
        }))
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
        range: jest.fn(() => ({
          nice: jest.fn()
        }))
      })),
      range: jest.fn(() => ({
        nice: jest.fn()
      }))
    })),
    axisBottom: jest.fn(() => ({
      tickValues: jest.fn(() => ({})),
      ticks: jest.fn(() => ({
        tickFormat: jest.fn()
      }))
    })),
    axisLeft: jest.fn(() => ({
      ticks: jest.fn(() => ({
        tickFormat: jest.fn()
      }))
    })),
    line: jest.fn(() => ({
      x: jest.fn(() => ({
        y: jest.fn()
      }))
    })),
    area: jest.fn(() => ({
      x: jest.fn(() => ({
        y0: jest.fn(() => ({
          y1: jest.fn()
        }))
      }))
    })),
    histogram: jest.fn(() => ({
      value: jest.fn(() => ({
        domain: jest.fn(() => ({
          thresholds: jest.fn()
        }))
      }))
    })),
    pointer: jest.fn(() => [100, 100]),
    max: jest.fn(() => 100),
    min: jest.fn(() => 0),
    format: jest.fn(() => jest.fn()),
    easeLinear: jest.fn()
  };
});

// Mock KaTeX rendering
jest.mock('katex', () => ({
  render: jest.fn((formula, container) => {
    container.innerHTML = `<span class="mock-katex">${formula}</span>`;
  })
}));

describe('QualityControlD3 Component', () => {
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
    
    // Set up a mock for clientWidth and clientHeight
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', {
      configurable: true,
      value: 600
    });
    
    Object.defineProperty(HTMLElement.prototype, 'clientHeight', {
      configurable: true,
      value: 300
    });

    // Mock getTotalLength for path elements
    SVGPathElement.prototype.getTotalLength = jest.fn(() => 1000);
  });
  
  test('renders component with parameter controls', () => {
    render(<QualityControlD3 />);
    
    expect(screen.getByText(/Simulation Parameters/i)).toBeInTheDocument();
    expect(screen.getByText(/Target Value \(Mean\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Process Variation \(Std Dev\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Lower Specification Limit/i)).toBeInTheDocument();
    expect(screen.getByText(/Upper Specification Limit/i)).toBeInTheDocument();
    expect(screen.getByText(/Sample Size/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Run Simulation/i })).toBeInTheDocument();
  });
  
  test('shows advanced visualization settings when toggled', async () => {
    render(<QualityControlD3 />);
    
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
  
  test('shows educational content about Normal distribution', () => {
    render(<QualityControlD3 />);
    
    expect(screen.getByText(/Normal Distribution Model/i)).toBeInTheDocument();
    expect(screen.getByText(/The Normal \(Gaussian\) distribution/i)).toBeInTheDocument();
    
    // Check if the LaTeX formula is rendered
    expect(document.querySelector('.mock-katex')).toBeInTheDocument();
    
    // Check if process capability indices info is present
    expect(screen.getByText(/Process Capability Indices/i)).toBeInTheDocument();
    expect(screen.getByText(/Cp = \(USL - LSL\) \/ \(6σ\)/i)).toBeInTheDocument();
  });
  
  test('runs simulation when button is clicked', async () => {
    render(<QualityControlD3 
      setLoading={jest.fn()}
      setError={jest.fn()}
      setSimulationResult={jest.fn()}
    />);
    
    // No simulation data initially
    expect(screen.getByText(/No Simulation Data/i)).toBeInTheDocument();
    
    // Click run simulation button
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    fireEvent.click(runButton);
    
    // Wait for simulation to complete and results to be shown
    await waitFor(() => {
      expect(screen.getByText(/Simulation Results/i)).toBeInTheDocument();
    });
  });
  
  test('can update simulation parameters', () => {
    const setSimulationResult = jest.fn();
    render(<QualityControlD3 
      setLoading={jest.fn()}
      setError={jest.fn()}
      setSimulationResult={setSimulationResult}
    />);
    
    // Find mean slider and change value
    const meanSlider = screen.getByText(/Target Value \(Mean\)/).nextElementSibling;
    fireEvent.change(meanSlider, { target: { value: 110 } });
    
    // Find standard deviation slider and change value
    const stdDevSlider = screen.getByText(/Process Variation \(Std Dev\)/).nextElementSibling;
    fireEvent.change(stdDevSlider, { target: { value: 3 } });
    
    // Find lower spec limit slider and change value
    const lslSlider = screen.getByText(/Lower Specification Limit/).nextElementSibling;
    fireEvent.change(lslSlider, { target: { value: 95 } });
    
    // Find upper spec limit slider and change value
    const uslSlider = screen.getByText(/Upper Specification Limit/).nextElementSibling;
    fireEvent.change(uslSlider, { target: { value: 125 } });
    
    // Find sample size slider and change value
    const sampleSizeSlider = screen.getByText(/Sample Size/).nextElementSibling;
    fireEvent.change(sampleSizeSlider, { target: { value: 50 } });
    
    // Run simulation with new parameters
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    fireEvent.click(runButton);
    
    // Verify simulation was run with new parameters
    expect(setSimulationResult).toHaveBeenCalled();
  });
  
  test('displays process capability indicators correctly', async () => {
    // Create a simulation result with good process capability
    const mockResult = {
      measurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)),
      sortedMeasurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)).sort(),
      capability: {
        empiricalMean: 100.1,
        empiricalStdDev: 2.1,
        cp: 2.38,
        cpk: 2.32,
        defectRate: 0.000035,
        dpmo: 35,
        sigmaLevel: 5.5,
        ucl: 106.4,
        lcl: 93.8
      },
      controlChart: {
        subgroupMeans: [100.2, 99.8, 100.5, 100.1, 99.9, 100.3],
        subgroupRanges: [3.2, 4.1, 3.8, 4.0, 3.5, 3.9],
        meanOfMeans: 100.1,
        meanOfRanges: 3.75,
        xBarUcl: 102.3,
        xBarLcl: 97.9,
        rChartUcl: 7.9,
        rChartLcl: 0
      },
      outOfSpecCount: 0,
      outOfControlCount: 0,
      theoretical: {
        xValues: Array.from({ length: 101 }, (_, i) => 85 + i * 0.3),
        pdfValues: Array.from({ length: 101 }, () => Math.random() * 0.2),
        cdfValues: Array.from({ length: 101 }, (_, i) => i / 100)
      }
    };
    
    // Render with result
    render(
      <QualityControlD3 
        setLoading={jest.fn()}
        setError={jest.fn()}
        setSimulationResult={jest.fn()}
        result={mockResult}
      />
    );
    
    // Success message should be displayed for good capability
    await waitFor(() => {
      expect(screen.getByText(/Process is capable/i)).toBeInTheDocument();
    });
  });
  
  test('shows control chart tabs and can switch between them', async () => {
    // Create a simulation result
    const mockResult = {
      measurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)),
      sortedMeasurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)).sort(),
      capability: {
        empiricalMean: 100.1,
        empiricalStdDev: 2.1,
        cp: 1.2,
        cpk: 1.1,
        defectRate: 0.0012,
        dpmo: 1200,
        sigmaLevel: 4.5,
        ucl: 106.4,
        lcl: 93.8
      },
      controlChart: {
        subgroupMeans: [100.2, 99.8, 100.5, 100.1, 99.9, 100.3],
        subgroupRanges: [3.2, 4.1, 3.8, 4.0, 3.5, 3.9],
        meanOfMeans: 100.1,
        meanOfRanges: 3.75,
        xBarUcl: 102.3,
        xBarLcl: 97.9,
        rChartUcl: 7.9,
        rChartLcl: 0
      },
      outOfSpecCount: 0,
      outOfControlCount: 0,
      theoretical: {
        xValues: Array.from({ length: 101 }, (_, i) => 85 + i * 0.3),
        pdfValues: Array.from({ length: 101 }, () => Math.random() * 0.2),
        cdfValues: Array.from({ length: 101 }, (_, i) => i / 100)
      }
    };
    
    // Render with result
    render(
      <QualityControlD3 
        setLoading={jest.fn()}
        setError={jest.fn()}
        setSimulationResult={jest.fn()}
        result={mockResult}
      />
    );
    
    // X-bar tab should be active initially
    expect(screen.getByRole('tab', { name: /X-bar Chart/i, selected: true })).toBeInTheDocument();
    
    // Switch to R chart tab
    const rChartTab = screen.getByRole('tab', { name: /R Chart/i });
    fireEvent.click(rChartTab);
    
    // R chart tab should be active
    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /R Chart/i, selected: true })).toBeInTheDocument();
    });
  });
  
  test('can reset simulation', async () => {
    const setSimulationResult = jest.fn();
    // Start with a result already set
    const mockResult = {
      measurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)),
      sortedMeasurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)).sort(),
      capability: {
        empiricalMean: 100.1,
        empiricalStdDev: 2.1,
        cp: 1.2,
        cpk: 1.1,
        defectRate: 0.0012,
        dpmo: 1200,
        sigmaLevel: 4.5,
        ucl: 106.4,
        lcl: 93.8
      },
      controlChart: {
        subgroupMeans: [100.2, 99.8, 100.5, 100.1, 99.9, 100.3],
        subgroupRanges: [3.2, 4.1, 3.8, 4.0, 3.5, 3.9],
        meanOfMeans: 100.1,
        meanOfRanges: 3.75,
        xBarUcl: 102.3,
        xBarLcl: 97.9,
        rChartUcl: 7.9,
        rChartLcl: 0
      },
      outOfSpecCount: 0,
      outOfControlCount: 0,
      theoretical: {
        xValues: Array.from({ length: 101 }, (_, i) => 85 + i * 0.3),
        pdfValues: Array.from({ length: 101 }, () => Math.random() * 0.2),
        cdfValues: Array.from({ length: 101 }, (_, i) => i / 100)
      }
    };
    
    render(
      <QualityControlD3 
        setLoading={jest.fn()}
        setError={jest.fn()}
        setSimulationResult={setSimulationResult}
        result={mockResult}
      />
    );
    
    // Simulation results should be visible
    expect(screen.getByText(/Simulation Results/i)).toBeInTheDocument();
    
    // Find and click the reset button
    const resetButton = screen.getByRole('button', { name: /Reset/i });
    fireEvent.click(resetButton);
    
    // setSimulationResult should be called with null to reset
    expect(setSimulationResult).toHaveBeenCalledWith(null);
  });
});