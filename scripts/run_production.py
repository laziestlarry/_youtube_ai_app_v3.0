#!/usr/bin/env python3
"""
Production server runner for YouTube AI Content Creator.
"""

import uvicorn
import sys
import socket
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def find_free_port(start_port=8000, max_port=8100):
    """Find a free port starting from start_port."""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Run the production server."""
    try:
        from backend.core.config import settings
        app_target = os.getenv("APP_TARGET", "autonomax")
        app_module = "services.autonomax_api.main:app"
        if app_target == "youtube":
            app_module = "services.youtube_ai_api.main:app"
        
        # Find available port
        available_port = find_free_port(settings.port)
        if available_port is None:
            print("❌ No available ports found in range 8000-8100")
            sys.exit(1)
        
        if available_port != settings.port:
            print(f"⚠️  Port {settings.port} is in use, using port {available_port}")
        
        print("🚀 Starting YouTube AI Content Creator")
        print("=" * 40)
        print(f"🌐 Host: {settings.host}")
        print(f"🔌 Port: {available_port}")
        print(f"🏭 Environment: {settings.environment}")
        print(f"🗄️  Database: {settings.database_url}")
        print("=" * 40)
        print(f"🌐 Application URL: http://localhost:{available_port}")
        print(f"📚 API Documentation: http://localhost:{available_port}/docs")
        print(f"🏥 Health Check: http://localhost:{available_port}/health")
        print("=" * 40)
        print("Press Ctrl+C to stop the server")
        print("")
        
        uvicorn.run(
            app_module,
            host=settings.host,
            port=available_port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
