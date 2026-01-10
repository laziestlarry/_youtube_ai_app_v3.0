#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PHASE="${1:-all}" # test | deploy | frontend | all

LOCAL_ENV_FILE="${LOCAL_ENV_FILE:-$ROOT_DIR/.env}"
BACKEND_ENV_FILE="${BACKEND_ENV_FILE:-$ROOT_DIR/config/cloudrun.backend.env}"
FRONTEND_ENV_FILE="${FRONTEND_ENV_FILE:-$ROOT_DIR/config/cloudrun.frontend.env}"

REGION="${REGION:-us-central1}"
BACKEND_SERVICE="${BACKEND_SERVICE:-youtube-ai-backend}"
FRONTEND_SERVICE="${FRONTEND_SERVICE:-youtube-ai-frontend}"
CLOUD_SQL_INSTANCE="${CLOUD_SQL_INSTANCE:-${CLOUDSQL_INSTANCE:-}}"
BACKEND_SECRETS="${BACKEND_SECRETS:-SECRET_KEY=youtube-ai-secret-key:latest,SECURITY_SECRET_KEY=youtube-ai-security-secret-key:latest,OPENAI_API_KEY=youtube-ai-openai-api-key:latest,GEMINI_API_KEY=youtube-ai-gemini-api-key:latest,GROQ_API_KEY=youtube-ai-groq-api-key:latest,YOUTUBE_CLIENT_ID=youtube-ai-youtube-client-id:latest,YOUTUBE_CLIENT_SECRET=youtube-ai-youtube-client-secret:latest,YOUTUBE_REFRESH_TOKEN=youtube-ai-youtube-refresh-token:latest,DATABASE_URL=youtube-ai-database-url:latest,SHOPIER_PERSONAL_ACCESS_TOKEN=youtube-ai-shopier-pat:latest,PAYMENT_SHOPIER_API_KEY=youtube-ai-shopier-api-key:latest,PAYMENT_SHOPIER_API_SECRET=youtube-ai-shopier-api-secret:latest,SHOPIER_WEBHOOK_TOKEN=youtube-ai-shopier-webhook-token:latest,SHOPIFY_ADMIN_TOKEN=youtube-ai-shopify-admin-token:latest,SHOPIFY_SHOP_DOMAIN=youtube-ai-shopify-shop-domain:latest,SHOPIFY_STOREFRONT_TOKEN=youtube-ai-shopify-storefront-token:latest}"

log() {
  printf "\n%s\n" "$1" >&2
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Missing required command: $1"
    exit 1
  fi
}

env_file_to_kv() {
  grep -v '^[[:space:]]*#' "$1" \
    | grep -v '^[[:space:]]*$' \
    | grep -v '^PORT=' \
    | grep -v '^NEXT_PUBLIC_BACKEND_URL=' \
    | grep -v '^CLOUD_SQL_INSTANCE=' \
    | tr -d '\r' \
    | paste -sd, -
}

read_env_value() {
  local key="$1"
  local file="$2"
  local line
  line="$(grep -E "^[[:space:]]*${key}=" "$file" | tail -n1 | tr -d '\r')"
  if [ -z "$line" ]; then
    return 0
  fi
  printf "%s" "${line#*=}"
}

resolve_frontend_backend_url() {
  if [ -n "${BACKEND_URL_OVERRIDE:-}" ]; then
    printf "%s" "$BACKEND_URL_OVERRIDE"
    return
  fi
  if [ ! -f "$FRONTEND_ENV_FILE" ]; then
    echo "❌ Frontend env file not found: $FRONTEND_ENV_FILE"
    echo "   Copy config/cloudrun.frontend.env.example to $FRONTEND_ENV_FILE and fill it out."
    exit 1
  fi
  local backend_url
  backend_url="$(read_env_value "NEXT_PUBLIC_BACKEND_URL" "$FRONTEND_ENV_FILE")"
  if [ -z "$backend_url" ]; then
    echo "❌ NEXT_PUBLIC_BACKEND_URL missing in $FRONTEND_ENV_FILE"
    exit 1
  fi
  printf "%s" "$backend_url"
}

run_smoke_tests() {
  log "✅ Running local smoke tests (backend + frontend build)"

  if [ ! -f "$LOCAL_ENV_FILE" ]; then
    echo "❌ Local env file not found: $LOCAL_ENV_FILE"
    echo "   Set LOCAL_ENV_FILE or create .env before testing."
    exit 1
  fi

  if [ ! -x "$ROOT_DIR/venv/bin/python" ]; then
    echo "❌ venv not found at $ROOT_DIR/venv"
    echo "   Run: python3 -m venv venv && ./venv/bin/pip install -r backend/requirements.txt"
    exit 1
  fi

  "$ROOT_DIR/venv/bin/python" - <<'PY'
import importlib
for mod in ("uvicorn", "fastapi"):
    importlib.import_module(mod)
PY

  log "▶️  Running backend health checks via TestClient"
  LOCAL_ENV_FILE="$LOCAL_ENV_FILE" "$ROOT_DIR/venv/bin/python" - <<'PY'
import os
from dotenv import dotenv_values

env_file = os.environ.get("LOCAL_ENV_FILE")
if env_file:
    env_values = dotenv_values(env_file)
    os.environ.update({k: v for k, v in env_values.items() if v is not None})

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
resp = client.get("/health")
assert resp.status_code == 200, resp.text
resp = client.get("/api/status")
assert resp.status_code == 200, resp.text
print("✅ Backend health checks passed")
PY

  if [ ! -d "$ROOT_DIR/frontend_v3/node_modules" ]; then
    echo "❌ frontend_v3/node_modules missing."
    echo "   Run: (cd frontend_v3 && npm ci)"
    exit 1
  fi

  log "▶️  Building frontend_v3 (production)"
  (cd "$ROOT_DIR/frontend_v3" && NEXT_PUBLIC_BACKEND_URL="http://127.0.0.1:8000" npm run build -- --webpack)

  log "✅ Frontend build passed"
}

