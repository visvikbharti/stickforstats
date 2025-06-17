# Performance Testing Guide for StickForStats

## Overview

This document outlines the comprehensive performance testing strategy implemented for the StickForStats application. The performance testing system enables automated testing across different device profiles, network conditions, and application scenarios to ensure consistent performance and identify potential bottlenecks.

## Key Performance Metrics

StickForStats monitors the following key performance metrics:

### Core Web Vitals

| Metric | Description | Good | Needs Improvement | Poor |
|--------|-------------|------|-------------------|------|
| **LCP** | Largest Contentful Paint - Time to render the largest content element | 0-2500ms | 2500-4000ms | >4000ms |
| **FID** | First Input Delay - Time from first user interaction to response | 0-100ms | 100-300ms | >300ms |
| **CLS** | Cumulative Layout Shift - Sum of layout shift scores | 0-0.1 | 0.1-0.25 | >0.25 |

### Additional Performance Metrics

| Metric | Description | Good | Needs Improvement | Poor |
|--------|-------------|------|-------------------|------|
| **FCP** | First Contentful Paint - Time until the first content is painted | 0-1000ms | 1000-3000ms | >3000ms |
| **TTFB** | Time to First Byte - Time until the first byte is received | 0-200ms | 200-500ms | >500ms |
| **Load** | Page Load Time - Time until the page is fully loaded | 0-2500ms | 2500-5000ms | >5000ms |
| **Resources** | Number of resources loaded | 0-40 | 40-80 | >80 |
| **Page Weight** | Total size of all resources | 0-1000KB | 1000-2500KB | >2500KB |

## Testing Infrastructure

### Components

The performance testing infrastructure consists of the following components:

1. **Performance Testing Utility (`performanceTesting.js`)**
   - Manages test execution and configuration
   - Handles device and network emulation
   - Collects and analyzes performance metrics
   - Generates test reports and recommendations

2. **Performance Monitoring Utility (`performanceMonitoring.js`)**
   - Tracks real-time performance metrics
   - Monitors Web Vitals, resource loading, API calls, and errors
   - Provides hooks for component-level performance tracking

3. **Performance Test Dashboard (`PerformanceTestDashboard.jsx`)**
   - User interface for configuring and running tests
   - Visualizes test results and historical data
   - Provides recommendations for performance improvements

4. **Cypress Performance Tests (`performance-testing.cy.js`)**
   - Automated performance testing in CI environments
   - Validates performance across key application scenarios
   - Enforces performance budgets and thresholds

### Device Profiles

The testing infrastructure supports the following device profiles:

| Profile | Viewport | Device Pixel Ratio | Description |
|---------|----------|-------------------|-------------|
| Desktop | 1920x1080 | 1 | Standard desktop computer |
| Laptop | 1366x768 | 1 | Standard laptop screen |
| Tablet | 768x1024 | 2 | Tablet devices (iPad-like) |
| Mobile | 375x812 | 3 | Mobile phone (iPhone X-like) |

### Network Profiles

The following network conditions can be simulated:

| Profile | Download | Upload | Latency | Description |
|---------|----------|--------|---------|-------------|
| Offline | 0 Kbps | 0 Kbps | ∞ | No connectivity |
| Slow 2G | 250 Kbps | 50 Kbps | 300ms | Very slow connection |
| Fast 3G | 1.5 Mbps | 750 Kbps | 40ms | Average mobile connection |
| Slow 4G | 4 Mbps | 2 Mbps | 20ms | Basic 4G connection |
| Fast 4G | 25 Mbps | 10 Mbps | 5ms | Good 4G connection |
| WiFi | 50 Mbps | 20 Mbps | 2ms | Standard home WiFi |

### Test Scenarios

Performance tests are conducted across the following application scenarios:

1. **Home Page** - Initial page load performance
2. **Probability Distributions** - Performance of probability distributions module
3. **Confidence Intervals** - Performance of confidence intervals module
4. **DOE Analysis** - Performance of DOE analysis module
5. **SQC Analysis** - Performance of SQC analysis module
6. **PCA Analysis** - Performance of PCA analysis module

## Running Performance Tests

### Using the Performance Dashboard

