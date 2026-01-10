# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
# We include FastAPI for the server and Uvicorn as the ASGI worker.
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Run the web service on container startup.
# Cloud Run automatically sets the PORT environment variable (default 8080).
CMD ["python", "main.py"]

