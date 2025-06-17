#!/usr/bin/env node

/**
 * Automated Performance Testing Script
 * 
 * This script runs performance tests for the StickForStats application across
 * different device profiles, network conditions, and application modules.
 * It generates a baseline report of performance metrics, identifies bottlenecks,
 * and provides recommendations for optimization.
 * 
 * Usage:
 *   node scripts/run-performance-tests.js [options]
 * 
 * Options:
 *   --device=<profile>    Specify device profile (desktop, tablet, mobile)
 *   --network=<profile>   Specify network profile (wifi, 4g, 3g)
 *   --module=<name>       Test specific module only
 *   --iterations=<num>    Number of test iterations (default: 3)
 *   --output=<file>       Output file for report (default: performance-report.json)
 *   --headless            Run in headless mode
 *   --ci                  Run in CI mode (adjusts thresholds)
 *   --verbose             Show detailed logs
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const puppeteer = require('puppeteer');
const chalk = require('chalk');
const commander = require('commander');

// Define program and options
const program = new commander.Command();

program
  .name('run-performance-tests')
  .description('Run performance tests for StickForStats')
  .version('1.0.0')
  .option('-d, --device <profile>', 'device profile (desktop, tablet, mobile)', 'desktop')
  .option('-n, --network <profile>', 'network profile (wifi, 4g, 3g)', 'wifi')
  .option('-m, --module <name>', 'test specific module only')
  .option('-i, --iterations <number>', 'number of test iterations', 3)
  .option('-o, --output <file>', 'output file for report', 'performance-report.json')
  .option('--headless', 'run in headless mode', false)
  .option('--ci', 'run in CI mode (adjusts thresholds)', false)
  .option('-v, --verbose', 'show detailed logs', false)
  .parse(process.argv);

const options = program.opts();

// -----------------------------------------------------------------------------
// Constants and Configuration
// -----------------------------------------------------------------------------

// Device Profiles
const DEVICE_PROFILES = {
  desktop: {
    name: 'Desktop',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
  },
  laptop: {
    name: 'Laptop',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 768 },
  },
  tablet: {
    name: 'Tablet',
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1',
    viewport: { width: 768, height: 1024 },
  },
  mobile: {
    name: 'Mobile',
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1',
    viewport: { width: 375, height: 812 },
  }
};

// Network Profiles
const NETWORK_PROFILES = {
  wifi: {
    name: 'WiFi',
    downloadThroughput: 50 * 1024 * 1024 / 8, // 50 Mbps
    uploadThroughput: 20 * 1024 * 1024 / 8,   // 20 Mbps
    latency: 2, // 2 ms
  },
  fast4g: {
    name: 'Fast 4G',
    downloadThroughput: 25 * 1024 * 1024 / 8, // 25 Mbps
    uploadThroughput: 10 * 1024 * 1024 / 8,   // 10 Mbps
    latency: 20, // 20 ms
  },
  slow4g: {
    name: 'Slow 4G',
    downloadThroughput: 5 * 1024 * 1024 / 8,  // 5 Mbps
    uploadThroughput: 2 * 1024 * 1024 / 8,    // 2 Mbps
    latency: 40, // 40 ms
  },
  fast3g: {
    name: 'Fast 3G',
    downloadThroughput: 1.5 * 1024 * 1024 / 8, // 1.5 Mbps
    uploadThroughput: 750 * 1024 / 8,         // 750 Kbps
    latency: 100, // 100 ms
  }
};

// Modules to test
const TEST_MODULES = {
  home: {
    name: 'Home Page',
    path: '/',
    importance: 'high',
  },
  probability: {
    name: 'Probability Distributions',
    path: '/probability-distributions',
    importance: 'high',
  },
  confidence: {
    name: 'Confidence Intervals',
    path: '/confidence-intervals',
    importance: 'high',
  },
  doe: {
    name: 'DOE Analysis',
    path: '/doe-analysis',
    importance: 'medium',
  },
  sqc: {
    name: 'SQC Analysis',
    path: '/sqc-analysis',
    importance: 'medium',
  },
  pca: {
    name: 'PCA Analysis',
    path: '/pca-analysis',
    importance: 'medium',
  },
  workflows: {
    name: 'Workflows',
    path: '/workflows',
    importance: 'low',
  },
  reports: {
    name: 'Reports',
    path: '/reports',
    importance: 'low',
  }
};

// Performance thresholds - these are stricter for development than CI
const THRESHOLDS = options.ci ? {
  // CI environment thresholds (more lenient)
  FCP: 3000,    // First Contentful Paint (ms)
  LCP: 5000,    // Largest Contentful Paint (ms)
  FID: 300,     // First Input Delay (ms)
  CLS: 0.3,     // Cumulative Layout Shift
  TTI: 5000,    // Time to Interactive (ms)
  TBT: 500,     // Total Blocking Time (ms)
  pageLoad: 8000, // Page Load (ms)
  requests: 100,  // Number of network requests
  dataTransfer: 5 * 1024 * 1024 // 5 MB
} : {
  // Development environment thresholds (stricter)
  FCP: 2000,    // First Contentful Paint (ms)
  LCP: 3000,    // Largest Contentful Paint (ms)
  FID: 150,     // First Input Delay (ms)
  CLS: 0.15,    // Cumulative Layout Shift
  TTI: 3500,    // Time to Interactive (ms)
  TBT: 300,     // Total Blocking Time (ms)
  pageLoad: 5000, // Page Load (ms)
  requests: 80,   // Number of network requests
  dataTransfer: 3 * 1024 * 1024 // 3 MB
};

// -----------------------------------------------------------------------------
// Helper Functions
// -----------------------------------------------------------------------------

/**
 * Log message with optional color
 * @param {string} message - Message to log
 * @param {string} type - Log type (info, success, warn, error)
 */
