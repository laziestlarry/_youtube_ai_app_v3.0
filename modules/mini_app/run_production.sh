#!/bin/bash
echo "🎬 YouTube Production Pipeline - Starting..."

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    bash install_dependencies.sh
fi

# Create output directories
mkdir -p outputs/{scripts,audio,thumbnails,videos}

echo "💰 Starting complete video production system..."
echo "🌐 Will open at: http://localhost:8080"

python complete_pipeline.py
