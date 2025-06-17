# StickForStats Performance Testing Guide

This guide explains how to use the performance testing tools provided with the StickForStats frontend application.

## Table of Contents

1. [Available Performance Tools](#available-performance-tools)
2. [Automated Performance Testing](#automated-performance-testing)
3. [Manual Performance Testing](#manual-performance-testing)
4. [Continuous Integration](#continuous-integration)
5. [Performance Monitoring](#performance-monitoring)
6. [Best Practices](#best-practices)

## Available Performance Tools

StickForStats includes several complementary performance tools:

- **Automated performance testing script** (`npm run test:performance`)
- **Manual performance testing utilities** (`src/utils/manualPerformanceTesting.js`)
- **Performance monitoring system** (`src/utils/performanceMonitoring.js`)
- **Bundle analysis tools** (`npm run build:analyze`)
- **Component performance tracking HOC** (`src/utils/withPerformanceTracking.jsx`)

## Automated Performance Testing

The automated performance testing system uses Puppeteer to measure key performance metrics across different device and network conditions.

### Basic Usage

```bash
# Run all tests with default settings
npm run test:performance

# Test on specific device
npm run test:performance -- --device=mobile

# Test with specific network conditions
npm run test:performance -- --network=slow4g

# Test a specific module
npm run test:performance -- --module=probability

# Run tests in CI mode (adjusts thresholds)
npm run test:performance -- --ci --headless
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--device` | Device profile (desktop, laptop, tablet, mobile) | desktop |
| `--network` | Network profile (wifi, fast4g, slow4g, fast3g) | wifi |
| `--module` | Specific module to test | (all modules) |
| `--iterations` | Number of test iterations | 3 |
| `--output` | Output file name | performance-report.json |
| `--headless` | Run in headless mode | false |
| `--ci` | Run in CI mode (adjusts thresholds) | false |
| `--verbose` | Show detailed logs | false |

### Understanding Test Results

The test generates two output files in the `performance-results` directory:

1. `performance-report.json` - Raw test data
2. `performance-report.md` - Formatted report with analysis

The report includes:
- Overall performance score
- Module-specific scores
- Detailed metrics for each test
- Failed thresholds and recommendations

## Manual Performance Testing

For measuring performance during development, use the manual testing utilities:

```javascript
import { 
  timeFunction, 
  timeAsyncFunction,
  testRenderPerformance,
  testDataProcessing
} from '../utils/manualPerformanceTesting';

// Time a synchronous function
const result = timeFunction(() => {
  // Your code here
}, 'Calculation Time');

// Time an async function
const data = await timeAsyncFunction(async () => {
  return await fetchLargeDataset();
}, 'Data Fetch Time');

// Test component render performance
const renderTest = await testRenderPerformance('DataGrid', async (test) => {
  // Render your component
  test.mark('firstRender');
  
  // Perform more operations
  test.mark('dataLoaded');
});

// Get test history
import { getAllTestResults, generatePerformanceReport } from '../utils/manualPerformanceTesting';
console.log(getAllTestResults());
console.log(generatePerformanceReport());
```

### Timing Decorator

```javascript
import { timed } from '../utils/manualPerformanceTesting';

class DataProcessor {
  @timed('processData')
  processData(input) {
    // Method implementation
    return result;
  }
}
```

## Continuous Integration

For CI environments, use the headless and CI modes:

```bash
npm run test:performance:ci
```

This command uses more lenient thresholds appropriate for CI environments and runs in headless mode.

### GitHub Actions Integration

```yaml
jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - name: Run performance tests
        run: npm run test:performance:ci
      - name: Archive performance results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: performance-results/
```

## Performance Monitoring

StickForStats includes a real-time performance monitoring system that can be initialized in your application:

```javascript
import { initPerformanceMonitoring } from './utils/performanceMonitoring';

// Initialize at application startup
initPerformanceMonitoring({
  logToConsole: process.env.NODE_ENV === 'development',
  sendToBackend: process.env.NODE_ENV === 'production',
  samplingRate: 0.1 // Only monitor 10% of sessions
});
```

### Tracking Component Performance

```javascript
import { trackComponentRender } from './utils/performanceMonitoring';

function MyComponent() {
  const startTime = performance.now();
  
  // Component code here
  
  useEffect(() => {
    trackComponentRender('MyComponent', performance.now() - startTime);
  }, []);
  
  return <div>Content</div>;
}

// Or use the HOC
import withPerformanceTracking from './utils/withPerformanceTracking';

export default withPerformanceTracking(MyComponent, 'MyComponent');
```

## Best Practices

1. **Run tests regularly** during development to catch performance regressions early

2. **Focus on Core Web Vitals**:
   - First Contentful Paint (FCP) - < 2s
   - Largest Contentful Paint (LCP) - < 2.5s
   - Cumulative Layout Shift (CLS) - < 0.1
   - First Input Delay (FID) - < 100ms

3. **Optimize common bottlenecks**:
   - Reduce JavaScript bundle size through code splitting
   - Optimize image loading with WebP/AVIF formats and responsive images
   - Implement lazy loading for below-the-fold content
   - Use virtualization for long lists

4. **Test across environments**:
   - Multiple device profiles (desktop, tablet, mobile)
   - Various network conditions (fast, slow, offline)
   - Different browsers (Chrome, Firefox, Safari)

5. **Establish performance budgets**:
   - Maximum bundle size per route
   - Maximum number of network requests
   - Maximum time to interactive
   - Maximum server response time

6. **Document performance findings**:
   - Add comments for performance-critical code
   - Document performance implications of architectural decisions
   - Share benchmark results with the team