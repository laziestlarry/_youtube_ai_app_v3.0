#!/bin/bash

# Production Deployment Script
# Quick deployment for immediate use

set -e

echo "🚀 YouTube AI Content Creator - Production Deployment"
echo "=================================================="

# Check if required environment variables are set
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
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set"
        echo "Please set all required environment variables:"
        printf '%s\n' "${required_vars[@]}"
        exit 1
    fi
done
echo "✅ All required environment variables are set"

# Install dependencies
echo "📦 Installing
#!/bin/bash

# Production Deployment Script
# Quick deployment for immediate use

set -e

echo "🚀 YouTube AI Content Creator - Production Deployment"
echo "=================================================="

# Check if required environment variables are set
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
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set"
        echo "Please set all required environment variables:"
        printf '%s\n' "${required_vars[@]}"
        exit 1
    fi
done
echo "✅ All required environment variables are set"

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Initialize database
echo "🗄️ Initializing database..."
python -c "
import asyncio
from core.database import init_db
asyncio.run(init_db())
print('✅ Database initialized')
"

# Start the application
echo "🚀 Starting application..."
export ENVIRONMENT=production
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4

echo "✅ Application deployed successfully!"
echo "🌐 Access your application at: http://localhost:${PORT:-8000}"
echo "📚 API Documentation: http://localhost:${PORT:-8000}/docs"