function log(message, type = 'info') {
  // Only log if verbose is enabled or message is important (non-info)
  if (!options.verbose && type === 'info') return;
  
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  
  switch (type) {
    case 'success':
      console.log(chalk.green(`[${timestamp}] ✓ ${message}`));
      break;
    case 'warn':
      console.log(chalk.yellow(`[${timestamp}] ⚠ ${message}`));
      break;
    case 'error':
      console.log(chalk.red(`[${timestamp}] ✖ ${message}`));
      break;
    default:
      console.log(chalk.blue(`[${timestamp}] ℹ ${message}`));
  }
}

/**
 * Get current dev server URL
 * @returns {string} URL of the dev server
 */
function getDevServerUrl() {
  try {
    // Read from package.json
    const packageJson = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json')));
    
    // Check if proxy is set
    const proxy = packageJson.proxy || 'http://localhost:3000';
    
    return proxy;
  } catch (error) {
    log(`Error getting dev server URL: ${error.message}`, 'error');
    return 'http://localhost:3000';
  }
}

/**
 * Ensure development server is running
 */
function ensureDevServer() {
  log('Checking if development server is running...');
  
  try {
    // Simple check to see if server is responding
    execSync(`curl -s -o /dev/null -w "%{http_code}" ${getDevServerUrl()} | grep -q 200`, {
      stdio: options.verbose ? 'inherit' : 'ignore'
    });
    
    log('Development server is running', 'success');
  } catch (error) {
    log('Development server is not running. Please start it first.', 'error');
    process.exit(1);
  }
}

/**
 * Create result directory
 * @param {string} dir - Directory path
 */
function createResultDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    log(`Created results directory: ${dir}`, 'success');
  }
}

/**
 * Calculate average value from an array of numbers
 * @param {Array<number>} values - Array of values
 * @returns {number} Average value
 */
function calculateAverage(values) {
  if (!values || !values.length) return null;
  return values.reduce((sum, val) => sum + val, 0) / values.length;
}

/**
 * Format file size for display
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size string
 */
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

/**
 * Calculate performance score based on metrics
 * @param {Object} metrics - Performance metrics
 * @returns {number} Performance score (0-100)
 */
