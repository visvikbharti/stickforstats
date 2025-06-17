import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ManufacturingDefectsD3 from '../../../components/probability_distributions/simulations/ManufacturingDefectsD3';

// Mock d3 to avoid issues with SVG rendering in tests
jest.mock('d3', () => ({
  select: jest.fn(() => ({
    selectAll: jest.fn(() => ({
      remove: jest.fn()
    })),
    append: jest.fn(() => ({
      attr: jest.fn(() => ({
        attr: jest.fn(() => ({
          attr: jest.fn(() => ({
            attr: jest.fn(() => ({
              text: jest.fn()
            }))
          }))
        })),
        append: jest.fn(() => ({
          attr: jest.fn(() => ({
            attr: jest.fn(() => ({
              attr: jest.fn(() => ({
                text: jest.fn()
              }))
            }))
          }))
        })),
        style: jest.fn(() => ({
          text: jest.fn()
        })),
        text: jest.fn(),
        call: jest.fn()
      }))
    })),
    transition: jest.fn(() => ({
      duration: jest.fn(() => ({
        ease: jest.fn(() => ({
          attr: jest.fn()
        }))
      }))
    })),
    attr: jest.fn(() => ({
      attr: jest.fn(() => ({
        attr: jest.fn()
      }))
    }))
  })),
  axisBottom: jest.fn(() => ({
    ticks: jest.fn(() => ({
      tickFormat: jest.fn()
    }))
  })),
  axisLeft: jest.fn(() => ({
    ticks: jest.fn(() => ({
      tickFormat: jest.fn()
    }))
  })),
  scaleLinear: jest.fn(() => ({
    domain: jest.fn(() => ({
      range: jest.fn(() => ({
        nice: jest.fn()
      }))
    }))
  })),
  line: jest.fn(() => ({
    x: jest.fn(() => ({
      y: jest.fn()
    })),
    curve: jest.fn()
  })),
  area: jest.fn(() => ({
    x: jest.fn(() => ({
      y0: jest.fn(() => ({
        y1: jest.fn()
      }))
    }))
  })),
  easeLinear: jest.fn(),
  format: jest.fn(() => jest.fn()),
  max: jest.fn(() => 1),
  min: jest.fn(() => 0),
  pointer: jest.fn(() => [0, 0]),
  histogram: jest.fn(() => ({
    domain: jest.fn(() => ({
      thresholds: jest.fn(() => ({
        value: jest.fn()
      }))
    }))
  }))
}));

// Mock katex
jest.mock('katex', () => ({
  render: jest.fn((formula, container) => {
    container.innerHTML = `<span class="katex">${formula}</span>`;
  })
}));

// Create a theme for testing
const theme = createTheme();

// Test props
const defaultProps = {
  projectId: 'test-project',
  setLoading: jest.fn(),
  setError: jest.fn(),
  setSimulationResult: jest.fn(),
  result: null
};

// Mock result data for testing with result
const mockResultData = {
  binomialDist: {
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    pmf: [0.1, 0.2, 0.25, 0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01, 0],
    cdf: [0.1, 0.3, 0.55, 0.75, 0.85, 0.9, 0.94, 0.97, 0.99, 1.0, 1.0]
  },
  multipleTrials: {
    trials: [
      {
        sampleSize: 100,
        numDefects: 3,
        isAccepted: true,
        probability: 0.234,
        producerRisk: 0.05,
        consumerRisk: 0.1,
        defectRate: 0.05,
        acceptanceNumber: 3,
        percentDefective: 3
      }
    ],
    acceptedCount: 1,
    rejectedCount: 0,
    acceptanceRate: 1,
    avgDefects: 3,
    avgDefectRate: 0.03
  },
  ocCurveData: Array.from({ length: 20 }, (_, i) => ({
    defectRate: i * 0.01,
    acceptProb: Math.max(0, 1 - i * 0.1)
  })),
  samplingPlanAnalysis: {
    aql: 0.04,
    aqlAcceptProb: 0.95,
    rql: 0.12,
    iql: 0.08,
    maxAOQ: 0.03,
    maxAOQPoint: 0.06,
    atiData: Array.from({ length: 10 }, (_, i) => ({
      defectRate: i * 0.02,
      ati: 100 + i * 50
    }))
  },
  parameters: {
    defectRate: 0.05,
    sampleSize: 100,
    acceptanceNumber: 3,
    batchSize: 1000,
    aqlLevel: 0.04,
    trials: 1
  }
};

