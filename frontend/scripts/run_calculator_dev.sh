#!/bin/bash

# Enhanced test calculator runner script
# This script provides a more robust way to test the probability calculator
# with environment configuration, logging, and cleanup

# Color definitions for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set the working directory to the project root, regardless of where the script is run from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Output header
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Probability Calculator Development Tool ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo

# Check if node modules are installed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Node modules not found. Running npm install...${NC}"
    npm install
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error installing dependencies. Please check your npm setup.${NC}"
        exit 1
    fi
fi

# Check for stale or crashed processes
cleanup_existing() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Found process using port $port. Cleaning up...${NC}"
        kill -9 $pid
        sleep 1
    fi
}

# Set port, defaulting to 3001 if not specified
PORT=${1:-3001}
cleanup_existing $PORT

# Create log file for this session
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/calculator_test_$TIMESTAMP.log"

# Start the React app with custom environment variables
echo -e "${GREEN}Starting development server on port $PORT...${NC}"
echo -e "Logs will be written to: ${YELLOW}$LOG_FILE${NC}"

# Set up configuration
export REACT_APP_API_URL=http://localhost:8000
export REACT_APP_ENV=development
export REACT_APP_ENABLE_MOCKS=true
export PORT=$PORT

# Start React in the background
npm start > "$LOG_FILE" 2>&1 &
REACT_PID=$!

# Function to check if the server is ready
check_server() {
    for i in {1..30}; do
        if curl -s http://localhost:$PORT > /dev/null; then
            return 0
        fi
        sleep 1
    done
    return 1
}

echo -e "${YELLOW}Waiting for server to start (may take a moment)...${NC}"
if check_server; then
    echo -e "${GREEN}Server started successfully!${NC}"
else
    echo -e "${RED}Server did not start within expected time. Please check the logs at $LOG_FILE${NC}"
    kill -9 $REACT_PID 2>/dev/null
    exit 1
fi

# Open the browser to the test calculator page
echo -e "${GREEN}Opening the calculator in your browser...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:$PORT/test/calculator"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:$PORT/test/calculator"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows with Git Bash or similar
    start "http://localhost:$PORT/test/calculator"
else
    echo -e "${YELLOW}Please open http://localhost:$PORT/test/calculator in your browser${NC}"
fi

# Function to show menu
show_menu() {
    echo
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}  Calculator Development Options:${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo -e "  ${GREEN}r${NC} - Restart server"
    echo -e "  ${GREEN}o${NC} - Open calculator in browser again"
    echo -e "  ${GREEN}l${NC} - View logs"
    echo -e "  ${GREEN}c${NC} - Clear logs"
    echo -e "  ${GREEN}q${NC} - Quit"
    echo -e "${BLUE}=========================================${NC}"
    echo -n "Enter option: "
}

# Interactive command loop
while true; do
    show_menu
    read -n 1 option
    echo
    
    case $option in
        r)
            echo -e "${YELLOW}Restarting server...${NC}"
            kill -9 $REACT_PID 2>/dev/null
            cleanup_existing $PORT
            npm start > "$LOG_FILE" 2>&1 &
            REACT_PID=$!
            
            if check_server; then
                echo -e "${GREEN}Server restarted successfully!${NC}"
            else
                echo -e "${RED}Failed to restart server!${NC}"
            fi
            ;;
        o)
            echo -e "${GREEN}Opening calculator in browser...${NC}"
            if [[ "$OSTYPE" == "darwin"* ]]; then
                open "http://localhost:$PORT/test/calculator"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                xdg-open "http://localhost:$PORT/test/calculator"
            elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
                start "http://localhost:$PORT/test/calculator"
            else
                echo -e "${YELLOW}Please open http://localhost:$PORT/test/calculator in your browser${NC}"
            fi
            ;;
        l)
            echo -e "${YELLOW}Displaying logs (press Q to exit):${NC}"
            less "$LOG_FILE"
            ;;
        c)
            echo -e "${YELLOW}Clearing logs...${NC}"
            > "$LOG_FILE"
            echo -e "${GREEN}Logs cleared!${NC}"
            ;;
        q)
            echo -e "${GREEN}Shutting down server...${NC}"
            kill -9 $REACT_PID 2>/dev/null
            cleanup_existing $PORT
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option!${NC}"
            ;;
    esac
done