#!/bin/bash

# StickForStats Comprehensive Test Suite Runner
# This script runs all tests for the StickForStats application

set -e  # Exit on error

# Set up variables
COVERAGE_DIR="coverage_reports"
LOG_DIR="test_logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_LOG="$LOG_DIR/test_run_$TIMESTAMP.log"
PARALLEL_TESTS=4  # Number of tests to run in parallel

# Create directories if they don't exist
mkdir -p $COVERAGE_DIR
mkdir -p $LOG_DIR

echo "===== StickForStats Test Suite ====="
echo "Starting test run at $(date)"
echo "Logs will be saved to $TEST_LOG"

# Function to run a command and log output
run_and_log() {
  local cmd="$1"
  local description="$2"
  local log_file="$LOG_DIR/${description// /_}_$TIMESTAMP.log"
  
  echo "Running: $description" | tee -a $TEST_LOG
  echo "Command: $cmd" | tee -a $TEST_LOG
  echo "Log file: $log_file" | tee -a $TEST_LOG
  
  start_time=$(date +%s)
  
  # Run the command and capture output
  eval "$cmd" > "$log_file" 2>&1
  local status=$?
  
  end_time=$(date +%s)
  duration=$((end_time - start_time))
  
  if [ $status -eq 0 ]; then
    echo "✅ PASSED: $description (${duration}s)" | tee -a $TEST_LOG
  else
    echo "❌ FAILED: $description (${duration}s)" | tee -a $TEST_LOG
    echo "Check $log_file for details" | tee -a $TEST_LOG
    cat "$log_file" | tail -n 20 | tee -a $TEST_LOG
  fi
  
  return $status
}

# Activate virtual environment if it exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..." | tee -a $TEST_LOG
  source venv/bin/activate
fi

# Check Django project
echo "===== Checking Django project =====" | tee -a $TEST_LOG
run_and_log "python manage.py check" "Django system check"

# Run Python syntax check
echo "===== Checking Python syntax =====" | tee -a $TEST_LOG
run_and_log "python -m compileall ." "Python syntax check"

# Run Django migrations check
echo "===== Checking migrations =====" | tee -a $TEST_LOG
run_and_log "python manage.py makemigrations --check --dry-run" "Migration check"

# Run unit tests for each app
echo "===== Running unit tests =====" | tee -a $TEST_LOG

# Core app tests
run_and_log "python manage.py test stickforstats.core --keepdb" "Core app tests"

# Main app tests
run_and_log "python manage.py test stickforstats.mainapp --keepdb" "Main app tests"

# Run tests for each module
for module in "sqc_analysis" "doe_analysis" "pca_analysis" "probability_distributions" "confidence_intervals" "rag_system"; do
  run_and_log "python manage.py test stickforstats.$module --keepdb" "$module tests"
done

# Run coverage tests
echo "===== Running coverage tests =====" | tee -a $TEST_LOG
run_and_log "coverage run --source='stickforstats' manage.py test stickforstats" "Coverage tests"
run_and_log "coverage report" "Coverage report"
run_and_log "coverage html -d $COVERAGE_DIR/html_$TIMESTAMP" "HTML coverage report"

# Run integration tests
echo "===== Running integration tests =====" | tee -a $TEST_LOG
run_and_log "python test_integration.py --base-url http://localhost:8000" "Integration tests"

# Check for memory leaks using memray if available
if command -v memray &> /dev/null; then
  echo "===== Checking for memory leaks =====" | tee -a $TEST_LOG
  run_and_log "memray run -o $COVERAGE_DIR/memory_profile_$TIMESTAMP.bin python manage.py test stickforstats.core.tests.test_memory_usage" "Memory leak check"
fi

# Test frontend if Node is available
if command -v npm &> /dev/null; then
  echo "===== Running frontend tests =====" | tee -a $TEST_LOG
  
  cd frontend
  
  # Install dependencies if not already installed
  if [ ! -d "node_modules" ]; then
    run_and_log "npm install" "Frontend dependencies installation"
  fi
  
  # Run Jest tests
  run_and_log "npm test -- --coverage" "Frontend Jest tests"
  
  # Run ESLint
  run_and_log "npm run lint" "Frontend ESLint"
  
  cd ..
fi

# Print summary
echo "===== Test Summary =====" | tee -a $TEST_LOG
total_tests=$(grep -c "Running:" $TEST_LOG)
passed_tests=$(grep -c "✅ PASSED:" $TEST_LOG)
failed_tests=$(grep -c "❌ FAILED:" $TEST_LOG)

echo "Total tests: $total_tests" | tee -a $TEST_LOG
echo "Passed: $passed_tests" | tee -a $TEST_LOG
echo "Failed: $failed_tests" | tee -a $TEST_LOG

if [ $failed_tests -eq 0 ]; then
  echo "🎉 All tests passed! 🎉" | tee -a $TEST_LOG
else
  echo "❌ Some tests failed. Check logs for details." | tee -a $TEST_LOG
  # List failed tests
  echo "Failed tests:" | tee -a $TEST_LOG
  grep "❌ FAILED:" $TEST_LOG | tee -a $TEST_LOG
fi

echo "Test run completed at $(date)" | tee -a $TEST_LOG
echo "Coverage reports available in $COVERAGE_DIR/" | tee -a $TEST_LOG
echo "Log files available in $LOG_DIR/" | tee -a $TEST_LOG

# Exit with status code based on test results
exit $failed_tests