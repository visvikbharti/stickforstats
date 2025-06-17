# Performance Monitoring System

This document describes the comprehensive performance monitoring system implemented in the StickForStats frontend application. This system provides real-time insights into application performance, tracks Web Vitals, resource loading, component rendering, API calls, and JavaScript errors.

## Overview

The performance monitoring system consists of several components:

1. **Core Monitoring Utilities**: Tracks and collects various performance metrics
2. **Performance Dashboard**: Visual display of collected metrics 
3. **React Hooks and HOCs**: Easy integration with React components
4. **Toggle Component**: UI control for enabling/disabling monitoring

## Features

The monitoring system tracks the following metrics:

- **Core Web Vitals**
  - Largest Contentful Paint (LCP)
  - First Input Delay (FID)
  - Cumulative Layout Shift (CLS)
  - First Contentful Paint (FCP)
  - Time to First Byte (TTFB)

- **Resource Timing**
  - Script, stylesheet, image, and font loading times
  - Resource transfer sizes
  - Loading waterfalls

- **Component Performance**
  - Component render times
  - Re-render frequency
  - Props impact on performance

- **API/Network Calls**
  - API request durations
  - Success/failure rates
  - Network request sizes

- **JavaScript Errors**
  - Error tracking with stack traces
  - Error frequency and impact

- **User Interactions**
  - Interaction timing
  - Input delay
  - Long tasks detection

## Implementation

### 1. Core Monitoring Utilities

The `performanceMonitoring.js` utility is the core of the monitoring system, providing functions to:

- Initialize monitoring with configurable options
- Track Web Vitals metrics
- Monitor resource loading
- Track API calls
- Capture JavaScript errors
- Measure component render times
- Track user interactions

```javascript
// Initialize the monitoring system
import { initPerformanceMonitoring } from './utils/performanceMonitoring';

initPerformanceMonitoring({
  logToConsole: true,           // Log metrics to console
  sendToAnalytics: false,       // Send to analytics service
  sendToBackend: false,         // Send to backend API
  samplingRate: 1.0,            // Track all users (1.0 = 100%)
  includeResourceDetails: true, // Include detailed resource information
});
```

### 2. React Integration

#### Performance Tracking Hook

The `usePerformanceTracking` hook provides an easy way to track component performance:

```jsx
import { usePerformanceTracking } from '../hooks/usePerformanceTracking';

function MyComponent(props) {
  const { trackAction, mark } = usePerformanceTracking('MyComponent', {
    trackProps: true,
    dependencies: [props.id]
  });
  
  // Track a user interaction
  const handleClick = trackAction('button-click', () => {
    // Your code here
  });
  
  // Add a custom performance mark
  mark('component-ready', { timestamp: Date.now() });
  
  return (
    <button onClick={handleClick}>Click Me</button>
  );
}
```

#### Higher-Order Component

The `withPerformanceTracking` HOC can wrap any component to track its performance:

```jsx
import withPerformanceTracking from '../utils/withPerformanceTracking';

function ExpensiveComponent(props) {
  // Component code
}

// Wrap component with performance tracking
export default withPerformanceTracking(ExpensiveComponent, {
  trackProps: true,
  trackUpdates: true
});
```

### 3. Performance Dashboard

The `PerformanceDashboard` component provides a visual interface for viewing all collected metrics:

```jsx
import PerformanceDashboard from './components/performance/PerformanceDashboard';

function App() {
  return (
    <div>
      <AppContent />
      {process.env.NODE_ENV === 'development' && <PerformanceDashboard />}
    </div>
  );
}
```

### 4. Monitor Toggle

The `PerformanceMonitorToggle` component provides a floatable UI for controlling the monitoring system:

```jsx
import PerformanceMonitorToggle from './components/performance/PerformanceMonitorToggle';

function App() {
  return (
    <div>
      <AppContent />
      <PerformanceMonitorToggle defaultVisible={false} />
    </div>
  );
}
```

## Usage Guidelines

### When to Use Performance Monitoring

1. **Development**: Enable comprehensive monitoring during development to identify performance bottlenecks.
2. **Testing**: Use monitoring during testing phases to validate performance requirements.
3. **Production Sampling**: Use a reduced sampling rate (e.g., 10%) in production to monitor real-world performance.

### Optimizing Component Rendering

Use the performance data to identify slow-rendering components:

1. Look for components with high average render times (>16ms).
2. Check for components with excessive re-renders.
3. Optimize using React.memo, useMemo, and useCallback for identified components.

### Addressing Slow Resource Loading

The Resources tab helps identify slow-loading resources:

1. Look for resources with loading times >200ms.
2. Consider lazy loading, code splitting, or preloading critical resources.
3. Apply appropriate caching strategies.

### Monitoring Web Vitals

Use the Web Vitals tab to ensure good Core Web Vitals scores:

1. LCP should be under 2.5 seconds
2. FID should be under 100ms
3. CLS should be under 0.1

## Best Practices

1. **Use Sampling in Production**: To minimize performance impact, use a sampling rate of 10-20% in production.
2. **Focus on Problem Areas**: Use the dashboard to identify the slowest components and resources.
3. **Regular Audits**: Conduct regular performance audits using the monitoring data.
4. **Test on Different Devices**: Use the monitoring system on various devices and network conditions.
5. **Track Performance Over Time**: Save metrics reports to track performance trends across releases.

## Configuration Options

The monitoring system can be configured with these options:

```javascript
{
  logToConsole: false,        // Log metrics to console
  sendToAnalytics: false,     // Send to analytics (Google Analytics, etc.)
  sendToBackend: false,       // Send to backend API
  backendEndpoint: '/api/performance', // API endpoint for metrics
  samplingRate: 1.0,          // Percentage of sessions to monitor
  includeResourceDetails: true, // Include detailed resource information
  storageLimit: {             // Limits for stored metrics
    interactions: 50,
    componentRenders: 30,
    resources: 100,
    jsErrors: 10,
    apiCalls: 50
  }
}
```

## Integration with Analytics

The performance monitoring system can integrate with analytics platforms:

```javascript
initPerformanceMonitoring({
  sendToAnalytics: true,
  // Custom handler for analytics integration
  analyticsHandler: (metricData) => {
    // Send to your analytics platform
    window.analytics.track('performance_metric', metricData);
  }
});
```

## Backend Integration

For a more comprehensive monitoring solution, you can set up a backend API to receive and store metrics:

```javascript
initPerformanceMonitoring({
  sendToBackend: true,
  backendEndpoint: '/api/performance-metrics',
  // Additional data to send with metrics
  backendData: {
    appVersion: process.env.REACT_APP_VERSION,
    environment: process.env.NODE_ENV
  }
});
```

Your backend can then store and analyze this data to track performance over time and across different user segments.