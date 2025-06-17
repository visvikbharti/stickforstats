#!/usr/bin/env node

/**
 * Simplified Performance Testing Script
 * 
 * This script runs a simplified version of the performance tests for StickForStats
 * without requiring Puppeteer. It uses browser APIs directly when run in a browser environment.
 * 
 * Usage:
 *   node scripts/simplified-performance-test.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk') || { green: (t) => t, red: (t) => t, yellow: (t) => t, blue: (t) => t };

// Check if chalk is available, otherwise provide fallback
function safeLog(message, type = 'info') {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  
  if (chalk) {
    switch (type) {
      case 'success':
        console.log(`[${timestamp}] ✓ ${message}`);
        break;
      case 'warn':
        console.log(`[${timestamp}] ⚠ ${message}`);
        break;
      case 'error':
        console.log(`[${timestamp}] ✖ ${message}`);
        break;
      default:
        console.log(`[${timestamp}] ℹ ${message}`);
    }
  } else {
    console.log(`[${timestamp}] ${message}`);
  }
}

// Run a bundle analysis
function analyzeBundleSize() {
  safeLog('Analyzing bundle size...');
  
  try {
    // Check if build directory exists
    const buildDir = path.join(process.cwd(), 'build');
    
    if (!fs.existsSync(buildDir)) {
      safeLog('Build directory not found. Building project first...', 'warn');
      try {
        execSync('npm run build', { stdio: 'inherit' });
      } catch (error) {
        safeLog('Failed to build project. Please build the project first with "npm run build"', 'error');
        return false;
      }
    }
    
    // Check for JS files in build/static/js
    const jsDir = path.join(buildDir, 'static', 'js');
    
    if (!fs.existsSync(jsDir)) {
      safeLog('JavaScript bundle directory not found. The build may be incomplete.', 'error');
      return false;
    }
    
    // Read all JS files
    const jsFiles = fs.readdirSync(jsDir).filter(file => file.endsWith('.js'));
    
    if (jsFiles.length === 0) {
      safeLog('No JavaScript bundles found. The build may be incomplete.', 'error');
      return false;
    }
    
    // Analyze sizes
    const fileSizes = jsFiles.map(file => {
      const filePath = path.join(jsDir, file);
      const stats = fs.statSync(filePath);
      return {
        name: file,
        size: stats.size,
        sizeKB: Math.round(stats.size / 1024),
        sizeMB: (stats.size / (1024 * 1024)).toFixed(2)
      };
    });
    
    // Sort by size descending
    fileSizes.sort((a, b) => b.size - a.size);
    
    // Calculate total size
    const totalSize = fileSizes.reduce((sum, file) => sum + file.size, 0);
    const totalSizeKB = Math.round(totalSize / 1024);
    const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);
    
    // Report sizes
    safeLog('Bundle size analysis complete', 'success');
    safeLog(`Total bundle size: ${totalSizeMB} MB (${totalSizeKB} KB)`, 'info');
    
    console.log('\nBundle size breakdown:');
    fileSizes.forEach(file => {
      const percentOfTotal = ((file.size / totalSize) * 100).toFixed(1);
      console.log(`${file.name}: ${file.sizeMB} MB (${file.sizeKB} KB) - ${percentOfTotal}% of total bundle`);
    });
    
    // Provide recommendations
    console.log('\nRecommendations:');
    
    if (totalSizeKB > 1000) {
      safeLog('Your bundle size is larger than recommended (1000 KB). Consider implementing code splitting or removing unused dependencies.', 'warn');
    } else {
      safeLog('Your bundle size is within the recommended range.', 'success');
    }
    
    // Look for large chunks
    const largeChunks = fileSizes.filter(file => file.sizeKB > 300);
    
    if (largeChunks.length > 0) {
      safeLog(`Found ${largeChunks.length} large bundle chunks that could be optimized:`, 'warn');
      largeChunks.forEach(file => {
        console.log(`- ${file.name}: ${file.sizeMB} MB (${file.sizeKB} KB)`);
      });
      
      console.log('\nSuggestions:');
      console.log('1. Implement code splitting based on routes');
      console.log('2. Lazy load non-critical components');
      console.log('3. Check for unused dependencies with npm package "depcheck"');
      console.log('4. Use specific imports for large libraries (e.g., import Button from "@mui/material/Button" instead of import {Button} from "@mui/material")');
      console.log('5. Consider using smaller alternatives for large packages (e.g., date-fns instead of moment)');
    }
    
    // Create results directory if it doesn't exist
    const resultsDir = path.join(process.cwd(), 'performance-results');
    
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    
    // Write results to file
    const resultsFilePath = path.join(resultsDir, 'bundle-analysis.json');
    fs.writeFileSync(
      resultsFilePath,
      JSON.stringify({
        timestamp: new Date().toISOString(),
        totalSize,
        totalSizeKB,
        totalSizeMB,
        bundles: fileSizes,
        recommendations: totalSizeKB > 1000 ? [
          'Implement code splitting based on routes',
          'Lazy load non-critical components',
          'Check for unused dependencies',
          'Use specific imports for large libraries',
          'Consider smaller alternatives for large packages'
        ] : ['Bundle size is within recommended range']
      }, null, 2)
    );
    
    safeLog(`Results saved to ${resultsFilePath}`, 'success');
    
    return true;
  } catch (error) {
    safeLog(`Error analyzing bundle size: ${error.message}`, 'error');
    return false;
  }
}

// Check for resource-intensive components using static analysis
function analyzeCssComplexity() {
  safeLog('Analyzing CSS complexity...');
  
  try {
    // Check for CSS files
    const srcDir = path.join(process.cwd(), 'src');
    const cssFiles = [];
    
    // Simple recursive function to find all CSS files
    function findCssFiles(directory) {
      const files = fs.readdirSync(directory);
      
      files.forEach(file => {
        const filePath = path.join(directory, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isDirectory()) {
          findCssFiles(filePath);
        } else if (file.endsWith('.css')) {
          cssFiles.push(filePath);
        }
      });
    }
    
    findCssFiles(srcDir);
    
    if (cssFiles.length === 0) {
      safeLog('No CSS files found. Skipping CSS complexity analysis.', 'warn');
      return false;
    }
    
    // Analyze CSS files
    const cssAnalysis = cssFiles.map(filePath => {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);
      
      // Simple metrics
      const lines = content.split('\n').length;
      const selectorCount = (content.match(/\{/g) || []).length;
      const mediaQueryCount = (content.match(/@media/g) || []).length;
      const important = (content.match(/\!important/g) || []).length;
      const nestedSelectors = (content.match(/\s+>\s+/g) || []).length;
      const fileSize = Math.round(content.length / 1024); // KB
      
      // Check for potential issues
      const complexSelectors = content.split(/[{;}]/).filter(line => {
        const selectorText = line.trim();
        return selectorText && !selectorText.startsWith('@') && selectorText.split(/\s+/).length > 4;
      });
      
      return {
        path: relativePath,
        fileSize,
        lines,
        selectorCount,
        mediaQueryCount,
        important,
        nestedSelectors,
        complexSelectorCount: complexSelectors.length,
        complexSelectors: complexSelectors.slice(0, 5), // Just show a few examples
        score: Math.min(100, Math.max(0, 100 - important * 2 - complexSelectors.length * 5 - (fileSize > 100 ? 20 : 0)))
      };
    });
    
    // Sort by score (lower scores first)
    cssAnalysis.sort((a, b) => a.score - b.score);
    
    // Report findings
    safeLog('CSS complexity analysis complete', 'success');
    
    console.log('\nCSS Complexity Report:');
    cssAnalysis.forEach(file => {
      console.log(`\n${file.path} (Score: ${file.score}/100):`);
      console.log(`- File size: ${file.fileSize} KB`);
      console.log(`- Lines: ${file.lines}`);
      console.log(`- Selectors: ${file.selectorCount}`);
      console.log(`- Media queries: ${file.mediaQueryCount}`);
      console.log(`- !important declarations: ${file.important}`);
      console.log(`- Nested selectors: ${file.nestedSelectors}`);
      console.log(`- Complex selectors: ${file.complexSelectorCount}`);
      
      if (file.complexSelectorCount > 0 && file.complexSelectors.length > 0) {
        console.log('- Examples of complex selectors:');
        file.complexSelectors.forEach(selector => {
          console.log(`  * ${selector.trim()}`);
        });
      }
    });
    
    // Create recommendations
    const recommendations = [];
    
    if (cssAnalysis.some(file => file.important > 0)) {
      recommendations.push('Avoid using !important declarations as they make CSS harder to maintain');
    }
    
    if (cssAnalysis.some(file => file.complexSelectorCount > 0)) {
      recommendations.push('Simplify complex CSS selectors to improve rendering performance');
    }
    
    if (cssAnalysis.some(file => file.fileSize > 100)) {
      recommendations.push('Consider splitting large CSS files into smaller, more focused modules');
    }
    
    if (cssAnalysis.some(file => file.mediaQueryCount > 10)) {
      recommendations.push('Consolidate media queries to reduce redundancy');
    }
    
    if (recommendations.length > 0) {
      console.log('\nRecommendations:');
      recommendations.forEach(rec => console.log(`- ${rec}`));
    }
    
    // Create results directory if it doesn't exist
    const resultsDir = path.join(process.cwd(), 'performance-results');
    
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    
    // Write results to file
    const resultsFilePath = path.join(resultsDir, 'css-analysis.json');
    fs.writeFileSync(
      resultsFilePath,
      JSON.stringify({
        timestamp: new Date().toISOString(),
        files: cssAnalysis,
        recommendations
      }, null, 2)
    );
    
    safeLog(`Results saved to ${resultsFilePath}`, 'success');
    
    return true;
  } catch (error) {
    safeLog(`Error analyzing CSS complexity: ${error.message}`, 'error');
    return false;
  }
}

// Identify large component files
function analyzeComponentComplexity() {
  safeLog('Analyzing component complexity...');
  
  try {
    // Look for React component files
    const srcDir = path.join(process.cwd(), 'src');
    const componentFiles = [];
    
    // Simple recursive function to find React component files
    function findComponentFiles(directory) {
      const files = fs.readdirSync(directory);
      
      files.forEach(file => {
        const filePath = path.join(directory, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isDirectory()) {
          findComponentFiles(filePath);
        } else if (
          file.endsWith('.js') || 
          file.endsWith('.jsx') || 
          file.endsWith('.ts') || 
          file.endsWith('.tsx')
        ) {
          // Read file content to check if it's a component
          const content = fs.readFileSync(filePath, 'utf8');
          
          // Very simple heuristic - check for React imports and component patterns
          if (
            (content.includes('import React') || content.includes('from "react"') || content.includes("from 'react'")) &&
            (content.includes('function ') || content.includes('class ') || content.includes('=>')) &&
            (content.includes('return (') || content.includes('render() {'))
          ) {
            componentFiles.push(filePath);
          }
        }
      });
    }
    
    findComponentFiles(srcDir);
    
    if (componentFiles.length === 0) {
      safeLog('No React component files found.', 'warn');
      return false;
    }
    
    // Analyze component files
    const componentAnalysis = componentFiles.map(filePath => {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);
      const fileName = path.basename(filePath);
      
      // Simple metrics
      const lines = content.split('\n').length;
      const renderReturns = (content.match(/return\s*\(/g) || []).length;
      const stateHooks = (content.match(/useState\(/g) || []).length;
      const effectHooks = (content.match(/useEffect\(/g) || []).length;
      const memoHooks = (content.match(/useMemo\(/g) || []).length + (content.match(/useCallback\(/g) || []).length;
      const jsxElements = (content.match(/<[A-Z][A-Za-z0-9]*/g) || []).length;
      const fileSize = Math.round(content.length / 1024); // KB
      
      // Check for optimization potential
      const hasMemo = content.includes('React.memo') || content.includes('memo(');
      const hasUseMemo = content.includes('useMemo(');
      const hasUseCallback = content.includes('useCallback(');
      
      let complexity = 'low';
      if (lines > 500 || jsxElements > 50 || stateHooks + effectHooks > 10) {
        complexity = 'high';
      } else if (lines > 300 || jsxElements > 30 || stateHooks + effectHooks > 5) {
        complexity = 'medium';
      }
      
      return {
        path: relativePath,
        fileName,
        fileSize,
        lines,
        stateHooks,
        effectHooks,
        memoHooks,
        jsxElements,
        renderReturns,
        hasMemo,
        hasUseMemo,
        hasUseCallback,
        complexity
      };
    });
    
    // Sort by complexity
    componentAnalysis.sort((a, b) => {
      const complexityOrder = { high: 3, medium: 2, low: 1 };
      return complexityOrder[b.complexity] - complexityOrder[a.complexity];
    });
    
    // Report findings
    safeLog('Component complexity analysis complete', 'success');
    
    const highComplexity = componentAnalysis.filter(c => c.complexity === 'high');
    const mediumComplexity = componentAnalysis.filter(c => c.complexity === 'medium');
    
    console.log('\nComponent Complexity Report:');
    console.log(`\nFound ${highComplexity.length} high complexity components`);
    console.log(`Found ${mediumComplexity.length} medium complexity components`);
    console.log(`Found ${componentAnalysis.length - highComplexity.length - mediumComplexity.length} low complexity components`);
    
    if (highComplexity.length > 0) {
      console.log('\nHigh complexity components:');
      highComplexity.forEach(comp => {
        console.log(`\n${comp.path}:`);
        console.log(`- File size: ${comp.fileSize} KB`);
        console.log(`- Lines: ${comp.lines}`);
        console.log(`- State hooks: ${comp.stateHooks}`);
        console.log(`- Effect hooks: ${comp.effectHooks}`);
        console.log(`- Memo hooks: ${comp.memoHooks}`);
        console.log(`- JSX elements: ${comp.jsxElements}`);
        console.log(`- Uses memo: ${comp.hasMemo ? 'Yes' : 'No'}`);
        console.log(`- Uses useMemo: ${comp.hasUseMemo ? 'Yes' : 'No'}`);
        console.log(`- Uses useCallback: ${comp.hasUseCallback ? 'Yes' : 'No'}`);
      });
    }
    
    // Create recommendations
    const recommendations = [];
    
    if (highComplexity.length > 0) {
      recommendations.push('Break down high complexity components into smaller, more focused components');
    }
    
    if (componentAnalysis.some(c => c.lines > 500)) {
      recommendations.push('Split very large components (>500 lines) into multiple components');
    }
    
    if (componentAnalysis.some(c => c.stateHooks > 5)) {
      recommendations.push('Consider using useReducer for components with many state variables');
    }
    
    if (componentAnalysis.some(c => c.complexity !== 'low' && !c.hasMemo)) {
      recommendations.push('Use React.memo for non-trivial components to prevent unnecessary rerenders');
    }
    
    if (componentAnalysis.some(c => c.jsxElements > 30 && c.renderReturns === 1)) {
      recommendations.push('Split components with many JSX elements into smaller sub-components');
    }
    
    if (recommendations.length > 0) {
      console.log('\nRecommendations:');
      recommendations.forEach(rec => console.log(`- ${rec}`));
    }
    
    // Create results directory if it doesn't exist
    const resultsDir = path.join(process.cwd(), 'performance-results');
    
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    
    // Write results to file
    const resultsFilePath = path.join(resultsDir, 'component-analysis.json');
    fs.writeFileSync(
      resultsFilePath,
      JSON.stringify({
        timestamp: new Date().toISOString(),
        components: componentAnalysis,
        recommendations
      }, null, 2)
    );
    
    safeLog(`Results saved to ${resultsFilePath}`, 'success');
    
    return true;
  } catch (error) {
    safeLog(`Error analyzing component complexity: ${error.message}`, 'error');
    return false;
  }
}

