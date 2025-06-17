# StickForStats Frontend

This is the frontend for the StickForStats application, a comprehensive statistical analysis platform designed for scientists and engineers.

## Overview

StickForStats provides a user-friendly interface to interact with various statistical modules, making advanced statistical analysis accessible to professionals across fields.

## Available Modules

1. **Confidence Intervals** - Statistical estimation with interactive confidence interval analysis tools
2. **Probability Distributions** - Visualization and analysis of standard probability distributions
3. **PCA Analysis** - Principal Component Analysis for high-dimensional data
4. **DOE Analysis** - Design of Experiments for experimental design and analysis
5. **SQC Analysis** - Statistical Quality Control for process monitoring and control
6. **RAG System** - Retrieval Augmented Generation for statistical assistance
7. **Reports** - Generation and management of statistical reports
8. **Workflows** - Creation and execution of analysis workflows

## Getting Started

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:

```bash
npm install
# or
yarn install
```

### Development

To start the development server:

```bash
npm start
# or
yarn start
```

This will start the development server at http://localhost:3000.

### Building for Production

To build the application for production:

```bash
npm run build
# or
yarn build
```

This will create a production-ready build in the `build` directory.

## Environment Configuration

The application uses environment-specific configuration through `.env` files:

- `.env.development` - Development environment settings
- `.env.production` - Production environment settings

These files contain configurations for:
- API endpoints
- WebSocket connections
- Feature flags
- Authentication settings
- Performance parameters

Example configuration:
```
# API Configuration
REACT_APP_API_URL=https://api.stickforstats.com
REACT_APP_WEBSOCKET_URL=wss://api.stickforstats.com

# Feature Flags
REACT_APP_ENABLE_DEBUG_MODE=false
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_EXPERIMENTAL_FEATURES=false

# Authentication
REACT_APP_TOKEN_EXPIRATION_DAYS=7
REACT_APP_AUTH_PROVIDER=default

# Performance
REACT_APP_MAX_CONCURRENT_REQUESTS=5
REACT_APP_BATCH_SIZE=50
```

## Project Structure

- `src/` - Source code
  - `assets/` - Static assets (images, icons, etc.)
  - `components/` - React components
    - `confidence_intervals/` - Confidence Intervals module components
    - `probability_distributions/` - Probability Distributions module components
    - `pca/` - PCA Analysis module components
    - `doe/` - DOE Analysis module components
    - `sqc/` - SQC Analysis module components
    - `rag/` - RAG System components
    - `core/` - Core components used across modules
    - `layout/` - Layout components
    - `reports/` - Report generation components
    - `workflow/` - Workflow management components
  - `api/` - API clients for communicating with the backend
  - `hooks/` - Custom React hooks
  - `pages/` - Page components
  - `services/` - Business logic and services
  - `utils/` - Utility functions including error handling
  - `config/` - Application configuration
  - `App.jsx` - Root component
  - `index.js` - Entry point

## Development Guidelines

### Error Handling

The application implements a comprehensive error handling system:

- Global `ErrorBoundary` for React component errors
- API error handling utilities in `utils/errorHandlers.js`
- Consistent error categorization by HTTP status codes
- User-friendly error notifications using Snackbar components

Example usage:
```jsx
import { useErrorHandler } from '../../utils/errorHandlers';

function MyComponent() {
  const handleError = useErrorHandler();
  
  const fetchData = async () => {
    try {
      // API calls
    } catch (err) {
      handleError(err, {
        onServerError: () => setFallbackData([]),
        onNetworkError: () => setIsOfflineMode(true)
      });
    }
  };
}
```

### React Hooks

When using React hooks, especially `useEffect`, ensure dependency arrays are correctly specified to avoid stale closures or unnecessary re-renders.

Example:
```jsx
// Correct usage with proper dependencies
useEffect(() => {
  // Effect logic
}, [dependency1, dependency2]);
```

## Testing

Run tests using:

```bash
npm test
# or
yarn test
```

## Browser Compatibility

The application supports:
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Technologies Used

- React
- React Router
- Material-UI
- MathJax (for mathematical formulas)
- D3.js (for visualizations)
- Recharts
- Axios
- Jest (for testing)

## License

This project is licensed under the MIT License.