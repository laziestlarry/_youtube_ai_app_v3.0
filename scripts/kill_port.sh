#!/bin/bash

PORT=${1:-8000}

echo "🔍 Checking for processes on port $PORT..."

# Find processes using the port
PIDS=$(lsof -ti :$PORT)

if [ -z "$PIDS" ]; then
    echo "✅ No processes found on port $PORT"
else
    echo "🔪 Killing processes on port $PORT: $PIDS"
    echo $PIDS | xargs kill -9
    echo "✅ Processes killed"
fi