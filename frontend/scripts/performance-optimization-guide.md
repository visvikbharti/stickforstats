# Performance Optimization Guide

This guide outlines strategies and best practices for optimizing the performance of the StickForStats frontend application.

## Table of Contents

1. [Bundle Size Optimization](#bundle-size-optimization)
2. [Rendering Performance](#rendering-performance)
3. [Network Optimization](#network-optimization)
4. [Image Optimization](#image-optimization)
5. [Code Splitting](#code-splitting)
6. [Caching Strategies](#caching-strategies)
7. [Measuring Performance](#measuring-performance)

## Bundle Size Optimization

### Analyzing Bundle Size

```bash
# Generate detailed bundle analysis
npm run build:analyze

# Run interactive analysis
npm run analyze:interactive
```

### Reducing Bundle Size

- **Remove unused dependencies**
  - Use `npm run optimize:deps` to identify unused dependencies
  - Implement tree shaking by using ES modules and proper exports

- **Minimize library size**
  - Use smaller alternatives (e.g., date-fns instead of moment)
  - Use specific imports (e.g., `import { Button } from '@mui/material'` instead of importing the entire library)

- **Code splitting and lazy loading**
  - Split code by route using React.lazy() and Suspense
  - Lazy load heavy components that aren't immediately needed

## Rendering Performance

### Component Optimization

- **Prevent unnecessary re-renders**
  - Use React.memo for pure functional components
  - Implement useMemo for expensive calculations
  - Use useCallback for functions passed as props

- **Virtualization for long lists**
  - Implement virtualized lists for data tables and long lists
  - Only render visible items to reduce DOM nodes

- **Optimize state management**
  - Avoid deeply nested state
  - Use appropriate state management for the task (useState, useReducer, global state)
  - Implement context selectors to prevent unnecessary rerenders

### Example: Optimizing a Component

```jsx
// Before optimization
function DataTable({ data }) {
  return (
    <div>
      {data.map(item => (
        <Row key={item.id} data={item} />
      ))}
    </div>
  );
}

// After optimization
import { memo } from 'react';
import { FixedSizeList } from 'react-window';

const Row = memo(({ data }) => (
  <div className="row">{data.name}</div>
));

function DataTable({ data }) {
  return (
    <FixedSizeList
      height={500}
      width="100%"
      itemCount={data.length}
      itemSize={35}
      itemData={data}
    >
      {({ index, style, data }) => (
        <Row style={style} data={data[index]} />
      )}
    </FixedSizeList>
  );
}
```

## Network Optimization

### API Request Optimization

- **Implement request batching**
  - Combine multiple API requests into a single request
  - Use GraphQL to request only needed data

- **Cache API responses**
  - Use React Query or SWR for data fetching with built-in caching
  - Implement custom caching for frequently accessed data

- **Enable compression**
  - Make sure gzip/brotli compression is enabled on the server
  - Compress API responses and static assets

### Reducing Roundtrips

- **Implement connection pooling**
  - Reuse connections to reduce handshake overhead

- **Use HTTP/2 or HTTP/3**
  - Multiplex requests over a single connection

## Image Optimization

### Image Format Selection

- **Use WebP and AVIF formats**
  - Convert images using the built-in scripts:
  ```bash
  npm run convert:webp
  npm run convert:avif
  ```

- **Generate responsive images**
  - Create multiple sizes for different devices:
  ```bash
  npm run generate:responsive
  ```

- **Run complete image optimization**
  ```bash
  npm run optimize:images
  ```

### Lazy Loading Images

- **Use native lazy loading**
  ```html
  <img src="image.jpg" loading="lazy" alt="Description" />
  ```

- **Implement blur-up technique**
  - Show low-quality image placeholder while loading

## Code Splitting

### Route-Based Splitting

```jsx
import { lazy, Suspense } from 'react';

const ProbabilityModule = lazy(() => import('./components/probability_distributions/ProbabilityDistributionsPage'));
const ConfidenceModule = lazy(() => import('./components/confidence_intervals/ConfidenceIntervalsPage'));

function App() {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/probability-distributions" element={<ProbabilityModule />} />
          <Route path="/confidence-intervals" element={<ConfidenceModule />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
```

### Component-Based Splitting

```jsx
import { lazy, Suspense, useState } from 'react';

const HeavyChart = lazy(() => import('./components/HeavyChart'));

function Dashboard() {
  const [showChart, setShowChart] = useState(false);
  
  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>
      
      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}
```

## Caching Strategies

### Static Asset Caching

- **Configure proper cache headers**
  - Use long cache times for versioned assets
  - Set appropriate Cache-Control headers

- **Implement service workers**
  - Cache static assets and API responses
  - Enable offline functionality

### Service Worker Implementation

```javascript
// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').then(registration => {
      console.log('SW registered:', registration);
    }).catch(registrationError => {
      console.log('SW registration failed:', registrationError);
    });
  });
}
```

## Measuring Performance

### Using the Built-in Performance Monitoring

```javascript
import { initPerformanceMonitoring, trackComponentRender } from '../utils/performanceMonitoring';

// Initialize at app startup
initPerformanceMonitoring({
  logToConsole: process.env.NODE_ENV === 'development',
  sendToBackend: process.env.NODE_ENV === 'production'
});

// Track component render performance
function MyComponent() {
  const startTime = performance.now();
  
  // Component rendering...
  
  useEffect(() => {
    trackComponentRender('MyComponent', performance.now() - startTime);
  }, []);
  
  return <div>Content</div>;
}
```

### Custom Performance Marks

```javascript
import { addCustomMark } from '../utils/performanceMonitoring';

function DataLoadingComponent() {
  useEffect(() => {
    const fetchStart = performance.now();
    
    fetchData().then(data => {
      addCustomMark('dataFetchTime', performance.now() - fetchStart);
      // Process data...
    });
  }, []);
}
```

### Running Performance Tests

```bash
# Run performance tests
npm run test:performance

# Test specific device and network
npm run test:performance -- --device=mobile --network=slow4g

# Focus on specific module
npm run test:performance -- --module=probability
```

## Next Steps

1. Run a complete performance audit using the built-in tools
2. Identify the biggest bottlenecks using the performance reports
3. Implement the most impactful optimizations first
4. Re-run performance tests to measure improvements
5. Establish performance budgets for each module
6. Integrate performance testing into the CI/CD pipeline