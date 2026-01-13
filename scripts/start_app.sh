#!/bin/bash

# Platform Launch Script
# Starts the shared backend. UIs run separately.

set -e

APP_TARGET="${APP_TARGET:-autonomax}"
APP_MODULE="services.autonomax_api.main:app"
if [ "$APP_TARGET" = "youtube" ]; then
    APP_MODULE="services.youtube_ai_api.main:app"
fi

echo "🚀 Launching shared backend ($APP_TARGET)..."

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
python3 -m uvicorn "$APP_MODULE" --host 0.0.0.0 --port 8000 --reload &

# 4. Dashboard Availability
echo ""
echo "✨ Backend is initializing..."
echo "🌐 API Base: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "UI options:"
echo "  - YouTube AI (Vite):  APP_TARGET=youtube bash scripts/dev.sh"
echo "  - Autonomax (Next):   APP_TARGET=autonomax bash scripts/dev.sh"
echo ""
echo "Press Ctrl+C to stop all services."

# Wait for background processes
wait
