#!/bin/bash

# StickForStats Project Runner
echo "=== StickForStats Project Runner ==="
echo "This script will start both the Django backend and React frontend."

# Check requirements
if ! command -v python >/dev/null 2>&1; then
    echo "Python is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "Node.js/npm is not installed. Please install Node.js and try again."
    exit 1
fi

# Navigate to project directory if needed
if [[ $(basename "$PWD") != "new_project" ]]; then
    PROJECT_DIR="$(dirname "$0")"
    cd "$PROJECT_DIR"
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Install additional dependencies
echo "Installing additional dependencies..."
pip install drf-nested-routers

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Django server in background
echo "Starting Django backend server..."
python manage.py runserver 8000 &
DJANGO_PID=$!

# Navigate to frontend directory
cd frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Installing the missing dependencies
echo "Installing additional frontend dependencies..."
npm install notistack recharts react-markdown web-vitals date-fns papaparse react-dropzone d3 jstat framer-motion

# Start React server
echo "Starting React frontend server..."
npm start &
REACT_PID=$!

# Function to handle script termination
function cleanup {
    echo "Stopping servers..."
    kill $DJANGO_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Register the cleanup function for termination signals
trap cleanup SIGINT SIGTERM

echo "=== StickForStats servers are running ==="
echo "Django backend: http://localhost:8000"
echo "React frontend: http://localhost:3000"
echo "Press Ctrl+C to stop all servers"

# Wait for termination
wait