function calculateScore(metrics) {
  // Define weights for each metric
  const weights = {
    FCP: 0.15,
    LCP: 0.25,
    CLS: 0.15,
    FID: 0.15,
    TTI: 0.10,
    TBT: 0.10,
    requests: 0.05,
    dataTransfer: 0.05
  };
  
  let score = 0;
  let totalWeight = 0;
  
  // Calculate score for each metric
  Object.entries(metrics).forEach(([key, value]) => {
    if (value !== null && weights[key]) {
      const threshold = THRESHOLDS[key];
      let metricScore;
      
      // Higher is worse for all metrics except CLS
      if (key === 'CLS') {
        if (value <= threshold / 2) {
          metricScore = 100; // Perfect
        } else if (value <= threshold) {
          metricScore = 100 - (value - threshold / 2) / (threshold / 2) * 40; // 60-100
        } else {
          metricScore = 60 - Math.min(60, (value - threshold) / threshold * 60); // 0-60
        }
      } else {
        if (value <= threshold / 2) {
          metricScore = 100; // Perfect
        } else if (value <= threshold) {
          metricScore = 100 - (value - threshold / 2) / (threshold / 2) * 40; // 60-100
        } else {
          metricScore = 60 - Math.min(60, (value - threshold) / threshold * 60); // 0-60
        }
      }
      
      score += metricScore * weights[key];
      totalWeight += weights[key];
    }
  });
  
  // Normalize score
  if (totalWeight > 0) {
    score = score / totalWeight;
  }
  
  return Math.round(score);
}

/**
 * Generate recommendations based on metrics
 * @param {Object} metrics - Performance metrics
 * @returns {Array} Array of recommendations
 */
function generateRecommendations(metrics) {
  const recommendations = [];
  
  // Check FCP
  if (metrics.FCP > THRESHOLDS.FCP) {
    recommendations.push({
      metric: 'First Contentful Paint',
      value: `${metrics.FCP.toFixed(0)}ms`,
      recommendation: 'Reduce server response time, eliminate render-blocking resources, or inline critical CSS.'
    });
  }
  
  // Check LCP
  if (metrics.LCP > THRESHOLDS.LCP) {
    recommendations.push({
      metric: 'Largest Contentful Paint',
      value: `${metrics.LCP.toFixed(0)}ms`,
      recommendation: 'Optimize largest image or text block, use resource hints like preload for critical assets.'
    });
  }
  
  // Check CLS
  if (metrics.CLS > THRESHOLDS.CLS) {
    recommendations.push({
      metric: 'Cumulative Layout Shift',
      value: metrics.CLS.toFixed(3),
      recommendation: 'Set image dimensions in HTML, avoid dynamic content insertion, use CSS transform for animations.'
    });
  }
  
  // Check FID
  if (metrics.FID > THRESHOLDS.FID) {
    recommendations.push({
      metric: 'First Input Delay',
      value: `${metrics.FID.toFixed(0)}ms`,
      recommendation: 'Break up long tasks, optimize JavaScript execution, remove unused code, defer non-critical scripts.'
    });
  }
  
  // Check TTI
  if (metrics.TTI > THRESHOLDS.TTI) {
    recommendations.push({
      metric: 'Time to Interactive',
      value: `${metrics.TTI.toFixed(0)}ms`,
      recommendation: 'Reduce JavaScript execution time, defer non-essential scripts, minimize main thread work.'
    });
  }
  
  // Check TBT
  if (metrics.TBT > THRESHOLDS.TBT) {
    recommendations.push({
      metric: 'Total Blocking Time',
      value: `${metrics.TBT.toFixed(0)}ms`,
      recommendation: 'Optimize JavaScript execution, use Web Workers for complex calculations, implement code splitting.'
    });
  }
  
  // Check Requests
  if (metrics.requests > THRESHOLDS.requests) {
    recommendations.push({
      metric: 'Network Requests',
      value: metrics.requests,
      recommendation: 'Reduce number of requests by bundling assets, using sprite sheets, or eliminating unnecessary resources.'
    });
  }
  
  // Check Data Transfer
  if (metrics.dataTransfer > THRESHOLDS.dataTransfer) {
    recommendations.push({
      metric: 'Data Transfer',
      value: formatSize(metrics.dataTransfer),
      recommendation: 'Reduce page weight by optimizing images, enabling text compression, and removing unused code.'
    });
  }
  
  return recommendations;
}

