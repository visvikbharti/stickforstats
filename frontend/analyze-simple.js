#!/usr/bin/env node

/**
 * analyze-simple.js
 * 
 * A simplified script to analyze the webpack bundle structure
 * without requiring a full production build.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Create report directory if it doesn't exist
const reportDir = path.resolve(__dirname, 'bundle-reports');
if (!fs.existsSync(reportDir)) {
  fs.mkdirSync(reportDir, { recursive: true });
}

// Get current date formatted as YYYY-MM-DD
const getFormattedDate = () => {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};

// Create report filename
const reportFileName = `bundle-report-simple-${getFormattedDate()}.html`;
const reportPath = path.join(reportDir, reportFileName);

console.log('\n📊 Starting simplified bundle analysis...');
console.log('----------------------------------------');

try {
  // Create development build with source maps for analysis
  console.log('🔨 Building development bundle with source maps...');
  execSync('GENERATE_SOURCEMAP=true react-scripts build --profile', { stdio: 'inherit' });
  
  // Run source-map-explorer for analysis
  console.log('\n🔍 Running source-map-explorer...');
  execSync(`source-map-explorer --html "${reportPath}" "build/static/js/*.js"`, { stdio: 'inherit' });
  
  console.log('\n✅ Simple bundle analysis complete!');
  console.log(`📋 Report saved to: ${reportPath}`);
  
  // Provide a basic summary of the build
  const jsFiles = fs.readdirSync('build/static/js');
  let totalSize = 0;
  
  console.log('\n📦 Bundle Size Summary:');
  console.log('---------------------');
  console.log('JavaScript files:');
  
  jsFiles.forEach(file => {
    const stats = fs.statSync(`build/static/js/${file}`);
    const fileSizeKB = (stats.size / 1024).toFixed(2);
    totalSize += stats.size;
    console.log(`- ${file}: ${fileSizeKB} KB`);
  });
  
  const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);
  console.log(`\nTotal JS bundle size: ${totalSizeMB} MB`);
  
} catch (error) {
  console.error('\n❌ Error during bundle analysis:', error.message);
  process.exit(1);
}

console.log('\n🚀 Done!');