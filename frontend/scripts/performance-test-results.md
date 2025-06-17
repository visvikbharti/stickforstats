# Performance Test Results

## Overview of Performance Testing Framework

The StickForStats frontend application includes a comprehensive performance testing framework that measures key metrics across different modules, device profiles, and network conditions. This document explains the infrastructure and how to use it to optimize application performance.

## Key Performance Metrics

Our testing framework measures the following Core Web Vitals and additional metrics:

### Core Web Vitals
- **FCP (First Contentful Paint)**: Time until the first content appears (target: < 2000ms)
- **LCP (Largest Contentful Paint)**: Time until largest content element is visible (target: < 2500ms)
- **CLS (Cumulative Layout Shift)**: Visual stability measure (target: < 0.1)
- **FID (First Input Delay)**: Time until page responds to user interaction (target: < 100ms)

### Additional Metrics
- **TTI (Time to Interactive)**: When the page becomes fully interactive (target: < 3500ms)
- **TBT (Total Blocking Time)**: Main thread blocking time (target: < 300ms)
- **Network Requests**: Total number of network requests (target: < 80)
- **Data Transfer**: Total data downloaded (target: < 3MB)
- **Page Load**: Overall page load time (target: < 5000ms)

## Running Performance Tests

The application includes a dedicated performance testing script that can be run with:

```bash
npm run test:performance
```

### Test Configuration

You can customize the testing parameters:

```bash
# Test specific device profile
npm run test:performance -- --device=mobile

# Test specific network condition
npm run test:performance -- --network=fast3g

# Test specific module
npm run test:performance -- --module=probability

# Run multiple iterations
npm run test:performance -- --iterations=5

# Run in headless mode
npm run test:performance -- --headless

# Run in CI mode (adjusts thresholds)
npm run test:performance -- --ci

# View detailed logs
npm run test:performance -- --verbose
```

## Device Profiles

The testing framework includes the following device profiles:

| Profile | Resolution | User Agent |
|---------|------------|------------|
| Desktop | 1920x1080  | Desktop Chrome |
| Laptop  | 1366x768   | Desktop Chrome |
| Tablet  | 768x1024   | iPad Safari |
| Mobile  | 375x812    | iPhone Safari |

## Network Profiles

The following network conditions can be simulated:

| Profile | Download | Upload | Latency |
|---------|----------|--------|---------|
| WiFi    | 50 Mbps  | 20 Mbps | 2ms    |
| Fast 4G | 25 Mbps  | 10 Mbps | 20ms   |
| Slow 4G | 5 Mbps   | 2 Mbps  | 40ms   |
| Fast 3G | 1.5 Mbps | 750 Kbps | 100ms  |

## Modules Tested

The performance test covers all major application modules:

- Home Page (`/`)
- Probability Distributions (`/probability-distributions`)
- Confidence Intervals (`/confidence-intervals`)
- DOE Analysis (`/doe-analysis`)
- SQC Analysis (`/sqc-analysis`)
- PCA Analysis (`/pca-analysis`)
- Workflows (`/workflows`)
- Reports (`/reports`)

## Understanding Test Results

After running the tests, a comprehensive report is generated in the `performance-results` directory. The report includes:

- Overall performance score (0-100)
- Module-specific scores
- Detailed performance metrics for each module
- Failed thresholds and recommendations for improvement

## Common Performance Issues and Solutions

### Slow First Contentful Paint (FCP)
- **Issue**: Server response time or render-blocking resources
- **Solution**: Implement code splitting, reduce JavaScript bundle size, use resource hints (preload, preconnect)

### Poor Largest Contentful Paint (LCP)
- **Issue**: Slow-loading hero images or critical content
- **Solution**: Optimize images, implement responsive images, use WebP/AVIF formats, lazy load non-critical images

### High Cumulative Layout Shift (CLS)
- **Issue**: Elements moving after initial render
- **Solution**: Set image dimensions in HTML, avoid dynamic content insertion above existing content, use CSS transform for animations

### Long First Input Delay (FID)
- **Issue**: Heavy JavaScript execution
- **Solution**: Break up long tasks, defer non-critical JavaScript, remove unused code, implement code splitting

### Large Bundle Size
- **Issue**: Too much JavaScript being loaded
- **Solution**: Implement tree shaking, code splitting, lazy loading of components, and dynamic imports

## Performance Budget

The application aims to meet the following performance targets:

| Metric | Target | Poor |
|--------|--------|------|
| Performance Score | ≥ 90 | < 70 |
| First Contentful Paint | < 2s | > 3s |
| Largest Contentful Paint | < 2.5s | > 4s |
| Cumulative Layout Shift | < 0.1 | > 0.25 |
| First Input Delay | < 100ms | > 300ms |
| Time to Interactive | < 3.5s | > 7.5s |
| JS Bundle Size | < 500KB | > 1MB |
| Total Page Weight | < 2MB | > 4MB |

## Continuous Monitoring

In addition to the performance testing framework, the application includes real-time performance monitoring:

- Web Vitals tracking in production
- Performance metrics dashboard
- User-experienced performance tracking
- Custom performance marks for critical user flows

## Next Steps

1. Run the performance tests regularly during development
2. Address any failing metrics based on the recommendations
3. Focus on the high-importance modules first
4. Verify improvements by re-running tests after changes
5. Consider implementing user-centric performance metrics