1. Navigate to the Performance Dashboard at `/test/performance`
2. Configure test parameters:
   - Select device profile (Desktop, Tablet, Mobile, etc.)
   - Select network profile (WiFi, 4G, 3G, etc.)
   - Select test scenarios to run
   - Set number of iterations (1-10)
   - Set delay between runs (1000-10000ms)
3. Click "Run Performance Tests" button
4. View results and recommendations after tests complete

### Using Cypress for Automated Testing

```bash
# Run all performance tests
npx cypress run --spec "cypress/e2e/performance-testing.cy.js"

# Run tests for a specific scenario
npx cypress run --spec "cypress/e2e/performance-testing.cy.js" --env scenario=home
```

### Programmatic API

```javascript
import { 
  configurePerformanceTesting, 
  runPerformanceTest, 
  DEVICE_PROFILES, 
  NETWORK_PROFILES, 
  TEST_SCENARIOS 
} from './utils/performanceTesting';

// Configure testing parameters
configurePerformanceTesting({
  deviceProfile: DEVICE_PROFILES.MOBILE,
  networkProfile: NETWORK_PROFILES.FAST_3G,
  iterations: 3,
  delayBetweenRuns: 3000
});

// Run tests for specific scenarios
const testScenarios = [
  TEST_SCENARIOS.HOME_PAGE,
  TEST_SCENARIOS.PROBABILITY_DISTRIBUTIONS
];

// Execute tests and get results
runPerformanceTest(testScenarios)
  .then(({ results, summary }) => {
    console.log('Test Summary:', summary);
    
    // Check for performance issues
    if (summary.issuesFound) {
      console.warn('Performance issues detected:', summary.recommendations);
    }
  });
```

## Interpreting Test Results

### Performance Score

Each test scenario receives an overall performance score (0-100) calculated as a weighted average of individual metric scores:

- **90-100**: Excellent - Performance is optimal
- **70-89**: Good - Performance is acceptable but could be improved
- **50-69**: Needs Improvement - Performance issues may affect user experience
- **0-49**: Poor - Critical performance issues requiring immediate attention

### Recommendations

The testing system automatically generates recommendations based on detected performance issues. These recommendations include:

1. **Specific Actions**: Concrete steps to address the identified issues
2. **Prioritization**: More critical issues receive higher priority
3. **Documentation Links**: References to relevant performance optimization techniques

## Integration with CI/CD

Performance tests can be integrated into CI/CD pipelines to ensure performance regressions are caught before deployment.

### GitHub Actions Example

```yaml
jobs:
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Build project
        run: npm run build
      - name: Run performance tests
        run: npx cypress run --spec "cypress/e2e/performance-testing.cy.js"
      - name: Check performance budgets
        run: node scripts/check-performance-budgets.js
```

## Best Practices

1. **Run Tests Regularly**: Schedule regular performance tests to catch regressions early
2. **Test on Multiple Profiles**: Always test across different device and network profiles
3. **Set Performance Budgets**: Establish clear thresholds for key metrics
4. **Focus on User-Centric Metrics**: Prioritize metrics that directly impact user experience
5. **Trend Analysis**: Monitor performance trends over time rather than just absolute values

## Troubleshooting

### Common Issues

1. **Inconsistent Results**: 
   - Run multiple iterations to get a more reliable average
   - Ensure the testing environment is stable

2. **Failed Tests in CI**:
   - CI environments may have different performance characteristics
   - Adjust thresholds for CI environments to account for virtualization overhead

3. **Network Emulation Issues**:
   - Browser-based network throttling is approximate
   - For precise network testing, use dedicated tools like WebPageTest

## Future Enhancements

1. **Machine Learning Analysis**: Implement ML models to predict performance issues
2. **User Experience Metrics**: Add metrics like "Time to Interactive" and "Speed Index"
3. **Component-Level Testing**: Extend testing to individual components
4. **Performance Monitoring in Production**: Integrate with real user monitoring

## References

- [Web Vitals Documentation](https://web.dev/vitals/)
- [Performance Optimization Techniques](https://web.dev/fast/)
- [Lighthouse Performance Audits](https://developers.google.com/web/tools/lighthouse/audits/metrics)
- [Performance Testing Best Practices](https://web.dev/performance-audit/)
- [Chrome DevTools Performance Panel](https://developers.google.com/web/tools/chrome-devtools/evaluate-performance)