describe('ManufacturingDefectsD3 Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} />
      </ThemeProvider>
    );
    
    expect(screen.getByText('Sampling Plan Parameters')).toBeInTheDocument();
  });

  test('renders sliders for all parameters', () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} />
      </ThemeProvider>
    );
    
    // Check for parameter labels
    expect(screen.getByText(/Defect Rate \(p\)/)).toBeInTheDocument();
    expect(screen.getByText(/Total Batch Size/)).toBeInTheDocument();
    expect(screen.getByText(/Sample Size \(n\)/)).toBeInTheDocument();
    expect(screen.getByText(/Acceptance Number \(c\)/)).toBeInTheDocument();
    expect(screen.getByText(/Acceptable Quality Level/)).toBeInTheDocument();
  });

  test('run simulation button calls the simulation function', async () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} />
      </ThemeProvider>
    );
    
    const runButton = screen.getByText('Run Simulation');
    fireEvent.click(runButton);
    
    await waitFor(() => {
      expect(defaultProps.setLoading).toHaveBeenCalledWith(true);
      expect(defaultProps.setLoading).toHaveBeenCalledWith(false);
      expect(defaultProps.setSimulationResult).toHaveBeenCalled();
    });
  });

  test('renders educational content about manufacturing quality control', () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} />
      </ThemeProvider>
    );
    
    expect(screen.getByText('Manufacturing Quality Control')).toBeInTheDocument();
    expect(screen.getByText(/Acceptance sampling uses statistical methods/)).toBeInTheDocument();
    expect(screen.getByText('Binomial Probability Mass Function:')).toBeInTheDocument();
  });

  test('renders visualization settings controls', () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} />
      </ThemeProvider>
    );
    
    const settingsButton = screen.getByText('Show Visualization Settings');
    fireEvent.click(settingsButton);
    
    expect(screen.getByText('Show Animations')).toBeInTheDocument();
    expect(screen.getByText('Show Data Points')).toBeInTheDocument();
    expect(screen.getByText('Show Legend')).toBeInTheDocument();
  });

  test('renders results when simulation data is provided', () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} result={mockResultData} />
      </ThemeProvider>
    );
    
    expect(screen.getByText('Sampling Plan Analysis')).toBeInTheDocument();
    expect(screen.getByText('Plan Performance:')).toBeInTheDocument();
    expect(screen.getByText('Quality Levels:')).toBeInTheDocument();
    expect(screen.getByText(/AQL Accept Probability:/)).toBeInTheDocument();
    expect(screen.getByText(/Producer's Risk:/)).toBeInTheDocument();
    expect(screen.getByText(/Consumer's Risk:/)).toBeInTheDocument();
  });

  test('renders tabs for different visualizations', () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} result={mockResultData} />
      </ThemeProvider>
    );
    
    expect(screen.getByRole('tab', { name: 'Inspection Results' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'OC Curve' })).toBeInTheDocument();
    
    // Click on the OC Curve tab
    fireEvent.click(screen.getByRole('tab', { name: 'OC Curve' }));
    
    // Check if insights text changes
    expect(screen.getByText(/The OC Curve shows how the sampling plan performs/)).toBeInTheDocument();
  });

  test('reset button clears simulation results', () => {
    render(
      <ThemeProvider theme={theme}>
        <ManufacturingDefectsD3 {...defaultProps} result={mockResultData} />
      </ThemeProvider>
    );
    
    const resetButton = screen.getByText('Reset');
    fireEvent.click(resetButton);
    
    expect(defaultProps.setSimulationResult).toHaveBeenCalledWith(null);
  });
});