deploy_backend() {
  log "🚀 Deploying backend to Cloud Run"

  if [ ! -f "$BACKEND_ENV_FILE" ]; then
    echo "❌ Backend env file not found: $BACKEND_ENV_FILE"
    echo "   Copy config/cloudrun.backend.env.example to $BACKEND_ENV_FILE and fill it out."
    exit 1
  fi

  PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
  if [ -z "$PROJECT_ID" ]; then
    echo "❌ gcloud project not set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
  fi

  BACKEND_IMAGE="gcr.io/${PROJECT_ID}/${BACKEND_SERVICE}"
  BACKEND_ENV_VARS="$(env_file_to_kv "$BACKEND_ENV_FILE")"
  CLOUD_SQL_INSTANCE_FILE="$(read_env_value "CLOUD_SQL_INSTANCE" "$BACKEND_ENV_FILE")"
  if [ -n "$CLOUD_SQL_INSTANCE_FILE" ]; then
    CLOUD_SQL_INSTANCE="$CLOUD_SQL_INSTANCE_FILE"
  fi

  gcloud builds submit \
    --config "$ROOT_DIR/cloudbuild.backend.image.yaml" \
    --substitutions "_BACKEND_IMAGE=${BACKEND_IMAGE}" 1>&2

  gcloud run deploy "$BACKEND_SERVICE" \
    --image "$BACKEND_IMAGE" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars "$BACKEND_ENV_VARS" \
    --set-secrets "$BACKEND_SECRETS" \
    ${CLOUD_SQL_INSTANCE:+--add-cloudsql-instances "$CLOUD_SQL_INSTANCE"} 1>&2

  BACKEND_URL="$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" --format='value(status.url)')"
  printf "%s" "$BACKEND_URL"
}

deploy_frontend() {
  local backend_url="$1"

  log "🚀 Deploying frontend_v3 to Cloud Run"

  if [ ! -f "$FRONTEND_ENV_FILE" ]; then
    echo "❌ Frontend env file not found: $FRONTEND_ENV_FILE"
    echo "   Copy config/cloudrun.frontend.env.example to $FRONTEND_ENV_FILE and fill it out."
    exit 1
  fi

  PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
  FRONTEND_IMAGE="gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE}"
  FRONTEND_ENV_VARS="$(env_file_to_kv "$FRONTEND_ENV_FILE")"

  gcloud builds submit \
    --config "$ROOT_DIR/cloudbuild.frontend_v3.image.yaml" \
    --substitutions "_BACKEND_URL=${backend_url},_FRONTEND_IMAGE=${FRONTEND_IMAGE}" 1>&2

  gcloud run deploy "$FRONTEND_SERVICE" \
    --image "$FRONTEND_IMAGE" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars "${FRONTEND_ENV_VARS},NEXT_PUBLIC_BACKEND_URL=${backend_url}" 1>&2

  gcloud run services describe "$FRONTEND_SERVICE" --region "$REGION" --format='value(status.url)'
}

update_backend_cors() {
  local backend_url="$1"
  local frontend_url="$2"

  log "🔒 Tightening backend CORS to frontend URL"

  gcloud run services update "$BACKEND_SERVICE" \
    --region "$REGION" \
    --update-env-vars "SECURITY_CORS_ORIGINS=[\"${frontend_url}\"],FRONTEND_ORIGIN=${frontend_url},BACKEND_ORIGIN=${backend_url}" 1>&2
}

require_cmd curl
if [ "$PHASE" = "deploy" ] || [ "$PHASE" = "frontend" ] || [ "$PHASE" = "all" ]; then
  require_cmd gcloud
fi

if [ "$PHASE" = "test" ] || [ "$PHASE" = "all" ]; then
  require_cmd npm
  run_smoke_tests
fi

if [ "$PHASE" = "deploy" ] || [ "$PHASE" = "all" ]; then
  backend_url="$(deploy_backend)"
  log "✅ Backend live: ${backend_url}"

  frontend_url="$(deploy_frontend "$backend_url")"
  log "✅ Frontend live: ${frontend_url}"

  update_backend_cors "$backend_url" "$frontend_url"
  log "✅ CORS updated for production"
fi

if [ "$PHASE" = "frontend" ]; then
  backend_url="$(resolve_frontend_backend_url)"
  frontend_url="$(deploy_frontend "$backend_url")"
  log "✅ Frontend live: ${frontend_url}"
  update_backend_cors "$backend_url" "$frontend_url"
  log "✅ CORS updated for production"
fi
