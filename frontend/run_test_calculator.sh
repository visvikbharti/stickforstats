#!/bin/bash

# Navigate to the frontend directory
cd "$(dirname "$0")"

# Start the React app with custom environment variables
PORT=3001 npm start &

# Save the process ID to shut it down later
REACT_PID=$!

# Wait for 5 seconds to let the server start
echo "Starting the development server..."
sleep 5

# Open the browser to the test calculator page
echo "Opening the test page in browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3001/test/calculator
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:3001/test/calculator
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows with Git Bash or similar
    start http://localhost:3001/test/calculator
else
    echo "Please open http://localhost:3001/test/calculator in your browser"
fi

echo "Press Ctrl+C to stop the server"

# Wait for user to press Ctrl+C
trap "kill $REACT_PID; exit" INT
wait $REACT_PID