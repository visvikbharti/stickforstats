// Jest DOM setup
import '@testing-library/jest-dom';

// Mock MathJax
jest.mock('better-react-mathjax', () => ({
  MathJax: ({ children }) => <div data-testid="mathjax">{children}</div>,
  MathJaxContext: ({ children }) => <div>{children}</div>
}));

// Mock Chart.js
jest.mock('chart.js', () => ({
  Chart: jest.fn(),
  registerables: [],
  register: jest.fn(),
  CategoryScale: jest.fn(),
  LinearScale: jest.fn(),
  PointElement: jest.fn(),
  LineElement: jest.fn(),
  BarElement: jest.fn(),
  Title: jest.fn(),
  Tooltip: jest.fn(),
  Legend: jest.fn(),
  Filler: jest.fn()
}));

jest.mock('react-chartjs-2', () => ({
  Line: ({ data, options }) => (
    <div data-testid="chart-line" data-data={JSON.stringify(data)} data-options={JSON.stringify(options)}>
      Chart
    </div>
  ),
  Bar: ({ data, options }) => (
    <div data-testid="chart-bar" data-data={JSON.stringify(data)} data-options={JSON.stringify(options)}>
      Chart
    </div>
  )
}));

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} }))
}));

// Global mocks for window objects that may not exist in the test environment
global.URL.createObjectURL = jest.fn();
global.URL.revokeObjectURL = jest.fn();

// Suppress React 18 console errors related to act warnings
const originalError = console.error;
console.error = (...args) => {
  if (/Warning.*not wrapped in act/.test(args[0])) {
    return;
  }
  originalError.call(console, ...args);
};