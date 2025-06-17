#!/bin/bash
# Complete local test script for StickForStats
# This script sets up and runs all components of the application locally

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="/Users/vishalbharti/Downloads/StickForStats_Migration/new_project"
VENV_DIR="$PROJECT_ROOT/venv"
DJANGO_PORT=8000
REACT_PORT=3000
LOG_FILE="$PROJECT_ROOT/local_test.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if Python is installed
check_python() {
    log "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        log "ERROR: Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
    log "Found Python $PYTHON_VERSION"
    
    # Validate Python version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        log "ERROR: Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
        exit 1
    fi
}

# Check if Node.js is installed
check_nodejs() {
    log "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        log "ERROR: Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    log "Found Node.js $NODE_VERSION"
    
    # Validate Node.js version
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1 | tr -d 'v')
    
    if [ "$NODE_MAJOR" -lt 16 ]; then
        log "ERROR: Node.js 16 or higher is required. Found Node.js $NODE_VERSION"
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    log "Setting up Python virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        log "Creating new virtual environment at $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    else
        log "Using existing virtual environment at $VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install requirements
    log "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt"
    
    log "Python virtual environment setup complete"
}

# Create test database
setup_database() {
    log "Setting up test database..."
    
    # Check if database exists
    if [ -f "$PROJECT_ROOT/db.sqlite3" ]; then
        read -p "Existing database found. Do you want to recreate it? (y/N): " recreate
        if [[ "$recreate" =~ ^[Yy]$ ]]; then
            log "Backing up existing database..."
            cp "$PROJECT_ROOT/db.sqlite3" "$PROJECT_ROOT/db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)"
            rm "$PROJECT_ROOT/db.sqlite3"
            log "Existing database removed"
        else
            log "Using existing database"
        fi
    fi
    
    # Run migrations
    log "Running database migrations..."
    cd "$PROJECT_ROOT"
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    log "Checking superuser..."
    if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0 if User.objects.filter(is_superuser=True).exists() else 1)"; then
        log "Creating superuser..."
        python create_superuser.py
    else
        log "Superuser already exists"
    fi
    
    # Register modules
    log "Registering modules..."
    python register_modules.py
    
    # Create sample data if needed
    read -p "Do you want to create sample data for testing? (Y/n): " sample_data
    if [[ ! "$sample_data" =~ ^[Nn]$ ]]; then
        log "Creating sample data..."
        python manage.py loaddata sample_dataset.json
    fi
    
    log "Database setup complete"
}

# Setup React frontend
setup_frontend() {
    log "Setting up React frontend..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Install dependencies
    log "Installing Node.js dependencies..."
    npm install
    
    log "Frontend setup complete"
}

# Start Django backend server
start_backend() {
    log "Starting Django backend server on port $DJANGO_PORT..."
    
    cd "$PROJECT_ROOT"
    source "$VENV_DIR/bin/activate"
    
    # Run the Django server in background
    python manage.py runserver "$DJANGO_PORT" > "$PROJECT_ROOT/server.log" 2>&1 &
    DJANGO_PID=$!
    
    log "Django server started with PID $DJANGO_PID"
    
    # Wait for server to start
    log "Waiting for Django server to start..."
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://localhost:$DJANGO_PORT/api/v1/core/health-check/" > /dev/null; then
            log "Django server is running"
            break
        fi
        
        attempt=$((attempt+1))
        log "Waiting for Django server (attempt $attempt/$max_attempts)..."
        sleep 1
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log "ERROR: Django server failed to start in time"
        log "Check server.log for details"
        kill_processes
        exit 1
    fi
}

# Start React frontend server
start_frontend() {
    log "Starting React frontend server on port $REACT_PORT..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run the React dev server in background
    npm start > "$PROJECT_ROOT/frontend.log" 2>&1 &
    REACT_PID=$!
    
    log "React server started with PID $REACT_PID"
    
    # Wait for server to start
    log "Waiting for React server to start..."
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://localhost:$REACT_PORT/" > /dev/null; then
            log "React server is running"
            break
        fi
        
        attempt=$((attempt+1))
        log "Waiting for React server (attempt $attempt/$max_attempts)..."
        sleep 1
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log "ERROR: React server failed to start in time"
        log "Check frontend.log for details"
        kill_processes
        exit 1
    fi
}

# Run integration tests
run_tests() {
    log "Running basic integration tests..."
    
    cd "$PROJECT_ROOT"
    source "$VENV_DIR/bin/activate"
    
    # Run Django system checks
    log "Running Django system checks..."
    python manage.py check --deploy
    
    # Test API endpoints
    log "Testing API endpoints..."
    curl -s "http://localhost:$DJANGO_PORT/api/v1/core/health-check/" | grep -q "ok" || { log "ERROR: API health check failed"; kill_processes; exit 1; }
    
    log "Basic integration tests passed"
}

# Open application in browser
open_application() {
    log "Opening application in default browser..."
    
    # Try to open browser based on platform
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:$REACT_PORT/"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:$REACT_PORT/" &> /dev/null
    else
        log "Please open http://localhost:$REACT_PORT/ in your browser"
    fi
}

# Kill running processes
kill_processes() {
    log "Cleaning up processes..."
    
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null || true
        log "Django server stopped"
    fi
    
    if [ ! -z "$REACT_PID" ]; then
        kill $REACT_PID 2>/dev/null || true
        log "React server stopped"
    fi
}

# Wait for user to exit
wait_for_exit() {
    log "StickForStats is now running!"
    log "Backend: http://localhost:$DJANGO_PORT/"
    log "Frontend: http://localhost:$REACT_PORT/"
    log "Admin: http://localhost:$DJANGO_PORT/admin/"
    log "API Documentation: http://localhost:$DJANGO_PORT/api/docs/"
    log ""
    log "Press Ctrl+C to stop the servers"
    
    # Trap Ctrl+C
    trap kill_processes INT
    
    # Wait for user to stop the script
    tail -f "$PROJECT_ROOT/server.log" "$PROJECT_ROOT/frontend.log"
}

# Display summary
display_summary() {
    log "=== StickForStats Application Summary ==="
    log "Backend URL: http://localhost:$DJANGO_PORT/"
    log "Frontend URL: http://localhost:$REACT_PORT/"
    log "Admin URL: http://localhost:$DJANGO_PORT/admin/"
    log "API Documentation: http://localhost:$DJANGO_PORT/api/docs/"
    log ""
    log "Log files:"
    log "- Server log: $PROJECT_ROOT/server.log"
    log "- Frontend log: $PROJECT_ROOT/frontend.log"
    log "- Script log: $LOG_FILE"
    log ""
    log "=== Credentials ==="
    log "Admin username: admin@example.com"
    log "Admin password: (created during setup)"
    log ""
    log "=== Next Steps ==="
    log "1. Test all modules and features"
    log "2. Verify data persistence and cross-module integration"
    log "3. Test performance with larger datasets"
    log "4. When finished, stop the servers with Ctrl+C"
    log ""
}

# Main function
main() {
    log "=== StickForStats Local Test Script ==="
    log "Starting test of the complete application..."
    
    # Check requirements
    check_python
    check_nodejs
    
    # Setup components
    setup_venv
    setup_database
    setup_frontend
    
    # Start servers
    start_backend
    start_frontend
    
    # Run basic tests
    run_tests
    
    # Open application
    open_application
    
    # Display summary
    display_summary
    
    # Wait for user to exit
    wait_for_exit
}

# Run the main function
main