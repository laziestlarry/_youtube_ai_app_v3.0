gcloud run deploy youtube-ai-backend \
  --image gcr.io/YOUR_PROJECT_ID/youtube-ai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080