FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for numpy, pandas, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy everything from root
COPY . .

# Install dependencies from backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8080

# Start with the full module path
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
