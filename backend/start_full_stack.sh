#!/bin/bash

echo "🚀 Starting Full Stack YouTube AI Content Creator"
echo "================================================"

# Build frontend if it doesn't exist
if [ ! -d "frontend/build" ]; then
    echo "🏗️  Frontend build not found. Building..."
    chmod +x build_frontend.sh
    ./build_frontend.sh
fi

# Start the backend (which will serve both API and frontend)
echo "🌐 Starting full stack application..."
./start.sh