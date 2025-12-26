#!/bin/bash

echo "🐳 Starting YouTube AI Creator in Docker"
echo "======================================="

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker stop $(docker ps -q --filter "ancestor=youtube-ai-creator-simple") 2>/dev/null || true

# Remove stopped containers
echo "🧹 Cleaning up..."
docker container prune -f

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is in use, using port 8001 instead"
    PORT=8001
else
    PORT=8000
fi

echo "🚀 Starting container on port $PORT..."
docker run -p $PORT:8000 --name youtube-ai-creator youtube-ai-creator-simple

echo "🌐 Application available at: http://localhost:$PORT"