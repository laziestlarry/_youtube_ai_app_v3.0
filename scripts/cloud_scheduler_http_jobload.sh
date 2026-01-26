#!/usr/bin/env bash
set -euo pipefail

# Cloud Scheduler HTTP jobload for ops endpoints.
# Usage:
# PROJECT_ID=your-project REGION=us-central1 BASE_URL=https://your-api-url \
# SERVICE_ACCOUNT=scheduler-invoker@$PROJECT_ID.iam.gserviceaccount.com \
# ADMIN_KEY=your-admin-key ENABLE_GLOBAL_SYNC=true ENABLE_PAYOUT_JOB=true \
# ./scripts/cloud_scheduler_http_jobload.sh

PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
BASE_URL="${BASE_URL:-}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-}"
ADMIN_KEY="${ADMIN_KEY:-}"
ENABLE_GLOBAL_SYNC="${ENABLE_GLOBAL_SYNC:-false}"
ENABLE_PAYOUT_JOB="${ENABLE_PAYOUT_JOB:-false}"
ENABLE_HOURLY_BATCH="${ENABLE_HOURLY_BATCH:-false}"
HOURLY_TASKS="${HOURLY_TASKS:-revenue-sync,ledger-monitor}"

if [[ -z "$PROJECT_ID" || -z "$BASE_URL" || -z "$SERVICE_ACCOUNT" || -z "$ADMIN_KEY" ]]; then
  echo "Missing env vars. Require PROJECT_ID, BASE_URL, SERVICE_ACCOUNT, ADMIN_KEY."
  exit 1
fi

create_schedule() {
  local name="$1"
  local schedule="$2"
  local path="$3"
  local body="${4:-}"
  local headers="X-Admin-Key=$ADMIN_KEY"
  gcloud scheduler jobs create http "$name" \
    --project "$PROJECT_ID" \
    --location "$REGION" \
    --schedule "$schedule" \
    --time-zone "UTC" \
    --http-method POST \
    --uri "${BASE_URL%/}${path}" \
    --headers "$headers" \
    ${body:+--headers "Content-Type=application/json,$headers"} \
    ${body:+--message-body "$body"} \
    --oidc-service-account-email "$SERVICE_ACCOUNT" \
    --quiet || \
  gcloud scheduler jobs update http "$name" \
    --project "$PROJECT_ID" \
    --location "$REGION" \
    --schedule "$schedule" \
    --time-zone "UTC" \
    --http-method POST \
    --uri "${BASE_URL%/}${path}" \
    --headers "$headers" \
    ${body:+--headers "Content-Type=application/json,$headers"} \
    ${body:+--message-body "$body"} \
    --oidc-service-account-email "$SERVICE_ACCOUNT" \
    --quiet
}

create_schedule "cp-revenue-sync" "0 */4 * * *" "/api/ops/run/revenue-sync"
create_schedule "cp-ledger-monitor" "0 * * * *" "/api/ops/run/ledger-monitor"
create_schedule "cp-growth-snapshot" "15 9 * * *" "/api/ops/run/growth-snapshot"
create_schedule "cp-health-report" "0 10 * * *" "/api/ops/run/health-report"
create_schedule "cp-shopier-verify" "30 10 * * *" "/api/ops/run/shopier-verify"
create_schedule "cp-alexandria-genesis" "30 8 * * 1" "/api/ops/run/alexandria-genesis"

if [[ "$ENABLE_GLOBAL_SYNC" == "true" ]]; then
  create_schedule "cp-global-revenue-sync" "30 2 * * *" "/api/ops/run/global-revenue-sync"
fi

if [[ "$ENABLE_PAYOUT_JOB" == "true" ]]; then
  create_schedule "cp-payout-orchestrator" "0 12 * * 5" "/api/ops/run/payout-orchestrator"
fi

if [[ "$ENABLE_HOURLY_BATCH" == "true" ]]; then
  tasks_json=$(printf '%s' "$HOURLY_TASKS" | awk -F',' '{
    printf "{";
    printf "\"tasks\":[";
    for (i=1; i<=NF; i++) {
      printf "\"%s\"", $i;
      if (i < NF) printf ",";
    }
    printf "],\"background\":true}";
  }')
  create_schedule "cp-hourly-batch" "0 * * * *" "/api/ops/run" "$tasks_json"
fi

echo "Cloud Scheduler HTTP jobload configured."
