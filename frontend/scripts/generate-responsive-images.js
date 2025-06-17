#!/usr/bin/env node

/**
 * Generate Responsive Image Variants
 * 
 * This script generates responsive image variants from source images,
 * creating multiple sizes and formats for optimal delivery.
 * 
 * Usage:
 *   node scripts/generate-responsive-images.js [inputDir] [outputDir] [options]
 * 
 * Options:
 *   --widths  Comma-separated list of widths to generate (default: 320,640,1024,1920)
 *   --formats Comma-separated list of formats to generate (default: jpg,webp,avif)
 *   --quality Quality level for output images (default: 80)
 *   --include File pattern to include (default: "**/*.{jpg,jpeg,png}")
 *   --placeholder Generate low-quality placeholders
 *   --clean Remove existing files in output dir first
 * 
 * Examples:
 *   node scripts/generate-responsive-images.js public/images/originals public/images/responsive
 *   node scripts/generate-responsive-images.js --widths=320,768,1280,1920 --formats=webp,avif --quality=85
 * 
 * Requirements:
 *   npm install sharp glob fs-extra
 */

const sharp = require('sharp');
const glob = require('glob');
const path = require('path');
const fs = require('fs-extra');
const { program } = require('commander');

// Configure command-line options
program
  .argument('[inputDir]', 'Input directory', 'public/images')
  .argument('[outputDir]', 'Output directory', 'public/images')
  .option('--widths <list>', 'Comma-separated list of widths to generate', '320,640,1024,1920')
  .option('--formats <list>', 'Comma-separated list of formats to generate', 'jpg,webp,avif')
  .option('--quality <number>', 'Quality level for output images (1-100)', '80')
  .option('--avif-quality <number>', 'Quality level for AVIF images (1-100)', '65')
  .option('--avif-effort <number>', 'Encoding effort for AVIF (0-9, higher is better but slower)', '4')
  .option('--include <pattern>', 'File pattern to include', '**/*.{jpg,jpeg,png}')
  .option('--placeholder', 'Generate low-quality placeholders', false)
  .option('--clean', 'Remove existing files in output directory first', false)
  .parse(process.argv);

const options = program.opts();
const inputDir = program.args[0] || 'public/images';
const outputDir = program.args[1] || 'public/images';

// Parse options
const widths = options.widths.split(',').map(w => parseInt(w.trim(), 10));
const formats = options.formats.split(',').map(f => f.trim().toLowerCase());
const quality = parseInt(options.quality, 10);
const avifQuality = parseInt(options.avifQuality, 10);
const avifEffort = parseInt(options.avifEffort, 10);
const includePattern = options.include;
const generatePlaceholders = options.placeholder;
const cleanOutputDir = options.clean;

// Validate options
if (widths.some(isNaN)) {
  console.error('Error: Invalid width values. Must be comma-separated numbers.');
  process.exit(1);
}

if (quality < 1 || quality > 100 || isNaN(quality)) {
  console.error('Error: Quality must be between 1 and 100');
  process.exit(1);
}

if (avifQuality < 1 || avifQuality > 100 || isNaN(avifQuality)) {
  console.error('Error: AVIF quality must be between 1 and 100');
  process.exit(1);
}

if (avifEffort < 0 || avifEffort > 9 || isNaN(avifEffort)) {
  console.error('Error: AVIF effort must be between 0 and 9');
  process.exit(1);
}

const validFormats = ['jpg', 'jpeg', 'png', 'webp', 'avif'];
if (formats.some(f => !validFormats.includes(f))) {
  console.error(`Error: Invalid formats. Must be one of: ${validFormats.join(', ')}`);
  process.exit(1);
}

// Clean output directory if specified
if (cleanOutputDir) {
  console.log(`Cleaning output directory: ${outputDir}`);
  fs.emptyDirSync(outputDir);
}

// Ensure output directory exists
fs.ensureDirSync(outputDir);

// Find all matching image files
const imageFiles = glob.sync(path.join(inputDir, includePattern), { nocase: true });

if (imageFiles.length === 0) {
  console.warn(`No images found matching pattern: ${includePattern} in ${inputDir}`);
  process.exit(0);
}

