#!/bin/bash

# Script to start the development server with increased memory allocation for Node.js

# Amount of memory to allocate (in MB)
MEMORY_ALLOCATION=8192

echo "🚀 Starting development server with ${MEMORY_ALLOCATION}MB memory allocation..."

# Set NODE_OPTIONS environment variable to increase memory limit
export NODE_OPTIONS="--max-old-space-size=${MEMORY_ALLOCATION}"

# Run the standard start script
npm run start

# Check if start was successful
if [ $? -ne 0 ]; then
  echo "❌ Development server failed to start. Try increasing memory allocation further or check for other issues."
fi