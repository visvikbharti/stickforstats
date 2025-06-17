#!/usr/bin/env node

/**
 * optimize-dependencies.js
 * 
 * A utility script to help optimize dependencies in the StickForStats frontend.
 * This script:
 * 1. Analyzes current bundle size
 * 2. Installs specific D3 modules to replace full D3 package
 * 3. Updates package.json with optimized dependencies
 * 4. Creates utility files for optimized imports
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

// Configuration
const ROOT_DIR = path.resolve(__dirname, '..');
const UTILS_DIR = path.join(ROOT_DIR, 'src/utils');

// Ensure utils directory exists
if (!fs.existsSync(UTILS_DIR)) {
  fs.mkdirSync(UTILS_DIR, { recursive: true });
}

// Helper for console output
const log = {
  info: (msg) => console.log(chalk.blue('INFO: ') + msg),
  success: (msg) => console.log(chalk.green('SUCCESS: ') + msg),
  warning: (msg) => console.log(chalk.yellow('WARNING: ') + msg),
  error: (msg) => console.log(chalk.red('ERROR: ') + msg),
  step: (msg) => console.log(chalk.cyan('\n== ' + msg + ' =='))
};

// Function to run shell commands
const runCommand = (command) => {
  try {
    return execSync(command, { stdio: 'inherit', cwd: ROOT_DIR });
  } catch (error) {
    log.error(`Failed to execute command: ${command}`);
    throw error;
  }
};

// Main function
async function main() {
  log.step('Starting dependency optimization');
  
  // Analyze current bundle
  log.info('Analyzing current bundle size...');
  try {
    runCommand('npm run build:analyze');
    log.success('Bundle analysis complete. Review the report to identify areas for improvement.');
  } catch (error) {
    log.warning('Unable to analyze bundle. Continuing with optimization...');
  }
  
  // Install optimized D3 modules
  log.step('Installing optimized D3 modules');
  log.info('Replacing full D3 package with specific modules...');
  
  try {
    runCommand('npm uninstall d3');
    runCommand('npm install --save d3-selection d3-scale d3-axis d3-shape d3-format d3-time-format d3-array d3-transition d3-ease d3-scale-chromatic d3-brush d3-hierarchy d3-force');
    log.success('D3 modules installed successfully');
  } catch (error) {
    log.error('Failed to install D3 modules. You may need to do this manually.');
  }
  
  // Copy utility files
  log.step('Creating utility files for optimized imports');
  
  const utilFiles = [
    { 
      name: 'd3Imports.js', 
      description: 'D3.js import optimization utilities'
    },
    { 
      name: 'muiImports.js', 
      description: 'Material UI import optimization utilities'
    },
    { 
      name: 'mathRendering.js', 
      description: 'Math formula rendering optimization'
    },
    { 
      name: 'animationUtils.js', 
      description: 'Animation optimization utilities'
    },
    { 
      name: 'chartUtils.js', 
      description: 'Chart and visualization optimization utilities'
    }
  ];
  
  // Copy example source files from their optimized versions
  utilFiles.forEach(file => {
    const sourcePath = path.join(__dirname, '../src/utils', file.name);
    const destPath = path.join(UTILS_DIR, file.name);
    
    try {
      if (fs.existsSync(sourcePath)) {
        fs.copyFileSync(sourcePath, destPath);
        log.success(`Created ${file.name} - ${file.description}`);
      } else {
        log.warning(`Source file ${file.name} not found. You may need to create this manually.`);
      }
    } catch (error) {
      log.error(`Failed to create ${file.name}: ${error.message}`);
    }
  });
  
  // Create documentation
  log.step('Creating documentation');
  const docsPath = path.join(ROOT_DIR, 'DEPENDENCY_OPTIMIZATION.md');
  
  try {
    if (fs.existsSync(docsPath)) {
      log.info('Documentation already exists at DEPENDENCY_OPTIMIZATION.md');
    } else {
      const docsSource = path.join(__dirname, '../DEPENDENCY_OPTIMIZATION.md');
      if (fs.existsSync(docsSource)) {
        fs.copyFileSync(docsSource, docsPath);
        log.success('Created documentation at DEPENDENCY_OPTIMIZATION.md');
      } else {
        log.warning('Documentation template not found. You may need to create this manually.');
      }
    }
  } catch (error) {
    log.error(`Failed to create documentation: ${error.message}`);
  }

  // Create example component
  log.step('Creating example optimized component');
  const exampleComponentPath = path.join(ROOT_DIR, 'src/components/probability_distributions/DistributionPlot.optimized.jsx');
  const exampleComponentDestPath = path.join(ROOT_DIR, 'src/components/probability_distributions/DistributionPlot.jsx');
  
  try {
    if (fs.existsSync(exampleComponentPath)) {
      log.info('Example optimized component exists. You can use it as a reference.');
      log.info(`To replace the original component, run: cp ${exampleComponentPath} ${exampleComponentDestPath}`);
    } else {
      log.warning('Example optimized component not found. Check the documentation for examples.');
    }
  } catch (error) {
    log.error(`Failed to check example component: ${error.message}`);
  }
  
  // Final instructions
  log.step('Dependency optimization complete');
  log.info('Next steps:');
  log.info('1. Review the documentation in DEPENDENCY_OPTIMIZATION.md');
  log.info('2. Use the example optimized component as a reference for updating your code');
  log.info('3. Gradually replace heavy imports with the optimized utilities');
  log.info('4. Run bundle analysis to verify the size reduction');
  
  log.success('Optimization complete!');
}

// Run the script
main().catch(error => {
  log.error(`Optimization failed: ${error.message}`);
  process.exit(1);
});