// -----------------------------------------------------------------------------
// Performance Testing Functions
// -----------------------------------------------------------------------------

/**
 * Run performance test for a specific module
 * @param {Object} browser - Puppeteer browser instance
 * @param {Object} moduleConfig - Module configuration
 * @param {Object} deviceProfile - Device profile
 * @param {Object} networkProfile - Network profile
 * @param {number} iterations - Number of iterations
 * @returns {Object} Test results
 */
async function runModuleTest(browser, moduleConfig, deviceProfile, networkProfile, iterations) {
  const results = [];
  
  log(`Testing module: ${moduleConfig.name} (${moduleConfig.path})`);
  
  // Run test for specified number of iterations
  for (let i = 0; i < iterations; i++) {
    log(`Iteration ${i + 1}/${iterations}`);
    
    const page = await browser.newPage();
    
    // Set device profile
    await page.setUserAgent(deviceProfile.userAgent);
    await page.setViewport(deviceProfile.viewport);
    
    // Set network throttling if supported
    if (page.emulateNetworkConditions) {
      await page.emulateNetworkConditions({
        offline: false,
        downloadThroughput: networkProfile.downloadThroughput,
        uploadThroughput: networkProfile.uploadThroughput,
        latency: networkProfile.latency,
      });
    }
    
    // Collect metrics
    const metrics = {};
    
    // Listen for console logs
    page.on('console', (message) => {
      if (options.verbose) {
        console.log(`Console ${message.type()}: ${message.text()}`);
      }
    });
    
    // Start performance tracing
    await page.tracing.start({ path: path.join(process.cwd(), 'temp-trace.json'), categories: ['devtools.timeline'] });
    
    // Record request sizes
    let totalRequests = 0;
    let totalBytes = 0;
    page.on('requestfinished', (request) => {
      totalRequests++;
      const response = request.response();
      if (response) {
        const headers = response.headers();
        const contentLength = headers['content-length'];
        if (contentLength) {
          totalBytes += parseInt(contentLength, 10);
        }
      }
    });
    
    // Navigate to the page and wait for load
    try {
      const baseUrl = getDevServerUrl();
      const startTime = Date.now();
      
      const response = await page.goto(`${baseUrl}${moduleConfig.path}`, { 
        waitUntil: 'networkidle2', 
        timeout: 30000 
      });
      
      if (!response.ok()) {
        log(`Error loading page: ${response.status()} ${response.statusText()}`, 'error');
        await page.close();
        continue;
      }
      
      metrics.pageLoad = Date.now() - startTime;
      
      // Wait a bit for any delayed scripts to execute
      await page.waitForTimeout(1000);
      
      // Stop tracing
      const traceData = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'temp-trace.json'), 'utf8'));
      fs.unlinkSync(path.join(process.cwd(), 'temp-trace.json'));
      
      // Extract web vitals
      try {
        const performanceMetrics = await page.evaluate(() => {
          return {
            // Use the app's performance monitoring if available
            webVitals: window.getMetrics ? window.getMetrics().webVitals : {},
            // Fallback to browser performance API
            navigationTiming: window.performance.getEntriesByType('navigation')[0],
            paintTiming: window.performance.getEntriesByType('paint'),
          };
        });
        
        // Extract metrics from results
        metrics.FCP = performanceMetrics.webVitals.FCP || 
                     performanceMetrics.paintTiming.find(entry => entry.name === 'first-contentful-paint')?.startTime;
        metrics.LCP = performanceMetrics.webVitals.LCP;
        metrics.CLS = performanceMetrics.webVitals.CLS || 0;
        metrics.FID = performanceMetrics.webVitals.FID;
        
        // Additional metrics
        metrics.requests = totalRequests;
        metrics.dataTransfer = totalBytes;
        
        // Calculate TTI and TBT from trace data
        const mainThreadEvents = traceData.traceEvents.filter(
          e => e.cat.includes('devtools.timeline') && 
               e.name === 'FunctionCall' &&
               e.dur > 50000 // 50ms (in microseconds)
        );
        
        const totalBlockingTime = mainThreadEvents.reduce((sum, event) => sum + event.dur / 1000, 0);
        metrics.TBT = totalBlockingTime;
        
        // Estimate TTI based on main thread activity
        const lastLongTask = mainThreadEvents.sort((a, b) => b.ts - a.ts)[0];
        if (lastLongTask) {
          metrics.TTI = (lastLongTask.ts + lastLongTask.dur - traceData.traceEvents[0].ts) / 1000;
        } else {
          metrics.TTI = metrics.pageLoad;
        }
      } catch (error) {
        log(`Error extracting metrics: ${error.message}`, 'error');
      }
      
      // Add result
      results.push(metrics);
      
      // Log metrics for this iteration
      log(`Iteration ${i + 1} results:
  FCP: ${metrics.FCP?.toFixed(0)}ms
  LCP: ${metrics.LCP?.toFixed(0)}ms
  CLS: ${metrics.CLS?.toFixed(3)}
  FID: ${metrics.FID?.toFixed(0)}ms
  TTI: ${metrics.TTI?.toFixed(0)}ms
  TBT: ${metrics.TBT?.toFixed(0)}ms
  Requests: ${metrics.requests}
  Data: ${formatSize(metrics.dataTransfer)}
  Page Load: ${metrics.pageLoad?.toFixed(0)}ms`);
      
    } catch (error) {
      log(`Error testing module ${moduleConfig.name}: ${error.message}`, 'error');
    } finally {
      await page.close();
    }
    
    // Wait between iterations
    if (i < iterations - 1) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  // Calculate averages
  const averages = {
    FCP: calculateAverage(results.map(r => r.FCP).filter(Boolean)),
    LCP: calculateAverage(results.map(r => r.LCP).filter(Boolean)),
    CLS: calculateAverage(results.map(r => r.CLS).filter(Boolean)),
    FID: calculateAverage(results.map(r => r.FID).filter(Boolean)),
    TTI: calculateAverage(results.map(r => r.TTI).filter(Boolean)),
    TBT: calculateAverage(results.map(r => r.TBT).filter(Boolean)),
    pageLoad: calculateAverage(results.map(r => r.pageLoad).filter(Boolean)),
    requests: Math.round(calculateAverage(results.map(r => r.requests).filter(Boolean))),
    dataTransfer: calculateAverage(results.map(r => r.dataTransfer).filter(Boolean)),
  };
  
  // Calculate performance score
  const score = calculateScore(averages);
  
  // Generate recommendations
  const recommendations = generateRecommendations(averages);
  
  return {
    module: moduleConfig.name,
    path: moduleConfig.path,
    device: deviceProfile.name,
    network: networkProfile.name,
    iterations: results.length,
    timestamp: new Date().toISOString(),
    metrics: averages,
    score,
    recommendations,
    rawResults: results,
    pass: score >= 70 && recommendations.length === 0
  };
}

