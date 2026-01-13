| Variable Name         | Description                                 | Example Value                |
|----------------------|---------------------------------------------|------------------------------|
| OPENAI_API_KEY       | OpenAI API key for text generation          | sk-...                       |
| SECRET_KEY           | Secret key for JWT and session management   | superlongrandomstring        |
| DATABASE_URL         | Database connection string                  | sqlite+aiosqlite:///./db.db  |
| YOUTUBE_CLIENT_ID    | YouTube API client ID                       | ...                          |
| YOUTUBE_CLIENT_SECRET| YouTube API client secret                   | ...                          |
| YOUTUBE_REFRESH_TOKEN| YouTube API refresh token                   | ...                          |
| GOOGLE_TTS_API_KEY   | Google TTS API key                          | ...                          |
| DALLE_API_KEY        | DALL-E API key                              | ...                          |
| GEMINI_API_KEY       | Gemini API key                              | ...                          |
| GROQ_API_KEY         | Groq API key                                | ...                          |
| SERPER_API_KEY       | Serper API key                              | ...                          |
| REPLICATE_API_KEY    | Replicate API key                           | ...                          |
| FIGMA_API_KEY        | Figma API key                               | ...                          |
| MIDJOURNEY_API_KEY   | Midjourney API key                          | ...                          |
| PRINTBELLE_API_KEY   | Printbelle API key                          | ...                          |
| STRIPE_API_KEY       | Stripe API key                              | ...                          |
| SHOPIFY_API_KEY      | Shopify API key                             | ...                          |
| SHOPIFY_API_SECRET   | Shopify API secret                          | ...                          |
| PAYONEER_CUSTOMER_ID | Payoneer customer ID                        | ...                          |
| DATABASE_URL_PROD    | Production database URL                     | ...                          |
| REDIS_URL_PROD       | Production Redis URL                        | ...                          |
| APP_SECRET_KEY       | Application secret key                      | ...                          |
| KPI_TARGETS_PATH     | Override KPI targets file path              | backend/config/kpi_targets.json |
| KPI_ACTUAL_<ID>      | Inline actual KPI value (per KPI id)        | KPI_ACTUAL_MRR=28000         |
| BACKEND_ORIGIN       | Public backend base URL                     | http://localhost:8000        |
| FRONTEND_ORIGIN      | Public frontend base URL                    | http://localhost:3001        |
| NEXT_PUBLIC_BACKEND_URL | AutonomaX UI API base URL (build-time)   | https://autonomax-api-...    |
| VITE_API_BASE_URL    | YouTube AI UI API base URL (build-time)     | https://youtube-ai-backend-... |
| EMAIL_ENABLED        | Enable SMTP delivery                        | true                         |
| SMTP_HOST            | SMTP host                                   | smtp.gmail.com               |
| SMTP_PORT            | SMTP port                                   | 587                          |
| SMTP_USERNAME        | SMTP username                               | user@example.com             |
| SMTP_PASSWORD        | SMTP password or app password               | ...                          |
| SMTP_APP_PASSWORD    | Optional app password override              | ...                          |
| DELIVERY_FROM_EMAIL  | Sender address                              | support@example.com          |
| REVENUE_REAL_ONLY    | Restrict ledger summaries to real revenue   | true                         |
| VIDEO_PIPELINE_ALLOW_PLACEHOLDERS | Allow placeholder audio/video in pipeline | false |
| VERTEXAI_PROJECT    | Vertex AI project ID                       | propulse-autonomax           |
| VERTEXAI_LOCATION   | Vertex AI region                           | us-central1                  |
| VERTEXAI_MODEL      | Vertex AI model name                       | gemini-1.5-pro-002           |
| VERTEXAI_FALLBACK_TO_OPENAI | Fallback to OpenAI on Vertex errors  | true                         |
| CLOUD_RUN_SERVICE   | Cloud Run service name for log verification | autonomax-api               |
| APP_TARGET          | API entrypoint target (`autonomax` or `youtube`) | autonomax              |
