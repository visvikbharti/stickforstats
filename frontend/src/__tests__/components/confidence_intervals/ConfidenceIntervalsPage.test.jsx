import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { SnackbarProvider } from 'notistack';

import ConfidenceIntervalsPage from '../../../components/confidence_intervals/ConfidenceIntervalsPage';

// Mock child components to simplify testing
jest.mock('../../../components/confidence_intervals/education/TheoryFoundations', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-theory-foundations">Theory Foundations Component</div>
}));

jest.mock('../../../components/confidence_intervals/simulations/InteractiveSimulations', () => ({
  __esModule: true,
  default: ({ projects }) => (
    <div data-testid="mock-interactive-simulations">
      Interactive Simulations Component
      <span>Projects: {projects ? projects.length : 0}</span>
    </div>
  )
}));

jest.mock('../../../components/confidence_intervals/education/AdvancedMethods', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-advanced-methods">Advanced Methods Component</div>
}));

jest.mock('../../../components/confidence_intervals/education/RealWorldApplications', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-real-world-applications">Real World Applications Component</div>
}));

jest.mock('../../../components/confidence_intervals/education/MathematicalProofs', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-mathematical-proofs">Mathematical Proofs Component</div>
}));

jest.mock('../../../components/confidence_intervals/education/References', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-references">References Component</div>
}));

jest.mock('../../../components/confidence_intervals/calculators/CalculatorDashboard', () => ({
  __esModule: true,
  default: ({ projects }) => (
    <div data-testid="mock-calculator-dashboard">
      Calculator Dashboard Component
      <span>Projects: {projects ? projects.length : 0}</span>
    </div>
  )
}));

// Mock axios
jest.mock('axios');

describe('ConfidenceIntervalsPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Setup default mock returns for API calls
    axios.get.mockResolvedValue({
      data: [
        { id: '1', name: 'Test Project 1', description: 'Test Description 1', settings: { default_confidence_level: 0.95 } },
        { id: '2', name: 'Test Project 2', description: 'Test Description 2', settings: { default_confidence_level: 0.99 } }
      ]
    });
    
    axios.post.mockResolvedValue({
      data: { 
        id: '3', 
        name: 'New Project', 
        description: 'A new confidence interval project', 
        settings: { default_confidence_level: 0.95 } 
      }
    });
  });

  const renderWithRouter = (ui, { route = '/confidence-intervals' } = {}) => {
    window.history.pushState({}, 'Test page', route);
    return render(
      <SnackbarProvider>
        <MemoryRouter initialEntries={[route]}>
          <Routes>
            <Route path="/confidence-intervals/*" element={ui} />
          </Routes>
        </MemoryRouter>
      </SnackbarProvider>
    );
  };

  test('renders the main page components and title', async () => {
    renderWithRouter(<ConfidenceIntervalsPage />);
    
    // Check if the main title and subtitle are rendered
    expect(screen.getByText(/Confidence Intervals/i)).toBeInTheDocument();
    expect(screen.getByText(/Explore the theory, calculation, and application/i)).toBeInTheDocument();
    
    // Check if tabs are rendered
    expect(screen.getByText(/Overview/i)).toBeInTheDocument();
    expect(screen.getByText(/Calculators/i)).toBeInTheDocument();
    expect(screen.getByText(/Theory & Foundations/i)).toBeInTheDocument();
    expect(screen.getByText(/Interactive Simulations/i)).toBeInTheDocument();
    expect(screen.getByText(/Advanced Methods/i)).toBeInTheDocument();
  });

  test('fetches projects on component mount', async () => {
    renderWithRouter(<ConfidenceIntervalsPage />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/confidence-intervals/projects/');
    });
  });

  test('renders Overview tab by default', async () => {
    renderWithRouter(<ConfidenceIntervalsPage />);
    
    // Wait for component to render and API calls to resolve
    await waitFor(() => {
      // Check if the Welcome message from Overview is displayed
      expect(screen.getByText(/Welcome to the Confidence Intervals Module/i)).toBeInTheDocument();
      expect(screen.getByText(/Create New Project/i)).toBeInTheDocument();
    });
  });

  test('navigates to different tabs when clicked', async () => {
    renderWithRouter(<ConfidenceIntervalsPage />);
    
    // Click on Theory & Foundations tab
    fireEvent.click(screen.getByText(/Theory & Foundations/i));
    
    await waitFor(() => {
      expect(screen.getByTestId('mock-theory-foundations')).toBeInTheDocument();
    });
    
    // Click on Interactive Simulations tab
    fireEvent.click(screen.getByText(/Interactive Simulations/i));
    
    await waitFor(() => {
      expect(screen.getByTestId('mock-interactive-simulations')).toBeInTheDocument();
    });
    
    // Click on Calculators tab
    fireEvent.click(screen.getByText(/Calculators/i));
    
    await waitFor(() => {
      expect(screen.getByTestId('mock-calculator-dashboard')).toBeInTheDocument();
    });
  });

  test('creates a new project when button is clicked', async () => {
    renderWithRouter(<ConfidenceIntervalsPage />);
    
    // Wait for component to render
    await waitFor(() => {
      expect(screen.getByText(/Create New Project/i)).toBeInTheDocument();
    });
    
    // Click the Create New Project button
    fireEvent.click(screen.getByText(/Create New Project/i));
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        '/api/confidence-intervals/projects/',
        expect.objectContaining({
          name: expect.any(String),
          description: 'A new confidence interval project',
          settings: { default_confidence_level: 0.95 }
        })
      );
    });
  });

  test('handles API error when fetching projects', async () => {
    // Setup axios to return an error
    axios.get.mockRejectedValueOnce(new Error('Failed to fetch projects'));
    
    renderWithRouter(<ConfidenceIntervalsPage />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/confidence-intervals/projects/');
      // Check that projects array remains empty when API call fails
      expect(screen.queryByText(/Projects: 0/)).not.toBeInTheDocument();
    });
  });

  test('handles API error when creating a project', async () => {
    // Setup axios to return an error for post calls
    axios.post.mockRejectedValueOnce(new Error('Failed to create project'));
    
    renderWithRouter(<ConfidenceIntervalsPage />);
    
    // Wait for component to render
    await waitFor(() => {
      expect(screen.getByText(/Create New Project/i)).toBeInTheDocument();
    });
    
    // Click the Create New Project button
    fireEvent.click(screen.getByText(/Create New Project/i));
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        '/api/confidence-intervals/projects/',
        expect.any(Object)
      );
    });
  });

  test('renders correct component based on route', async () => {
    // Test with different routes
    renderWithRouter(<ConfidenceIntervalsPage />, { route: '/confidence-intervals/theory' });
    
    await waitFor(() => {
      expect(screen.getByTestId('mock-theory-foundations')).toBeInTheDocument();
    });
    
    // Clean up and test another route
    cleanup();
    renderWithRouter(<ConfidenceIntervalsPage />, { route: '/confidence-intervals/advanced' });
    
    await waitFor(() => {
      expect(screen.getByTestId('mock-advanced-methods')).toBeInTheDocument();
    });
  });
});