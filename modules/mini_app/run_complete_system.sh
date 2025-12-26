#!/bin/bash

echo "🎬 COMPLETE YOUTUBE PRODUCTION SYSTEM"
echo "======================================"

# Create all directories
mkdir -p outputs/{scripts,audio,thumbnails,videos,upload_packages}
mkdir -p exports

echo "📁 Directories created"

# Check dependencies
echo "🔍 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check ffmpeg (optional)
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg found - video creation enabled"
else
    echo "⚠️  ffmpeg not found - will create guides instead"
fi

# Check TTS capabilities
if command -v say &> /dev/null; then
    echo "✅ macOS TTS available"
elif command -v espeak &> /dev/null; then
    echo "✅ Linux TTS available"
else
    echo "⚠️  No TTS found - will create recording guides"
fi

echo ""
echo "🚀 AVAILABLE COMMANDS:"
echo "======================"
echo "1. Single Video Pipeline:"
echo "   python complete_sequential_pipeline.py"
echo ""
echo "2. Batch Video Creation:"
echo "   python batch_pipeline.py"
echo ""
echo "3. Project Management:"
echo "   python project_manager.py"
echo ""
echo "4. Quick Start (5 videos):"
echo "   python batch_pipeline.py"
echo ""

# Ask what to run
read -p "What would you like to run? (1-4): " choice

case $choice in
    1)
        echo "🎬 Starting single video pipeline..."
        python3 complete_sequential_pipeline.py
        ;;
    2)
        echo "🎬 Starting batch pipeline..."
        python3 batch_pipeline.py
        ;;
    3)
        echo "📋 Starting project manager..."
        python3 project_manager.py
        ;;
    4)
        echo "🚀 Quick start - creating 5 videos..."
        python3 batch_pipeline.py
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

echo ""
echo "✅ Complete! Check the outputs/ directory for your files."
echo "💰 Ready to upload and monetize your YouTube videos!"
