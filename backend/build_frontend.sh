#!/bin/bash

echo "🏗️  Building YouTube AI Content Creator Frontend"
echo "=============================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the React app
echo "🏗️  Building React app..."
npm run build

# Check if build was successful
if [ -d "build" ]; then
    echo "✅ Frontend build completed successfully!"
    echo "📁 Build files are in frontend/build/"
    
    # Copy build files to static directory for fallback
    echo "📋 Copying build files to static directory..."
    mkdir -p ../static
    cp build/index.html ../static/index.html 2>/dev/null || true
    
    echo "🎉 Frontend is ready!"
else
    echo "❌ Frontend build failed!"
    exit 1
fi