/**
 * Convert Images to AVIF Format
 * 
 * This script converts JPG, PNG, and WebP images to AVIF format with specified quality
 * and saves them alongside the original files. It uses Sharp for image processing.
 * 
 * AVIF provides significantly better compression than WebP and JPG while maintaining
 * similar or better visual quality. However, browser support is more limited than WebP,
 * so this should be used as a progressive enhancement with appropriate fallbacks.
 * 
 * Usage:
 *   node scripts/convert-to-avif.js [quality] [effort] [directory]
 *   
 * Options:
 *   quality   - AVIF quality level (1-100, default: 65)
 *   effort    - AVIF encoding effort (0-9, default: 4, higher = better compression but slower)
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
const quality = parseInt(args[0]) || 65;     // AVIF uses lower quality values by default
const effort = parseInt(args[1]) || 4;       // Default to medium effort (range 0-9)
const directory = args[2] || './public/images';

// Validate parameters
if (quality < 1 || quality > 100) {
  console.error('Quality must be between 1 and 100');
  process.exit(1);
}

if (effort < 0 || effort > 9) {
  console.error('Effort must be between 0 and 9');
  process.exit(1);
}

console.log(`Converting images in ${directory} to AVIF with quality ${quality} and effort ${effort}...`);

// Find all JPG, PNG, and WebP images in the directory (recursively)
const imageFiles = glob.sync(`${directory}/**/*.@(jpg|jpeg|png|webp)`, { nocase: true });

if (imageFiles.length === 0) {
  console.warn(`No JPG, PNG, or WebP images found in ${directory}`);
  process.exit(0);
}

console.log(`Found ${imageFiles.length} images to convert.`);

// Convert images to AVIF
let completed = 0;
let skipped = 0;
let errors = 0;

// Helper function to format file size
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

(async () => {
  // Process images in batches to avoid memory issues
  const batchSize = 5;
  const batches = Math.ceil(imageFiles.length / batchSize);
  
  for (let i = 0; i < batches; i++) {
    const batchFiles = imageFiles.slice(i * batchSize, (i + 1) * batchSize);
    const promises = batchFiles.map(async (file) => {
      try {
        const outputPath = `${file.substring(0, file.lastIndexOf('.'))}.avif`;
        
        // Skip if AVIF version already exists and is newer than the source
        if (fs.existsSync(outputPath)) {
          const srcStat = fs.statSync(file);
          const avifStat = fs.statSync(outputPath);
          
          if (avifStat.mtime > srcStat.mtime) {
            console.log(`Skipping ${file} (AVIF version is up to date)`);
            skipped++;
            return;
          }
        }
        
        // Process image
        console.log(`Converting ${file} to AVIF...`);
        
        await sharp(file)
          .avif({ 
            quality, 
            effort,
            chromaSubsampling: '4:2:0', // Standard chroma subsampling for better compression
          })
          .toFile(outputPath);
        
        completed++;
        
        // Calculate and log file size reduction
        const originalSize = fs.statSync(file).size;
        const avifSize = fs.statSync(outputPath).size;
        const reduction = ((originalSize - avifSize) / originalSize * 100).toFixed(2);
        
        console.log(`✓ Saved ${outputPath} (${reduction}% smaller, ${formatFileSize(originalSize)} → ${formatFileSize(avifSize)})`);
      } catch (error) {
        console.error(`Error converting ${file}:`, error.message);
        errors++;
      }
    });
    
    // Wait for current batch to complete
    await Promise.all(promises);
    
    // Simple progress indicator
    console.log(`Processed batch ${i + 1}/${batches} (${Math.min((i + 1) * batchSize, imageFiles.length)}/${imageFiles.length} images)`);
  }
  
  // Summary
  console.log('\nConversion complete!');
  console.log(`${completed} images converted successfully`);
  console.log(`${skipped} images skipped (already converted)`);
  
  if (errors > 0) {
    console.log(`${errors} images failed to convert`);
  }
})();