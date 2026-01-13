#!/bin/bash

set -euo pipefail

echo "🚀 YouTube AI Platform - Deployment (Local/Manual)"
echo "=================================================="

required_vars=(
  "DATABASE_URL"
  "OPENAI_API_KEY"
  "YOUTUBE_API_KEY"
  "GOOGLE_CLOUD_PROJECT"
  "GOOGLE_CLOUD_STORAGE_BUCKET"
  "SECRET_KEY"
)

echo "🔍 Checking environment variables..."
for var in "${required_vars[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "❌ Error: $var is not set"
    printf '%s\n' "${required_vars[@]}"
    exit 1
  fi
done
echo "✅ All required environment variables are set"

echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
echo "✅ Dependencies installed"

echo "🗄️ Initializing database..."
python - <<'PY'
import asyncio
from backend.core.database import init_db
asyncio.run(init_db())
print("✅ Database initialized")
PY

echo "🚀 Starting application..."
export ENVIRONMENT=production
python -m uvicorn services.autonomax_api.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 4
