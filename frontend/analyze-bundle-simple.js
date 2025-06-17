#!/usr/bin/env node

/**
 * analyze-bundle-simple.js
 * 
 * A simplified script to analyze the bundle without requiring full build
 */

const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Output directory for reports
const REPORT_DIR = path.resolve(__dirname, 'bundle-reports');

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
  // Run interactive webpack bundle analyzer
  console.log('\n🧩 Running webpack bundle analyzer...');
  execSync('ANALYZE=true npx craco build', { 
    stdio: 'inherit',
    env: { ...process.env, GENERATE_SOURCEMAP: 'true', ANALYZE: 'true' }
  });
  
  console.log('\n✅ Bundle analysis complete!');
  
} catch (error) {
  console.error('\n❌ Error during bundle analysis:', error.message);
  console.log('\n⚠️ Trying alternative approach with source-map-explorer...');
  
  try {
    // Alternative: Build with react-scripts and analyze with source-map-explorer
    execSync('npx react-scripts build', { 
      stdio: 'inherit',
      env: { ...process.env, GENERATE_SOURCEMAP: 'true' } 
    });
    
    execSync(`npx source-map-explorer --html "${reportPath}" "build/static/js/*.js"`, {
      stdio: 'inherit'
    });
    
    console.log(`\n✅ Alternative analysis complete! Report saved to: ${reportPath}`);
    
  } catch (err) {
    console.error('\n❌ Both analysis methods failed:', err.message);
    process.exit(1);
  }
}

// Provide a summary if build directory exists
if (fs.existsSync('build/static/js')) {
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
    
  } catch (error) {
    console.error('\n⚠️ Error generating bundle summary:', error.message);
  }
}

console.log('\n🚀 Done!');