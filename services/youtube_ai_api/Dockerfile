FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8080

CMD ["uvicorn", "services.youtube_ai_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
