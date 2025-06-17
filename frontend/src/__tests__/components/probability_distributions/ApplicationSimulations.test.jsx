import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SnackbarProvider } from 'notistack';
import ApplicationSimulations from '../../../components/probability_distributions/ApplicationSimulations';

// Mock the simulation components
jest.mock('../../../components/probability_distributions/simulations', () => ({
  EmailArrivalsD3: jest.fn(({ setLoading, setError, setSimulationResult }) => {
    const handleRunSimulation = () => {
      setLoading(true);
      setTimeout(() => {
        setSimulationResult({
          hourly_arrivals: [20, 18, 22, 19, 21, 23, 17, 20],
          total_arrivals: 160,
          k_values: Array.from({ length: 300 }, (_, i) => i),
          theoretical_pmf: Array.from({ length: 300 }, () => 0.005),
          theoretical_cdf: Array.from({ length: 300 }, (_, i) => i / 300),
          observed_pmf: Array.from({ length: 300 }, () => 0),
          daily_rate: 160,
          exceeds_capacity: false
        });
        setLoading(false);
      }, 50);
    };
    
    return (
      <div>
        <div>Arrivals follow a Poisson distribution</div>
        {setSimulationResult && (
          <>
            {setSimulationResult.result ? (
              <div>Simulation Results</div>
            ) : (
              <button onClick={handleRunSimulation}>Run Simulation</button>
            )}
          </>
        )}
      </div>
    );
  }),
  
  QualityControlD3: jest.fn(({ setLoading, setError, setSimulationResult }) => {
    const handleRunSimulation = () => {
      setLoading(true);
      setTimeout(() => {
        setSimulationResult({
          measurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)),
          sortedMeasurements: Array.from({ length: 30 }, () => 100 + (Math.random() * 4 - 2)).sort(),
          capability: {
            empiricalMean: 100.1,
            empiricalStdDev: 2.1,
            cp: 1.33,
            cpk: 1.2,
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
          }
        });
        setLoading(false);
      }, 50);
    };
    
    return (
      <div>
        <div>Process Capability Analysis</div>
        {setSimulationResult && (
          <>
            {setSimulationResult.result ? (
              <div>Process Capability</div>
            ) : (
              <button onClick={handleRunSimulation}>Run Simulation</button>
            )}
          </>
        )}
      </div>
    );
  })
}));

// Helper to render with SnackbarProvider
const renderWithSnackbar = (ui) => {
  return render(
    <SnackbarProvider maxSnack={3}>
      {ui}
    </SnackbarProvider>
  );
};

describe('ApplicationSimulations Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders the main component with simulation categories', () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    expect(screen.getByText(/Real-world Applications/i)).toBeInTheDocument();
    expect(screen.getByText(/Email Arrivals/i)).toBeInTheDocument();
    expect(screen.getByText(/Quality Control/i)).toBeInTheDocument();
    expect(screen.getByText(/Clinical Trials/i)).toBeInTheDocument();
    expect(screen.getByText(/Network Traffic/i)).toBeInTheDocument();
    expect(screen.getByText(/Manufacturing Defects/i)).toBeInTheDocument();
  });

  test('selects a simulation when clicking on a category card', () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Initial state should not show any simulation content
    expect(screen.queryByText(/Arrivals follow a Poisson distribution/i)).not.toBeInTheDocument();
    
    // Click on Email Arrivals card
    fireEvent.click(screen.getByText(/Email Arrivals/i));
    
    // Should now display email simulation content
    expect(screen.getByText(/Arrivals follow a Poisson distribution/i)).toBeInTheDocument();
  });

  test('runs Email Arrivals simulation when button is clicked', async () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Select Email Arrivals simulation
    fireEvent.click(screen.getByText(/Email Arrivals/i));
    
    // Find and click the Run Simulation button
    const runButton = screen.getByText(/Run Simulation/i);
    fireEvent.click(runButton);
    
    // Loading indicator should appear
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Results should be displayed after loading
    await waitFor(() => {
      expect(screen.getByText(/Simulation Results/i)).toBeInTheDocument();
    });
  });

  test('selects and runs Quality Control simulation', async () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Select Quality Control simulation
    fireEvent.click(screen.getByText(/Quality Control/i));
    
    // Should display quality control content
    expect(screen.getByText(/Process Capability Analysis/i)).toBeInTheDocument();
    
    // Find and click the Run Simulation button
    const runButton = screen.getByText(/Run Simulation/i);
    fireEvent.click(runButton);
    
    // Loading indicator should appear
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Results should be displayed after loading
    await waitFor(() => {
      expect(screen.getByText(/Process Capability/i)).toBeInTheDocument();
    });
  });

  test('shows placeholder for Clinical Trials simulation', () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Select Clinical Trials simulation
    fireEvent.click(screen.getByText(/Clinical Trials/i));
    
    // Should display placeholder content
    expect(screen.getByText(/This simulation is being enhanced/i)).toBeInTheDocument();
    expect(screen.getByText(/Clinical Trials Simulation/i)).toBeInTheDocument();
  });

  test('shows placeholder for Network Traffic simulation', () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Select Network Traffic simulation
    fireEvent.click(screen.getByText(/Network Traffic/i));
    
    // Should display placeholder content
    expect(screen.getByText(/This simulation is being enhanced/i)).toBeInTheDocument();
    expect(screen.getByText(/Network Traffic Simulation/i)).toBeInTheDocument();
  });

  test('shows placeholder for Manufacturing Defects simulation', () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Select Manufacturing Defects simulation
    fireEvent.click(screen.getByText(/Manufacturing Defects/i));
    
    // Should display placeholder content
    expect(screen.getByText(/This simulation is being enhanced/i)).toBeInTheDocument();
    expect(screen.getByText(/Manufacturing Defects Simulation/i)).toBeInTheDocument();
  });

  test('can navigate back to application list', async () => {
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Select Email Arrivals simulation
    fireEvent.click(screen.getByText(/Email Arrivals/i));
    
    // Should now display email simulation content
    expect(screen.getByText(/Arrivals follow a Poisson distribution/i)).toBeInTheDocument();
    
    // Go back to the list
    fireEvent.click(screen.getByText(/Back to Applications/i));
    
    // Should show application cards again
    expect(screen.getAllByText(/Explore/).length).toBeGreaterThan(1);
    expect(screen.queryByText(/Arrivals follow a Poisson distribution/i)).not.toBeInTheDocument();
  });

  test('error is displayed when simulation fails', async () => {
    // Replace one of the mock implementations to trigger an error
    jest.mock('../../../components/probability_distributions/simulations', () => ({
      ...jest.requireActual('../../../components/probability_distributions/simulations'),
      EmailArrivalsD3: jest.fn(({ setLoading, setError, setSimulationResult }) => {
        const handleRunSimulation = () => {
          setLoading(true);
          setTimeout(() => {
            setError('Error in simulation');
            setLoading(false);
          }, 50);
        };
        
        return (
          <div>
            <div>Arrivals follow a Poisson distribution</div>
            <button onClick={handleRunSimulation}>Run Simulation</button>
          </div>
        );
      })
    }));
    
    renderWithSnackbar(<ApplicationSimulations projectId={1} />);
    
    // Select Email Arrivals simulation
    fireEvent.click(screen.getByText(/Email Arrivals/i));
    
    // Find and click the Run Simulation button
    const runButton = screen.getByText(/Run Simulation/i);
    fireEvent.click(runButton);
    
    // Error should be displayed
    await waitFor(() => {
      expect(screen.getByText(/Error in simulation/i)).toBeInTheDocument();
    });
  });
});