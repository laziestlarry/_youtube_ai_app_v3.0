#!/bin/bash

# YouTube AI App v3.0 - Professional Setup Script
# This script prepares the consolidated environment for first-run.

set -e

echo "🚀 [v3.0] YouTube AI Platform - Intelligent Setup"
echo "=============================================="

# 1. Environment Verification
echo "🔍 Verifying Python environment..."
python_cmd="python3"
if ! command -v $python_cmd &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ and try again."
    exit 1
fi

# 2. Virtual Environment Creation
if [ ! -d "venv" ]; then
    echo "📦 Creating isolated virtual environment..."
    $python_cmd -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# 3. Dependency Installation
echo "📥 Installing backend dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Configuration Preparation
if [ ! -f ".env" ]; then
    echo "📝 Initializing .env from template..."
    if [ -f "config/env.full.example" ]; then
        cp config/env.full.example .env
        echo "⚠️  ACTION REQUIRED: Please update your .env file with valid API keys."
    elif [ -f "config/.env.example" ]; then
        cp config/.env.example .env
        echo "⚠️  ACTION REQUIRED: Please update your .env file with valid API keys."
    else
        echo "❌ Warning: config/.env.example not found."
    fi
else
    echo "✅ .env file already exists."
fi

# 5. Directory Initialization
echo "📁 Preparing system directories..."
mkdir -p logs static/output static/audio static/thumbnails backups uploads

# 6. Database Seeding & Initialization
echo "🗄️  Seeding database with professional admin defaults..."
# Ensure PYTHONPATH is set so that the seed script can find backend modules
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -c "import asyncio; from backend.core.database import init_db; from backend.core.seed_db import seed_db; asyncio.run(init_db()); asyncio.run(seed_db())"

# 7. Final Permissions
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "✨ [v3.0] Setup complete!"
echo "=============================================="
echo "Next Steps:"
echo "1. Configure your .env file with AI and YouTube API keys."
echo "2. Start the executive dashboard: ./scripts/start_app.sh"
echo ""
echo "Default Admin Login: admin@example.com / DEFAULT_ADMIN_PASSWORD (dev default: admin123)"
