/**
 * Convert Images to WebP Format
 * 
 * This script converts JPG and PNG images to WebP format with specified quality
 * and saves them alongside the original files. It uses Sharp for image processing.
 * 
 * Usage:
 *   node scripts/convert-to-webp.js [quality] [directory]
 *   
 * Options:
 *   quality   - WebP quality level (1-100, default: 80)
 *   directory - Directory containing images to convert (default: ./public/images)
 * 
 * Requirements:
 *   npm install sharp glob
 */

const sharp = require('sharp');
const glob = require('glob');
const path = require('path');
const fs = require('fs');

// Parse command line arguments
const args = process.argv.slice(2);
const quality = parseInt(args[0]) || 80;
const directory = args[1] || './public/images';

// Validate quality parameter
if (quality < 1 || quality > 100) {
  console.error('Quality must be between 1 and 100');
  process.exit(1);
}

console.log(`Converting images in ${directory} to WebP with quality ${quality}...`);

// Find all JPG and PNG images in the directory (recursively)
const imageFiles = glob.sync(`${directory}/**/*.@(jpg|jpeg|png)`, { nocase: true });

if (imageFiles.length === 0) {
  console.warn(`No JPG or PNG images found in ${directory}`);
  process.exit(0);
}

console.log(`Found ${imageFiles.length} images to convert.`);

// Convert images to WebP
let completed = 0;
let skipped = 0;
let errors = 0;

(async () => {
  for (const file of imageFiles) {
    try {
      const outputPath = `${file.substring(0, file.lastIndexOf('.'))}.webp`;
      
      // Skip if WebP version already exists and is newer than the source
      if (fs.existsSync(outputPath)) {
        const srcStat = fs.statSync(file);
        const webpStat = fs.statSync(outputPath);
        
        if (webpStat.mtime > srcStat.mtime) {
          console.log(`Skipping ${file} (WebP version is up to date)`);
          skipped++;
          continue;
        }
      }
      
      // Process image
      console.log(`Converting ${file} to WebP...`);
      
      await sharp(file)
        .webp({ quality })
        .toFile(outputPath);
      
      completed++;
      
      // Calculate and log file size reduction
      const originalSize = fs.statSync(file).size;
      const webpSize = fs.statSync(outputPath).size;
      const reduction = ((originalSize - webpSize) / originalSize * 100).toFixed(2);
      
      console.log(`✓ Saved ${outputPath} (${reduction}% smaller)`);
    } catch (error) {
      console.error(`Error converting ${file}:`, error.message);
      errors++;
    }
  }
  
  // Summary
  console.log('\nConversion complete!');
  console.log(`${completed} images converted successfully`);
  console.log(`${skipped} images skipped (already converted)`);
  
  if (errors > 0) {
    console.log(`${errors} images failed to convert`);
  }
})();