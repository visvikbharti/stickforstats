// Performance testing using Cypress
//
// This test file configures Cypress to run performance tests against
// the StickForStats application, measuring Core Web Vitals and other 
// performance metrics.

describe('Performance Testing', () => {
  const TEST_SCENARIOS = [
    { name: 'Home Page', path: '/' },
    { name: 'Probability Distributions', path: '/probability-distributions' },
    { name: 'Confidence Intervals', path: '/confidence-intervals' },
    { name: 'DOE Analysis', path: '/doe-analysis' },
    { name: 'SQC Analysis', path: '/sqc-analysis' },
    { name: 'PCA Analysis', path: '/pca-analysis' },
  ];
  
  // Performance thresholds (conservative for CI environments)
  const THRESHOLDS = {
    FCP: 3000,  // First Contentful Paint: 3 seconds
    LCP: 5000,  // Largest Contentful Paint: 5 seconds
    CLS: 0.25,  // Cumulative Layout Shift: 0.25
    resourceCount: 100, // Maximum number of resources
    totalBytes: 5000000, // 5MB (adjust if needed)
  };
  
  // Helper function to collect performance metrics
  const collectPerformanceMetrics = () => {
    return cy.window().then((win) => {
      // Wait for any pending measurements to complete
      return new Cypress.Promise((resolve) => {
        setTimeout(() => {
          // Use the app's performance monitoring utilities if available
          if (win.getPerformanceSummary) {
            resolve(win.getPerformanceSummary());
          } else {
            // Fallback to basic Performance API metrics
            const performance = win.performance;
            
            // Get navigation timing
            const navigationEntry = performance.getEntriesByType('navigation')[0];
            const paintEntries = performance.getEntriesByType('paint');
            const resourceEntries = performance.getEntriesByType('resource');
            
            // Calculate FCP
            const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint');
            const fcp = fcpEntry ? fcpEntry.startTime : null;
            
            // Calculate approximate CLS (not accurate without the Layout Instability API)
            const cls = 0; // Not possible to accurately measure in Cypress
            
            // Calculate TTFB
            const ttfb = navigationEntry ? navigationEntry.responseStart - navigationEntry.requestStart : null;
            
            // Calculate page load
            const pageLoad = navigationEntry ? navigationEntry.loadEventEnd - navigationEntry.startTime : null;
            
            // Calculate resource stats
            const resourceCount = resourceEntries.length;
            const totalBytes = resourceEntries.reduce((total, resource) => total + (resource.transferSize || 0), 0);
            
            resolve({
              webVitals: {
                FCP: fcp,
                LCP: null, // Not easily measurable in Cypress
                CLS: cls,
                FID: null, // Not easily measurable in Cypress
                TTFB: ttfb,
              },
              pageLoad,
              resourceCount,
              totalBytes,
              timestamp: Date.now()
            });
          }
        }, 1000); // Wait 1 second for metrics to stabilize
      });
    });
  };
  
  // Run tests for each scenario
  TEST_SCENARIOS.forEach((scenario) => {
    it(`should load ${scenario.name} with acceptable performance`, () => {
      // Visit the page
      cy.visit(scenario.path, {
        onBeforeLoad(win) {
          // Set up performance observer for PerformanceEntry objects
          const performanceObserver = win.PerformanceObserver;
          if (performanceObserver) {
            // Stub to ensure PerformanceObserver doesn't cause issues
            cy.stub(performanceObserver.prototype, 'observe').callsFake(() => {});
          }
        }
      });
      
      // Wait for page to be fully loaded
      cy.get('body', { timeout: 20000 }).should('be.visible');
      
      // Collect performance metrics
      cy.then(() => {
        return collectPerformanceMetrics().then((metrics) => {
          // Log the metrics
          cy.log('Performance Metrics', JSON.stringify(metrics, null, 2));
          
          // Assert on the metrics we can reliably measure
          if (metrics.webVitals.FCP) {
            expect(metrics.webVitals.FCP).to.be.lessThan(
              THRESHOLDS.FCP,
              `FCP should be less than ${THRESHOLDS.FCP}ms`
            );
          }
          
          if (metrics.resourceCount) {
            expect(metrics.resourceCount).to.be.lessThan(
              THRESHOLDS.resourceCount,
              `Resource count should be less than ${THRESHOLDS.resourceCount}`
            );
          }
          
          if (metrics.totalBytes) {
            expect(metrics.totalBytes).to.be.lessThan(
              THRESHOLDS.totalBytes,
              `Page weight should be less than ${THRESHOLDS.totalBytes} bytes`
            );
          }
          
          // Store results as test artifacts
          const testResults = {
            scenario: scenario.name,
            path: scenario.path,
            timestamp: Date.now(),
            metrics,
            pass: true
          };
          
          // Write results to file (only works in Node environment)
          cy.task('log', { message: `Performance test results for ${scenario.name}`, data: testResults });
        });
      });
    });
  });
});

// Test the performance dashboard itself
describe('Performance Test Dashboard', () => {
  it('should load and allow configuration of tests', () => {
    // Visit the performance dashboard 
    // (Note: This assumes you have added a route to the dashboard)
    cy.visit('/test/performance');
    
    // Verify key components are present
    cy.contains('Performance Testing Dashboard').should('be.visible');
    cy.contains('Test Configuration').should('be.visible');
    
    // Check device profile selector
    cy.get('#device-profile').should('be.visible');
    
    // Check network profile selector
    cy.get('#network-profile').should('be.visible');
    
    // Check test scenarios selector
    cy.get('#scenarios').should('be.visible');
    
    // Check run button is enabled
    cy.contains('Run Performance Tests').should('not.be.disabled');
  });
  
  it('should display saved results if available', () => {
    // Visit the performance dashboard
    cy.visit('/test/performance');
    
    // Check if saved results section exists
    cy.contains('Saved Results').should('be.visible');
    
    // Note: We can't reliably test the actual running of tests in Cypress
    // as it would create a recursive testing situation
  });
});