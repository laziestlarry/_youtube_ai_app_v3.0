#!/bin/bash

# YouTube AI Platform - Development Script
# Runs both backend and frontend in parallel

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=3001 # Changed to avoid conflict with Nginx on port 3000
LOG_DIR="$PROJECT_ROOT/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] 🎉 $1${NC}"
}

# Function to kill process on port
kill_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        warn "Port $port is in use. Killing existing process..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$url" >/dev/null 2>&1; then
            success "$service_name is ready!"
            return 0
        fi
        
        info "Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    warn "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Cleanup function
cleanup() {
    echo ""
    info "Stopping all services..."
    
    # Stop backend
    if [ -f "$LOG_DIR/backend-dev.pid" ]; then
        kill $(cat "$LOG_DIR/backend-dev.pid") 2>/dev/null || true
        rm "$LOG_DIR/backend-dev.pid"
    fi
    
    # Stop frontend
    if [ -f "$LOG_DIR/frontend-dev.pid" ]; then
        kill $(cat "$LOG_DIR/frontend-dev.pid") 2>/dev/null || true
        rm "$LOG_DIR/frontend-dev.pid"
    fi
    
    success "All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo "${CYAN}"
    echo "🚀 YouTube AI Platform - Development Mode"
    echo "=========================================="
    echo "${NC}"
    
    # Kill any existing processes
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    
    # Start backend
    log "Starting backend service..."
    cd "$PROJECT_ROOT/backend"
    source ../venv/bin/activate
    
    nohup python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$LOG_DIR/backend-dev.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$LOG_DIR/backend-dev.pid"
    cd "$PROJECT_ROOT"
    
    # Wait for backend to be ready
    if wait_for_service "http://localhost:$BACKEND_PORT/health" "Backend API"; then
        success "Backend service started successfully"
    else
        warn "Backend service may not be ready yet"
    fi
    
    # Start frontend
    log "Starting frontend service..."
    cd "$PROJECT_ROOT/frontend"
    
    info "Starting Vite dev server on port $FRONTEND_PORT..."
    nohup npx vite --host --port $FRONTEND_PORT > "$LOG_DIR/frontend-dev.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$LOG_DIR/frontend-dev.pid"
    cd "$PROJECT_ROOT"
    
    # Wait for frontend to be ready
    if wait_for_service "http://localhost:$FRONTEND_PORT" "Frontend"; then
        success "Frontend service started successfully"
    else
        warn "Frontend service may not be ready yet"
    fi
    
    # Display status
    echo ""
    success "🎉 Development servers are starting!"
    echo ""
    echo "${CYAN}📊 Service URLs:${NC}"
    echo "   Backend API:    ${GREEN}http://localhost:$BACKEND_PORT${NC}"
    echo "   API Docs:       ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
    echo "   Health Check:   ${GREEN}http://localhost:$BACKEND_PORT/health${NC}"
    echo "   Frontend:       ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
    echo ""
    echo "${CYAN}📁 Log Files:${NC}"
    echo "   Backend:        $LOG_DIR/backend-dev.log"
    echo "   Frontend:       $LOG_DIR/frontend-dev.log"
    echo ""
    echo "${YELLOW}💡 Development Tips:${NC}"
    echo "   - Backend will auto-reload on file changes"
    echo "   - Frontend will auto-reload on file changes"
    echo "   - Check logs for any errors"
    echo ""
    echo "${PURPLE}🛑 To stop all services: Press Ctrl+C${NC}"
    
    # Keep script running
    info "All services are running. Press Ctrl+C to stop."
    wait
}

# Run main function
main "$@" 