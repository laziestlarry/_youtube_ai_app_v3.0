#!/bin/bash
echo "🚀 YouTube Income Commander Mini - Quick Start"
echo "=============================================="

# Install requirements if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing FastAPI..."
    pip install fastapi uvicorn
fi

echo "💰 Starting cash generation app..."
python simple_start.py