/**
 * Run all performance tests
 */
async function runAllTests() {
  log('Starting performance tests');
  
  // Make sure development server is running
  ensureDevServer();
  
  // Create results directory
  const resultsDir = path.join(process.cwd(), 'performance-results');
  createResultDir(resultsDir);
  
  // Resolve device and network profiles
  const deviceProfile = DEVICE_PROFILES[options.device.toLowerCase()];
  if (!deviceProfile) {
    log(`Unknown device profile: ${options.device}. Using desktop.`, 'warn');
    options.device = 'desktop';
  }
  
  const networkProfile = NETWORK_PROFILES[options.network.toLowerCase()];
  if (!networkProfile) {
    log(`Unknown network profile: ${options.network}. Using wifi.`, 'warn');
    options.network = 'wifi';
  }
  
  // Determine which modules to test
  let modulesToTest = [];
  
  if (options.module) {
    // Test specific module
    const module = Object.values(TEST_MODULES).find(
      m => m.name.toLowerCase() === options.module.toLowerCase() || 
           m.path.includes(options.module.toLowerCase())
    );
    
    if (module) {
      modulesToTest = [module];
    } else {
      log(`Module "${options.module}" not found. Testing all modules.`, 'warn');
      modulesToTest = Object.values(TEST_MODULES);
    }
  } else {
    // Test all modules
    modulesToTest = Object.values(TEST_MODULES);
  }
  
  log(`Testing with device profile: ${DEVICE_PROFILES[options.device.toLowerCase()].name}`);
  log(`Testing with network profile: ${NETWORK_PROFILES[options.network.toLowerCase()].name}`);
  log(`Testing ${modulesToTest.length} modules with ${options.iterations} iterations each`);
  
  // Launch browser
  log('Launching browser');
  const browser = await puppeteer.launch({
    headless: options.headless,
    defaultViewport: null,
    args: ['--no-sandbox', '--disable-web-security']
  });
  
  // Run tests for each module
  const results = [];
  
  for (const moduleConfig of modulesToTest) {
    const result = await runModuleTest(
      browser, 
      moduleConfig, 
      DEVICE_PROFILES[options.device.toLowerCase()],
      NETWORK_PROFILES[options.network.toLowerCase()],
      parseInt(options.iterations, 10)
    );
    
    results.push(result);
    
    // Log test result
    if (result.pass) {
      log(`Module ${moduleConfig.name} passed performance test with score ${result.score}/100`, 'success');
    } else {
      log(`Module ${moduleConfig.name} has performance issues (score: ${result.score}/100)`, 'warn');
      
      // Log recommendations
      result.recommendations.forEach(rec => {
        log(`  - ${rec.metric} (${rec.value}): ${rec.recommendation}`, 'info');
      });
    }
  }
  
  // Close browser
  await browser.close();
  
  // Calculate overall results
  const overallScore = Math.round(results.reduce((sum, r) => sum + r.score, 0) / results.length);
  const overallPass = results.every(r => r.pass);
  
  // Prepare summary
  const summary = {
    timestamp: new Date().toISOString(),
    device: DEVICE_PROFILES[options.device.toLowerCase()].name,
    network: NETWORK_PROFILES[options.network.toLowerCase()].name,
    modulesCount: results.length,
    overallScore,
    pass: overallPass,
    modules: results.map(r => ({
      name: r.module,
      score: r.score,
      pass: r.pass,
      recommendations: r.recommendations.length
    })),
    results
  };
  
  // Save results
  const outputPath = path.join(resultsDir, options.output);
  fs.writeFileSync(outputPath, JSON.stringify(summary, null, 2));
  log(`Results saved to ${outputPath}`, 'success');
  
  // Generate a markdown report
  const reportPath = path.join(resultsDir, options.output.replace('.json', '.md'));
  const report = generateMarkdownReport(summary);
  fs.writeFileSync(reportPath, report);
  log(`Report saved to ${reportPath}`, 'success');
  
  // Final output
  if (overallPass) {
    log(`All performance tests passed with overall score: ${overallScore}/100`, 'success');
  } else {
    log(`Performance testing completed with issues. Overall score: ${overallScore}/100`, 'warn');
    
    // Count total recommendations
    const totalRecs = results.reduce((sum, r) => sum + r.recommendations.length, 0);
    log(`Found ${totalRecs} optimization opportunities. See report for details.`, 'warn');
  }
  
  return summary;
}

