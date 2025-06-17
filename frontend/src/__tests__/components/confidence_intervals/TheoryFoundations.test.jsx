import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import TheoryFoundations from '../../../components/confidence_intervals/education/TheoryFoundations';

// Mock dependencies
jest.mock('axios');
jest.mock('react-mathjax', () => ({
  Provider: ({ children }) => <div data-testid="mathjax-provider">{children}</div>,
  Node: ({ children, formula }) => (
    <div data-testid="mathjax-formula">
      {formula || children}
    </div>
  )
}));

jest.mock('../../../components/confidence_intervals/visualizations/CoverageAnimation', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-coverage-animation">Coverage Animation</div>
}));

jest.mock('../../../components/confidence_intervals/visualizations/IntervalConstructionAnimation', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-interval-construction-animation">Interval Construction Animation</div>
}));

describe('TheoryFoundations Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock the API call for educational content
    axios.get.mockResolvedValue({
      data: [
        {
          id: 1,
          title: 'Additional Topic: Bootstrapping',
          content: '\\text{This is an example of bootstrapping content with math: } \\hat{\\theta} = f(X_1, X_2, \\ldots, X_n)'
        },
        {
          id: 2,
          title: 'Advanced Concepts: Pivotal Quantities',
          content: '\\text{A pivotal quantity } Q(X, \\theta) \\text{ has a distribution that does not depend on the parameter } \\theta'
        }
      ]
    });
  });
  
  test('renders the title and description', async () => {
    render(<TheoryFoundations />);
    
    expect(screen.getByText(/Theoretical Foundations of Confidence Intervals/i)).toBeInTheDocument();
    expect(screen.getByText(/This section explores the fundamental concepts/i)).toBeInTheDocument();
  });
  
  test('shows loading state initially', () => {
    render(<TheoryFoundations />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
  
  test('fetches educational content on mount', async () => {
    render(<TheoryFoundations />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/confidence-intervals/educational/?section=FUNDAMENTALS');
    });
  });
  
  test('renders key sections after loading', async () => {
    render(<TheoryFoundations />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check for main sections
    expect(screen.getByText(/What is a Confidence Interval?/i)).toBeInTheDocument();
    expect(screen.getByText(/The General Formulation/i)).toBeInTheDocument();
    expect(screen.getByText(/Common Types of Confidence Intervals/i)).toBeInTheDocument();
    expect(screen.getByText(/Correct Interpretation of Confidence Intervals/i)).toBeInTheDocument();
    expect(screen.getByText(/Factors Affecting Confidence Interval Width/i)).toBeInTheDocument();
    expect(screen.getByText(/Confidence Intervals and Hypothesis Testing/i)).toBeInTheDocument();
  });
  
  test('renders MathJax formulas properly', async () => {
    render(<TheoryFoundations />);
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check for MathJax provider
    expect(screen.getByTestId('mathjax-provider')).toBeInTheDocument();
    
    // Check for MathJax formulas
    const mathFormulas = screen.getAllByTestId('mathjax-formula');
    expect(mathFormulas.length).toBeGreaterThan(0);
    
    // Check one specific formula
    expect(screen.getByTestId('mathjax-formula', { name: /Point Estimate/i })).toBeInTheDocument();
  });
  
  test('renders visualization components', async () => {
    render(<TheoryFoundations />);
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check for animation components
    expect(screen.getByTestId('mock-coverage-animation')).toBeInTheDocument();
    expect(screen.getByTestId('mock-interval-construction-animation')).toBeInTheDocument();
  });
  
  test('renders fetched educational content', async () => {
    render(<TheoryFoundations />);
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check for the fetched content titles
    expect(screen.getByText(/Additional Topic: Bootstrapping/i)).toBeInTheDocument();
    expect(screen.getByText(/Advanced Concepts: Pivotal Quantities/i)).toBeInTheDocument();
    
    // Check that the content is rendered with MathJax
    const mathFormulas = screen.getAllByTestId('mathjax-formula');
    const bootstrappingFormula = mathFormulas.find(formula => 
      formula.textContent.includes('This is an example of bootstrapping content with math')
    );
    expect(bootstrappingFormula).toBeInTheDocument();
  });
  
  test('handles API error gracefully', async () => {
    // Mock API error
    axios.get.mockRejectedValueOnce(new Error('Failed to fetch'));
    
    render(<TheoryFoundations />);
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Component should still render main content
    expect(screen.getByText(/What is a Confidence Interval?/i)).toBeInTheDocument();
    
    // But fetched content should be empty
    expect(screen.queryByText(/Additional Topic: Bootstrapping/i)).not.toBeInTheDocument();
  });
  
  test('accordion expansions work properly', async () => {
    render(<TheoryFoundations />);
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // First accordion (Confidence Interval for a Population Mean (Known Variance)) should be expanded by default
    expect(screen.getByText(/When the population variance/i)).toBeInTheDocument();
    
    // Second accordion should start collapsed (content not visible)
    expect(screen.queryByText(/When the population variance is unknown/i)).not.toBeInTheDocument();
  });
});