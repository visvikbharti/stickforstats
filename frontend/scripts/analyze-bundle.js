#!/usr/bin/env node

/**
 * analyze-bundle.js
 * 
 * A script to analyze the webpack bundle of the StickForStats frontend.
 * This script runs a production build with the ANALYZE environment variable set,
 * which triggers the webpack-bundle-analyzer plugin to generate interactive visualizations.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Output directory for reports
const REPORT_DIR = path.resolve(__dirname, '../bundle-reports');

// Ensure reports directory exists
if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

// Get current date formatted as YYYY-MM-DD for report naming
const getFormattedDate = () => {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};

// Create report filename with timestamp
const reportFileName = `bundle-report-${getFormattedDate()}.html`;
const reportPath = path.join(REPORT_DIR, reportFileName);

console.log('\n📊 Starting bundle analysis...');
console.log('------------------------------');

try {
  // Create production build with source maps for analysis
  console.log('🔨 Building production bundle with source maps...');
  execSync('GENERATE_SOURCEMAP=true npm run build', { stdio: 'inherit' });
  
  // Run source-map-explorer for detailed analysis
  console.log('\n🔍 Running source-map-explorer...');
  execSync(`source-map-explorer --html "${reportPath}" "build/static/js/*.js"`, { stdio: 'inherit' });
  
  // Run webpack bundle analyzer
  console.log('\n🧩 Running webpack bundle analyzer...');
  execSync('ANALYZE=true npx craco build', { stdio: 'inherit' });
  
  console.log('\n✅ Bundle analysis complete!');
  console.log(`📋 Report saved to: ${reportPath}`);
  console.log('\nKey insights:');
  console.log('- Check individual chunk sizes in the report');
  console.log('- Look for duplicated dependencies across chunks');
  console.log('- Identify large modules that could be further optimized');
  console.log('- Review unused exports from libraries that might be tree-shaken');
  
} catch (error) {
  console.error('\n❌ Error during bundle analysis:', error.message);
  process.exit(1);
}

// Provide a summary of the build
try {
  console.log('\n📦 Bundle Size Summary:');
  console.log('---------------------');
  
  // List JS files with sizes
  const jsFiles = fs.readdirSync('build/static/js');
  let totalSize = 0;
  
  console.log('JavaScript files:');
  jsFiles.forEach(file => {
    const stats = fs.statSync(`build/static/js/${file}`);
    const fileSizeKB = (stats.size / 1024).toFixed(2);
    totalSize += stats.size;
    console.log(`- ${file}: ${fileSizeKB} KB`);
  });
  
  // Calculate total bundle size
  const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);
  console.log(`\nTotal JS bundle size: ${totalSizeMB} MB`);
  
  // Suggestion based on bundle size
  if (totalSize > 2 * 1024 * 1024) {
    console.log('\n⚠️ Bundle size exceeds 2MB. Consider additional optimizations:');
    console.log('- Review large dependencies in the analyzer report');
    console.log('- Add more granular code-splitting');
    console.log('- Check for unused features from imported libraries');
  } else {
    console.log('\n✅ Bundle size is acceptable.');
  }
  
} catch (error) {
  console.error('\n⚠️ Error generating bundle summary:', error.message);
}

console.log('\n🚀 Done!');