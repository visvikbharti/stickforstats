#!/bin/bash

# Navigate to the frontend directory
cd "$(dirname "$0")"

# Check if node_modules exists, if not, install dependencies
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Set environment variables for testing
export NODE_ENV=test

# Run the tests
case "$1" in
  "watch")
    echo "Running tests in watch mode..."
    npm run test:watch
    ;;
  "coverage")
    echo "Running tests with coverage..."
    npm run test:coverage
    ;;
  "probability")
    echo "Running tests for Probability Distributions module..."
    npm test -- --testPathPattern=probability_distributions
    ;;
  "confidence")
    echo "Running tests for Confidence Intervals module..."
    npm test -- --testPathPattern=confidence_intervals
    ;;
  "simulations")
    echo "Running tests for simulation components..."
    npm test -- --testPathPattern=confidence_intervals/.*Simulation
    ;;
  "calculators")
    echo "Running tests for calculator components..."
    npm test -- --testPathPattern=confidence_intervals/.*Calculator
    ;;
  "education")
    echo "Running tests for educational components..."
    npm test -- --testPathPattern=confidence_intervals/Theory
    ;;
  *)
    echo "Running all tests..."
    npm test
    ;;
esac