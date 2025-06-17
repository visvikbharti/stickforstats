import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import ClinicalTrialD3 from '../../../components/probability_distributions/simulations/ClinicalTrialD3';

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
        })),
        transition: jest.fn(() => ({
          duration: jest.fn(() => ({
            ease: jest.fn(() => ({
              attr: jest.fn()
            }))
          }))
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
      })),
      domain: jest.fn(() => ({
        thresholds: jest.fn()
      }))
    })),
    pointer: jest.fn(() => [100, 100]),
    max: jest.fn(() => 100),
    min: jest.fn(() => 0),
    mean: jest.fn(() => 0.2),
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

describe('ClinicalTrialD3 Component', () => {
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
    render(<ClinicalTrialD3 />);
    
    expect(screen.getByText(/Trial Parameters/i)).toBeInTheDocument();
    expect(screen.getByText(/Control Group Success Rate/i)).toBeInTheDocument();
    expect(screen.getByText(/Treatment Effect/i)).toBeInTheDocument();
    expect(screen.getByText(/Sample Size/i)).toBeInTheDocument();
    expect(screen.getByText(/Significance Level/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Run Simulation/i })).toBeInTheDocument();
  });
  
  test('shows advanced visualization settings when toggled', async () => {
    render(<ClinicalTrialD3 />);
    
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
  
  test('shows educational content about clinical trials', () => {
    render(<ClinicalTrialD3 />);
    
    expect(screen.getByText(/Clinical Trial Basics/i)).toBeInTheDocument();
    expect(screen.getByText(/Clinical trials use statistical methods/i)).toBeInTheDocument();
    
    // Check if the LaTeX formula is rendered
    expect(document.querySelector('.mock-katex')).toBeInTheDocument();
    
    // Check if power and significance level info is present
    expect(screen.getByText(/Key Clinical Trial Concepts/i)).toBeInTheDocument();
    expect(screen.getByText(/Power/i)).toBeInTheDocument();
    expect(screen.getByText(/Significance Level/i)).toBeInTheDocument();
  });
  
  test('runs simulation when button is clicked', async () => {
    const setSimulationResult = jest.fn();
    render(<ClinicalTrialD3 
      setLoading={jest.fn()}
      setError={jest.fn()}
      setSimulationResult={setSimulationResult}
    />);
    
    // No simulation data initially
    expect(screen.getByText(/No Simulation Data/i)).toBeInTheDocument();
    
    // Click run simulation button
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    fireEvent.click(runButton);
    
    // Verify simulation was run
    expect(setSimulationResult).toHaveBeenCalled();
  });
  
  test('can update simulation parameters', () => {
    const setSimulationResult = jest.fn();
    render(<ClinicalTrialD3 
      setLoading={jest.fn()}
      setError={jest.fn()}
      setSimulationResult={setSimulationResult}
    />);
    
    // Find control success rate slider and change value
    const controlSuccessSlider = screen.getByText(/Control Group Success Rate/).nextElementSibling;
    fireEvent.change(controlSuccessSlider, { target: { value: 40 } });
    
    // Find treatment effect slider and change value
    const treatmentEffectSlider = screen.getByText(/Treatment Effect/).nextElementSibling;
    fireEvent.change(treatmentEffectSlider, { target: { value: 15 } });
    
    // Find sample size slider and change value
    const sampleSizeSlider = screen.getByText(/Sample Size/).nextElementSibling;
    fireEvent.change(sampleSizeSlider, { target: { value: 100 } });
    
    // Find significance level slider and change value
    const alphaSlider = screen.getByText(/Significance Level/).nextElementSibling;
    fireEvent.change(alphaSlider, { target: { value: 1 } });
    
    // Run simulation with new parameters
    const runButton = screen.getByRole('button', { name: /Run Simulation/i });
    fireEvent.click(runButton);
    
    // Verify simulation was run with new parameters
    expect(setSimulationResult).toHaveBeenCalled();
  });
  
  test('displays simulation results correctly', async () => {
    // Create a mock result
    const mockResult = {
      trialResults: [{
        controlGroup: {
          size: 50,
          successes: 15,
          proportion: 0.3
        },
        treatmentGroup: {
          size: 50,
          successes: 25,
          proportion: 0.5
        },
        testResults: {
          proportion1: 0.3,
          proportion2: 0.5,
          difference: 0.2,
          zScore: 2.1,
          pValue: 0.03,
          significant: true,
          confidenceInterval: [0.05, 0.35]
        }
      }],
      powerAnalysis: {
        power: 0.85,
        differenceDistribution: Array(1000).fill(0.2),
        pValueDistribution: Array(1000).fill(0.03),
        numTrials: 1000,
        significantTrials: 850
      },
      theoreticalDistributions: {
        control: {
          values: Array.from({ length: 51 }, (_, i) => i),
          pmf: Array.from({ length: 51 }, () => 0.02),
          cdf: Array.from({ length: 51 }, (_, i) => i / 50)
        },
        treatment: {
          values: Array.from({ length: 51 }, (_, i) => i),
          pmf: Array.from({ length: 51 }, () => 0.02),
          cdf: Array.from({ length: 51 }, (_, i) => i / 50)
        }
      },
      theoreticalPower: 0.85,
      parameters: {
        controlSuccess: 0.3,
        treatmentSuccess: 0.5,
        sampleSize: 50,
        alpha: 0.05,
        effect: 0.2
      },
      summary: {
        numTrials: 1,
        significantTrials: 1,
        significantProportion: 1,
        largerTreatmentEffect: 1,
        largerTreatmentProportion: 1,
        avgControlProportion: 0.3,
        avgTreatmentProportion: 0.5
      }
    };
    
    render(
      <ClinicalTrialD3 
        setLoading={jest.fn()}
        setError={jest.fn()}
        setSimulationResult={jest.fn()}
        result={mockResult}
      />
    );
    
    // Results should be displayed
    expect(screen.getByText(/Simulation Results/i)).toBeInTheDocument();
    expect(screen.getByText(/First Trial Outcome/i)).toBeInTheDocument();
    expect(screen.getByText(/Statistical Power Analysis/i)).toBeInTheDocument();
    
    // Check specific values
    expect(screen.getByText(/Control: 15\/50/i)).toBeInTheDocument();
    expect(screen.getByText(/Treatment: 25\/50/i)).toBeInTheDocument();
    expect(screen.getByText(/Difference: 20\.0%/i)).toBeInTheDocument();
    expect(screen.getByText(/p-value: 0\.0300/i)).toBeInTheDocument();
    expect(screen.getByText(/Theoretical Power: 85\.0%/i)).toBeInTheDocument();
  });
  
  test('shows power analysis tab when selected', async () => {
    // Create a mock result
    const mockResult = {
      trialResults: [{
        controlGroup: { size: 50, successes: 15, proportion: 0.3 },
        treatmentGroup: { size: 50, successes: 25, proportion: 0.5 },
        testResults: {
          proportion1: 0.3, proportion2: 0.5, difference: 0.2,
          zScore: 2.1, pValue: 0.03, significant: true,
          confidenceInterval: [0.05, 0.35]
        }
      }],
      powerAnalysis: {
        power: 0.85,
        differenceDistribution: Array(1000).fill(0.2),
        pValueDistribution: Array(1000).fill(0.03),
        numTrials: 1000,
        significantTrials: 850
      },
      theoreticalDistributions: {
        control: {
          values: Array.from({ length: 51 }, (_, i) => i),
          pmf: Array.from({ length: 51 }, () => 0.02),
          cdf: Array.from({ length: 51 }, (_, i) => i / 50)
        },
        treatment: {
          values: Array.from({ length: 51 }, (_, i) => i),
          pmf: Array.from({ length: 51 }, () => 0.02),
          cdf: Array.from({ length: 51 }, (_, i) => i / 50)
        }
      },
      theoreticalPower: 0.85,
      parameters: {
        controlSuccess: 0.3, treatmentSuccess: 0.5,
        sampleSize: 50, alpha: 0.05, effect: 0.2
      },
      summary: {
        numTrials: 1, significantTrials: 1, significantProportion: 1,
        largerTreatmentEffect: 1, largerTreatmentProportion: 1,
        avgControlProportion: 0.3, avgTreatmentProportion: 0.5
      }
    };
    
    render(
      <ClinicalTrialD3 
        setLoading={jest.fn()}
        setError={jest.fn()}
        setSimulationResult={jest.fn()}
        result={mockResult}
      />
    );
    
    // Trial Results tab should be active by default
    expect(screen.getByRole('tab', { name: /Trial Results/i, selected: true })).toBeInTheDocument();
    
    // Switch to Power Analysis tab
    const powerTab = screen.getByRole('tab', { name: /Power Analysis/i });
    fireEvent.click(powerTab);
    
    // Power Analysis tab should now be active
    expect(screen.getByRole('tab', { name: /Power Analysis/i, selected: true })).toBeInTheDocument();
    
    // Should show power analysis content
    await waitFor(() => {
      expect(screen.getByText(/how statistical power increases with sample size/i)).toBeInTheDocument();
    });
  });
  
  test('can reset simulation', async () => {
    const setSimulationResult = jest.fn();
    // Create a mock result
    const mockResult = {
      trialResults: [{
        controlGroup: { size: 50, successes: 15, proportion: 0.3 },
        treatmentGroup: { size: 50, successes: 25, proportion: 0.5 },
        testResults: {
          proportion1: 0.3, proportion2: 0.5, difference: 0.2,
          zScore: 2.1, pValue: 0.03, significant: true,
          confidenceInterval: [0.05, 0.35]
        }
      }],
      powerAnalysis: {
        power: 0.85,
        differenceDistribution: Array(1000).fill(0.2),
        pValueDistribution: Array(1000).fill(0.03),
        numTrials: 1000,
        significantTrials: 850
      },
      theoreticalDistributions: {
        control: {
          values: Array.from({ length: 51 }, (_, i) => i),
          pmf: Array.from({ length: 51 }, () => 0.02),
          cdf: Array.from({ length: 51 }, (_, i) => i / 50)
        },
        treatment: {
          values: Array.from({ length: 51 }, (_, i) => i),
          pmf: Array.from({ length: 51 }, () => 0.02),
          cdf: Array.from({ length: 51 }, (_, i) => i / 50)
        }
      },
      theoreticalPower: 0.85,
      parameters: {
        controlSuccess: 0.3, treatmentSuccess: 0.5,
        sampleSize: 50, alpha: 0.05, effect: 0.2
      },
      summary: {
        numTrials: 1, significantTrials: 1, significantProportion: 1,
        largerTreatmentEffect: 1, largerTreatmentProportion: 1,
        avgControlProportion: 0.3, avgTreatmentProportion: 0.5
      }
    };
    
    render(
      <ClinicalTrialD3 
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