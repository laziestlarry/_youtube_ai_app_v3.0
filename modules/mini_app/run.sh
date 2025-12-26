#!/bin/bash

# YouTube Income Commander - Quick Launch Script
# Makes it easy to run the system on any platform

echo "🚀 YouTube Income Commander - Quick Launch"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python not found. Please install Python 3.8+"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Using Python: $PYTHON_CMD"

# Check if we're in the right directory
if [ ! -f "cli_launcher.py" ]; then
    echo "❌ cli_launcher.py not found. Please run from the project directory."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt --quiet
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Run the CLI launcher
echo "🎬 Starting YouTube Income Commander..."
echo ""
$PYTHON_CMD cli_launcher.py

# Deactivate virtual environment
deactivate

echo ""
echo "👋 Thanks for using YouTube Income Commander!"
