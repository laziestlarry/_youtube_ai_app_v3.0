#!/bin/bash
set -e

# Colors for output
green='\033[0;32m'
red='\033[0;31m'
nc='\033[0m' # No Color

# 1. Initialize the database
echo -e "${green}Initializing database...${nc}"
python3 backend/scripts/init_db_launcher.py

echo -e "${green}Database initialized successfully.${nc}"

# 2. Run health check endpoint (requires server running in background)
HEALTH_URL="http://localhost:8000/api/v1/health"
echo -e "${green}Checking backend health endpoint...${nc}"

# Start backend in background for health check
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1 &
SERVER_PID=$!
sleep 5

HEALTH_STATUS=$(curl -s $HEALTH_URL | grep '"status":"healthy"')
if [ -z "$HEALTH_STATUS" ]; then
  echo -e "${red}Health check failed!${nc}"
  kill $SERVER_PID
  exit 1
else
  echo -e "${green}Health check passed.${nc}"
fi

# 3. Check log file creation
echo -e "${green}Checking log file creation...${nc}"
if [ -f backend/system.log ] && [ -s backend/system.log ]; then
  echo -e "${green}System log exists and is not empty.${nc}"
else
  echo -e "${red}System log missing or empty!${nc}"
  kill $SERVER_PID
  exit 1
fi

if [ -f logs/execution.log ] && [ -s logs/execution.log ]; then
  echo -e "${green}Execution log exists and is not empty.${nc}"
else
  echo -e "${red}Execution log missing or empty!${nc}"
  kill $SERVER_PID
  exit 1
fi

# 4. Stop the test server
kill $SERVER_PID
sleep 2

# 5. Launch backend server for production
# (Uncomment the following line to launch for production)
# uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2

echo -e "${green}Pre-launch validation complete. Ready for production launch.${nc}" 