/**
 * Generate markdown report
 * @param {Object} summary - Test summary
 * @returns {string} Markdown report
 */
function generateMarkdownReport(summary) {
  const date = new Date(summary.timestamp).toLocaleDateString();
  
  let markdown = `# StickForStats Performance Test Report

## Summary

- **Date:** ${date}
- **Device:** ${summary.device}
- **Network:** ${summary.network}
- **Overall Score:** ${summary.overallScore}/100 ${summary.pass ? '✅' : '⚠️'}
- **Modules Tested:** ${summary.modulesCount}

## Module Scores

| Module | Score | Status |
|--------|-------|--------|
`;

  // Add module scores
  summary.modules.forEach(module => {
    const status = module.pass ? '✅ Pass' : '⚠️ Needs Optimization';
    markdown += `| ${module.name} | ${module.score}/100 | ${status} |\n`;
  });

  // Add detailed results for each module
  markdown += `\n## Detailed Results\n\n`;
  
  summary.results.forEach(result => {
    markdown += `### ${result.module} (Score: ${result.score}/100)\n\n`;
    
    // Add metrics table
    markdown += `**Performance Metrics:**\n\n`;
    markdown += `| Metric | Value | Threshold | Status |\n`;
    markdown += `|--------|-------|-----------|--------|\n`;
    
    const metrics = [
      { name: 'First Contentful Paint (FCP)', value: `${Math.round(result.metrics.FCP)}ms`, threshold: `${THRESHOLDS.FCP}ms` },
      { name: 'Largest Contentful Paint (LCP)', value: `${Math.round(result.metrics.LCP)}ms`, threshold: `${THRESHOLDS.LCP}ms` },
      { name: 'Cumulative Layout Shift (CLS)', value: result.metrics.CLS.toFixed(3), threshold: THRESHOLDS.CLS.toFixed(2) },
      { name: 'First Input Delay (FID)', value: `${Math.round(result.metrics.FID)}ms`, threshold: `${THRESHOLDS.FID}ms` },
      { name: 'Time to Interactive (TTI)', value: `${Math.round(result.metrics.TTI)}ms`, threshold: `${THRESHOLDS.TTI}ms` },
      { name: 'Total Blocking Time (TBT)', value: `${Math.round(result.metrics.TBT)}ms`, threshold: `${THRESHOLDS.TBT}ms` },
      { name: 'Network Requests', value: result.metrics.requests, threshold: THRESHOLDS.requests },
      { name: 'Data Transfer', value: formatSize(result.metrics.dataTransfer), threshold: formatSize(THRESHOLDS.dataTransfer) },
      { name: 'Page Load', value: `${Math.round(result.metrics.pageLoad)}ms`, threshold: `${THRESHOLDS.pageLoad}ms` },
    ];
    
    metrics.forEach(metric => {
      const numericValue = parseFloat(metric.value);
      const numericThreshold = parseFloat(metric.threshold);
      let status = '✅';
      
      if (metric.name.includes('CLS')) {
        status = numericValue <= numericThreshold ? '✅' : '⚠️';
      } else if (!isNaN(numericValue) && !isNaN(numericThreshold)) {
        status = numericValue <= numericThreshold ? '✅' : '⚠️';
      }
      
      markdown += `| ${metric.name} | ${metric.value} | ${metric.threshold} | ${status} |\n`;
    });
    
    // Add recommendations if any
    if (result.recommendations.length > 0) {
      markdown += `\n**Recommendations:**\n\n`;
      
      result.recommendations.forEach(rec => {
        markdown += `- **${rec.metric} (${rec.value}):** ${rec.recommendation}\n`;
      });
    }
    
    markdown += '\n';
  });
  
  // Add footnote
  markdown += `\n## How to Improve Performance

1. Address the recommendations listed above, focusing on modules with lower scores first.
2. Run performance tests regularly to track improvements.
3. Test on multiple device and network profiles to ensure good performance across all conditions.
4. Refer to the [Web Vitals documentation](https://web.dev/vitals/) for more information.

---

Generated on ${new Date().toLocaleString()} using StickForStats Performance Test Suite.`;

  return markdown;
}

// -----------------------------------------------------------------------------
// Main Execution
// -----------------------------------------------------------------------------

// Run tests
runAllTests()
  .then(summary => {
    log(`Performance testing completed with overall score: ${summary.overallScore}/100`, 'success');
    process.exit(0);
  })
  .catch(error => {
    log(`Error running performance tests: ${error.message}`, 'error');
    process.exit(1);
  });