console.log(`Found ${imageFiles.length} images to process`);
console.log(`Generating widths: ${widths.join(', ')}px`);
console.log(`Output formats: ${formats.join(', ')}`);
console.log(`Quality level: ${quality}`);
console.log(`AVIF settings: quality=${avifQuality}, effort=${avifEffort}`);
console.log(`Generating placeholders: ${generatePlaceholders ? 'Yes' : 'No'}`);

// Create a queue of operations
const queue = [];

// Process each image
imageFiles.forEach(filePath => {
  const parsedPath = path.parse(filePath);
  const relativeDir = path.relative(inputDir, parsedPath.dir);
  const outputPath = path.join(outputDir, relativeDir);
  const fileName = parsedPath.name;
  
  // Create output directory
  fs.ensureDirSync(outputPath);
  
  // Generate each width and format
  widths.forEach(width => {
    formats.forEach(format => {
      const outputFileName = `${fileName}-${width}w.${format}`;
      const outputFilePath = path.join(outputPath, outputFileName);
      
      queue.push({
        inputPath: filePath,
        outputPath: outputFilePath,
        width,
        format,
        quality
      });
    });
  });
  
  // Generate placeholder if requested
  if (generatePlaceholders) {
    const placeholderPath = path.join(outputPath, `${fileName}-placeholder.jpg`);
    queue.push({
      inputPath: filePath,
      outputPath: placeholderPath,
      width: 40,
      format: 'jpg',
      quality: 20,
      isPlaceholder: true
    });
  }
});

console.log(`Preparing to process ${queue.length} images...`);

// Process the queue with limited concurrency
async function processQueue(concurrency = 5) {
  const total = queue.length;
  let completed = 0;
  let errors = 0;
  let inProgress = 0;
  
  console.log(`Processing with concurrency of ${concurrency}...`);
  
  // Create a pool of promises that gets refilled
  const pool = new Set();
  
  // Process a single item from the queue
  const processItem = async (item) => {
    const { inputPath, outputPath, width, format, quality, isPlaceholder } = item;
    
    try {
      console.log(`Processing: ${path.basename(inputPath)} -> ${path.basename(outputPath)}`);
      
      let image = sharp(inputPath)
        .resize(width);
        
      // Apply format-specific options
      switch (format) {
        case 'jpg':
        case 'jpeg':
          image = image.jpeg({ quality, progressive: true });
          break;
        case 'png':
          image = image.png({ quality });
          break;
        case 'webp':
          image = image.webp({ quality });
          break;
        case 'avif':
          image = image.avif({ 
            quality: avifQuality, 
            effort: avifEffort,
            chromaSubsampling: '4:2:0' // Standard chroma subsampling for better compression
          });
          break;
      }
      
      // Apply blur for placeholders
      if (isPlaceholder) {
        image = image.blur(8);
      }
      
      // Save the image
      await image.toFile(outputPath);
      
      // Get stats and log result
      const stats = await fs.stat(outputPath);
      const sizeKB = (stats.size / 1024).toFixed(1);
      console.log(`✓ Saved ${path.basename(outputPath)} (${sizeKB} KB)`);
      
      completed++;
    } catch (err) {
      console.error(`Error processing ${inputPath}:`, err.message);
      errors++;
    }
    
    inProgress--;
    processNext();
  };
  
  // Process the next batch of items
  const processNext = () => {
    // Fill the pool up to concurrency
    while (queue.length > 0 && inProgress < concurrency) {
      const item = queue.shift();
      inProgress++;
      
      const promise = processItem(item);
      pool.add(promise);
      
      // Remove from pool when done
      promise.then(() => {
        pool.delete(promise);
      });
    }
    
    // If the queue is empty and nothing is in progress, we're done
    if (queue.length === 0 && inProgress === 0) {
      console.log('\nProcessing complete!');
      console.log(`✓ ${completed} images generated successfully`);
      
      if (errors > 0) {
        console.log(`✗ ${errors} errors occurred`);
      }
    }
  };
  
  // Start processing
  processNext();
}

// Run the queue processor
processQueue(5);