#!/bin/bash

IMAGE_NAME="youtube-income-commander-mini"
CONTAINER_NAME="youtube-income-commander-mini-app"
PORT=8080

echo "Building Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

echo "Stopping and removing existing container: $CONTAINER_NAME..."
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

echo "Running new container: $CONTAINER_NAME on port $PORT..."
docker run -d --name $CONTAINER_NAME -p $PORT:$PORT --env-file .env $IMAGE_NAME

echo "Deployment of $IMAGE_NAME complete. Access at http://localhost:$PORT"