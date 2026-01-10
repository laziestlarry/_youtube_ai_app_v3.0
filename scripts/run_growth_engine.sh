#!/bin/bash
# Autonomous Growth Masterplan - Startup Script
# Runs the separate module on Port 8001

echo "Starting Autonomous Growth Engine (clean slate)..."
echo "Port: 8001"
echo "Database: modules/growth_engine_v1/growth_engine.db"

# Ensure we are in root
cd "$(dirname "$0")/.."

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run
uvicorn modules.growth_engine_v1.app:app --host 0.0.0.0 --port 8001 --reload
