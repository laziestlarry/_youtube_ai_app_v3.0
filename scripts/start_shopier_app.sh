#!/bin/bash

set -e

echo "🚀 [shopier] Launching Shopier app mode..."

ENV_FILE="${ENV_FILE:-.env.shopier}"
if [ -f "$ENV_FILE" ]; then
    echo "✅ Using env file: $ENV_FILE"
elif [ -f ".env" ]; then
    ENV_FILE=".env"
    echo "✅ Using env file: $ENV_FILE"
else
    echo "❌ Error: .env.shopier or .env not found. Copy config/shopier.env.example to .env.shopier."
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

export SHOPIER_APP_MODE=true
APP_TARGET="${APP_TARGET:-autonomax}"
APP_MODULE="services.autonomax_api.main:app"
if [ "$APP_TARGET" = "youtube" ]; then
    APP_MODULE="services.youtube_ai_api.main:app"
fi

if [ ! -f "static/store.html" ]; then
    echo "🛒 static/store.html missing. Generating storefront..."
    python3 scripts/deploy_storefront.py
fi

if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment (venv) not found. Please run scripts/setup.sh first."
    exit 1
fi

export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "🛰️  Starting Shopier backend on port 8000..."
python3 -m uvicorn "$APP_MODULE" --host 0.0.0.0 --port 8000 --reload
