#!/bin/bash
# Simple monitoring script

APP_NAME="youtube-income-commander-prod"
HEALTH_URL="http://localhost:8000/health"

while true; do
    if ! curl -f $HEALTH_URL > /dev/null 2>&1; then
        echo "$(date): Health check failed, restarting container..."
        docker restart $APP_NAME
        sleep 30
    fi
    sleep 60
done