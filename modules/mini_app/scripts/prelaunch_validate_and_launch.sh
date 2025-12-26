#!/bin/bash
set -e

green='\033[0;32m'
red='\033[0;31m'
nc='\033[0m'

cd youtube-income-commander-mini

# 1. Install dependencies
echo -e "${green}Installing mini-app dependencies...${nc}"
pip install -r requirements.txt

echo -e "${green}Dependencies installed.${nc}"

# 2. Initialize database (if script exists)
if [ -f scripts/init_db.py ]; then
  echo -e "${green}Initializing mini-app database...${nc}"
  python3 scripts/init_db.py
  echo -e "${green}Mini-app database initialized.${nc}"
fi

# 3. Start mini-app in background for health check
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 1 &
MINI_PID=$!
sleep 5
HEALTH_URL="http://localhost:8080/api/health"
HEALTH_STATUS=$(curl -s $HEALTH_URL | grep '"status":"healthy"')
if [ -z "$HEALTH_STATUS" ]; then
  echo -e "${red}Mini-app health check failed!${nc}"
  kill $MINI_PID
  exit 1
else
  echo -e "${green}Mini-app health check passed.${nc}"
fi

# 4. Check log file creation (if logging is implemented)
if [ -f system.log ] && [ -s system.log ]; then
  echo -e "${green}Mini-app system log exists and is not empty.${nc}"
else
  echo -e "${red}Mini-app system log missing or empty!${nc}"
  kill $MINI_PID
  exit 1
fi

# 5. Stop the test server
kill $MINI_PID
sleep 2

# 6. Launch mini-app for production (uncomment if needed)
# uvicorn app:app --host 0.0.0.0 --port 8080 --workers 2

cd ..
echo -e "${green}Mini-app pre-launch validation complete. Ready for production launch.${nc}" 