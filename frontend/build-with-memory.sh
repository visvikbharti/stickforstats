#!/bin/bash

# Script to build the frontend with increased memory allocation for Node.js

# Amount of memory to allocate (in MB)
MEMORY_ALLOCATION=8192

echo "🚀 Building frontend with ${MEMORY_ALLOCATION}MB memory allocation..."

# Set NODE_OPTIONS environment variable to increase memory limit
export NODE_OPTIONS="--max-old-space-size=${MEMORY_ALLOCATION}"

# Run the standard build script
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
  echo "✅ Build completed successfully with increased memory allocation."
else
  echo "❌ Build failed. Try increasing memory allocation further or check for other issues."
fi