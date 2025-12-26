#!/bin/bash

# YouTube AI App v3.0 - Professional Launch Script
# This script starts the unified backend and executive dashboard.

set -e

echo "🚀 [v3.0] Launching YouTube AI Platform..."

# 1. Environment Verification
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please run scripts/setup.sh first."
    exit 1
fi

# 2. Virtual Environment Activation
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment (venv) not found. Please run scripts/setup.sh first."
    exit 1
fi

# 3. Start Backend Services
echo "🛰️  Starting backend API on port 8000..."
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &

# 4. Dashboard Availability
echo ""
echo "✨ YouTube AI Executive Dashboard is initializing..."
echo "🌐 Access URI: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services."

# Wait for background processes
wait