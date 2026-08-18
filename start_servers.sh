#!/bin/bash

# Determine project root directory path
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python3"

echo "Starting AgentFlowGuard Servers..."

# Function to kill existing processes listening on ports 8000 and 8080
kill_port() {
    local port=$1
    local pid=$(lsof -t -i :$port)
    if [ ! -z "$pid" ]; then
        echo "Killing existing process on port $port (PID: $pid)..."
        kill -9 $pid
    fi
}

kill_port 8000
kill_port 8080

# Start main web app server
echo "Launching Web App Server on port 8000..."
cd "$PROJECT_DIR/web_app"
$PYTHON_BIN -u app.py > "$PROJECT_DIR/web_app.log" 2>&1 &
WEB_PID=$!

# Start LocalListener server
echo "Launching LocalListener Server on port 8080..."
cd "$PROJECT_DIR/LocalListener"
$PYTHON_BIN -u app.py > "$PROJECT_DIR/listener.log" 2>&1 &
LISTENER_PID=$!

echo "Servers launched successfully!"
echo "Web App PID: $WEB_PID (logs: web_app.log)"
echo "Listener PID: $LISTENER_PID (logs: listener.log)"

# Wait for background jobs to keep the script active
wait