// Generate a comprehensive report combining all analyses
function generateFullReport() {
  try {
    // Create results directory if it doesn't exist
    const resultsDir = path.join(process.cwd(), 'performance-results');
    
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    
    // Check if individual analysis files exist
    const bundleAnalysisPath = path.join(resultsDir, 'bundle-analysis.json');
    const cssAnalysisPath = path.join(resultsDir, 'css-analysis.json');
    const componentAnalysisPath = path.join(resultsDir, 'component-analysis.json');
    
    let bundleAnalysis = null;
    let cssAnalysis = null;
    let componentAnalysis = null;
    
    if (fs.existsSync(bundleAnalysisPath)) {
      bundleAnalysis = JSON.parse(fs.readFileSync(bundleAnalysisPath, 'utf8'));
    }
    
    if (fs.existsSync(cssAnalysisPath)) {
      cssAnalysis = JSON.parse(fs.readFileSync(cssAnalysisPath, 'utf8'));
    }
    
    if (fs.existsSync(componentAnalysisPath)) {
      componentAnalysis = JSON.parse(fs.readFileSync(componentAnalysisPath, 'utf8'));
    }
    
    // If no analyses were run, return false
    if (!bundleAnalysis && !cssAnalysis && !componentAnalysis) {
      safeLog('No analysis results found. Cannot generate full report.', 'error');
      return false;
    }
    
    // Generate a markdown report
    let markdown = `# StickForStats Performance Analysis Report

## Summary

**Date:** ${new Date().toISOString().split('T')[0]}

`;
    
    // Add bundle analysis section
    if (bundleAnalysis) {
      markdown += `### Bundle Size Analysis

Total bundle size: **${bundleAnalysis.totalSizeMB} MB** (${bundleAnalysis.totalSizeKB} KB)

${bundleAnalysis.totalSizeKB > 1000 ? '⚠️ **Warning:** Your bundle size exceeds the recommended maximum of 1000 KB.' : '✅ Your bundle size is within the recommended range.'}

#### Largest Bundles:

${bundleAnalysis.bundles.slice(0, 5).map(bundle => 
  `- ${bundle.name}: ${bundle.sizeMB} MB (${bundle.sizeKB} KB) - ${((bundle.size / bundleAnalysis.totalSize) * 100).toFixed(1)}% of total`
).join('\n')}

#### Recommendations:

${bundleAnalysis.recommendations.map(rec => `- ${rec}`).join('\n')}

`;
    }
    
    // Add CSS analysis section
    if (cssAnalysis) {
      const problemCssFiles = cssAnalysis.files.filter(file => file.score < 80);
      
      markdown += `### CSS Complexity Analysis

${problemCssFiles.length > 0 
  ? `Found **${problemCssFiles.length} CSS files** with potential performance issues.` 
  : 'CSS analysis shows no significant issues.'}

${problemCssFiles.length > 0 ? `#### CSS Files with Issues:

${problemCssFiles.slice(0, 5).map(file => 
  `- **${file.path}** (Score: ${file.score}/100)
  - ${file.fileSize} KB, ${file.selectorCount} selectors, ${file.important} !important declarations
  - ${file.complexSelectorCount} complex selectors identified`
).join('\n\n')}
` : ''}

${cssAnalysis.recommendations.length > 0 ? `#### Recommendations:

${cssAnalysis.recommendations.map(rec => `- ${rec}`).join('\n')}
` : ''}

`;
    }
    
    // Add component analysis section
    if (componentAnalysis) {
      const highComplexity = componentAnalysis.components.filter(c => c.complexity === 'high');
      
      markdown += `### Component Complexity Analysis

${highComplexity.length > 0 
  ? `Found **${highComplexity.length} high complexity components** that could impact performance.` 
  : 'No high complexity components found.'}

${highComplexity.length > 0 ? `#### High Complexity Components:

${highComplexity.slice(0, 5).map(comp => 
  `- **${comp.path}**
  - ${comp.fileSize} KB, ${comp.lines} lines
  - ${comp.stateHooks} state hooks, ${comp.effectHooks} effect hooks
  - ${comp.jsxElements} JSX elements
  - Optimization: ${[
    comp.hasMemo ? 'Uses memo' : 'No memo', 
    comp.hasUseMemo ? 'Uses useMemo' : 'No useMemo', 
    comp.hasUseCallback ? 'Uses useCallback' : 'No useCallback'
  ].join(', ')}`
).join('\n\n')}
` : ''}

${componentAnalysis.recommendations.length > 0 ? `#### Recommendations:

${componentAnalysis.recommendations.map(rec => `- ${rec}`).join('\n')}
` : ''}

`;
    }
    
    // Overall recommendations and next steps
    markdown += `## Overall Recommendations

${[
  ...(bundleAnalysis?.recommendations || []),
  ...(cssAnalysis?.recommendations || []),
  ...(componentAnalysis?.recommendations || []),
].filter((rec, index, self) => self.indexOf(rec) === index) // Remove duplicates
  .map(rec => `- ${rec}`)
  .join('\n')}

## Next Steps

1. Review the detailed analysis files in the \`performance-results\` directory
2. Prioritize high-impact optimizations (bundle size and high complexity components first)
3. Implement optimizations and re-run the analysis to measure improvements
4. Consider implementing the web performance monitoring utilities in src/utils/performanceMonitoring.js

---

Report generated on ${new Date().toISOString()} with the StickForStats simplified performance testing script.
`;
    
    // Write markdown to file
    const reportPath = path.join(resultsDir, 'performance-report.md');
    fs.writeFileSync(reportPath, markdown);
    
    safeLog(`Complete report saved to ${reportPath}`, 'success');
    console.log('\nSummary of findings:');
    
    // Count issues
    const issuesCount = [
      bundleAnalysis && bundleAnalysis.totalSizeKB > 1000 ? 1 : 0,
      cssAnalysis && cssAnalysis.files.filter(file => file.score < 80).length > 0 ? 1 : 0,
      componentAnalysis && componentAnalysis.components.filter(c => c.complexity === 'high').length > 0 ? 1 : 0
    ].reduce((a, b) => a + b, 0);
    
    if (issuesCount === 0) {
      safeLog('No major performance issues found. Good job!', 'success');
    } else {
      safeLog(`Found ${issuesCount} areas for improvement. See the full report for details.`, 'warn');
    }
    
    return true;
  } catch (error) {
    safeLog(`Error generating full report: ${error.message}`, 'error');
    return false;
  }
}

// Main function to run the performance tests
async function runTests() {
  safeLog('Starting simplified performance tests for StickForStats');
  
  // Create results directory if it doesn't exist
  const resultsDir = path.join(process.cwd(), 'performance-results');
  
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  // Run the various analyses
  const bundleResult = analyzeBundleSize();
  const cssResult = analyzeCssComplexity();
  const componentResult = analyzeComponentComplexity();
  
  // Generate full report
  if (bundleResult || cssResult || componentResult) {
    generateFullReport();
  }
  
  safeLog('Performance tests complete. Results are saved in the performance-results directory.', 'success');
}

// Run the tests
runTests().catch(error => {
  safeLog(`Error running tests: ${error.message}`, 'error');
  process.exit(1);
});