#!/bin/bash

# Script to run bundle analyzer with increased memory allocation for Node.js

# Amount of memory to allocate (in MB)
MEMORY_ALLOCATION=8192

echo "🚀 Running bundle analyzer with ${MEMORY_ALLOCATION}MB memory allocation..."

# Set NODE_OPTIONS environment variable to increase memory limit
export NODE_OPTIONS="--max-old-space-size=${MEMORY_ALLOCATION}"

# Run the analyze:interactive script
npm run analyze:interactive

# Check if analyze was successful
if [ $? -ne 0 ]; then
  echo "❌ Bundle analyzer failed. Try increasing memory allocation further or check for other issues."
fi