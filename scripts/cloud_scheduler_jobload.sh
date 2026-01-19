#!/usr/bin/env bash
set -euo pipefail

# Cloud Scheduler + Cloud Run Jobs setup for critical-path jobload.
# Usage: PROJECT_ID=your-project REGION=us-central1 IMAGE=gcr.io/$PROJECT_ID/autonomax-api \
#   SERVICE_ACCOUNT=scheduler-invoker@$PROJECT_ID.iam.gserviceaccount.com \
#   BASE_URL=https://your-api-url \
#   ./scripts/cloud_scheduler_jobload.sh

PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
IMAGE="${IMAGE:-}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-}"
BASE_URL="${BASE_URL:-}"

if [[ -z "$PROJECT_ID" || -z "$IMAGE" || -z "$SERVICE_ACCOUNT" || -z "$BASE_URL" ]]; then
  echo "Missing env vars. Require PROJECT_ID, IMAGE, SERVICE_ACCOUNT, BASE_URL."
  exit 1
fi

run_job() {
  local name="$1"
  shift
  local args_csv
  args_csv=$(IFS=','; echo "$*")
  gcloud run jobs create "$name" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --image "$IMAGE" \
    --command "python3" \
    --args "$args_csv" \
    --set-env-vars "BASE_URL=$BASE_URL" \
    --max-retries 0 \
    --task-timeout 900s \
    --quiet || \
  gcloud run jobs update "$name" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --image "$IMAGE" \
    --command "python3" \
    --args "$args_csv" \
    --set-env-vars "BASE_URL=$BASE_URL" \
    --max-retries 0 \
    --task-timeout 900s \
    --quiet
}

create_schedule() {
  local name="$1"
  local schedule="$2"
  local job_name="$3"
  gcloud scheduler jobs create http "$name" \
    --project "$PROJECT_ID" \
    --schedule "$schedule" \
    --time-zone "UTC" \
    --http-method POST \
    --uri "https://run.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/jobs/$job_name:run" \
    --oidc-service-account-email "$SERVICE_ACCOUNT" \
    --quiet || \
  gcloud scheduler jobs update http "$name" \
    --project "$PROJECT_ID" \
    --schedule "$schedule" \
    --time-zone "UTC" \
    --http-method POST \
    --uri "https://run.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/jobs/$job_name:run" \
    --oidc-service-account-email "$SERVICE_ACCOUNT" \
    --quiet
}

# Critical-path jobs (Cloud Run Jobs)
run_job "cp-revenue-sync" "scripts/run_revenue_sync.py" "--days" "7"
run_job "cp-ledger-monitor" "scripts/monitor_ledger.py"
run_job "cp-growth-snapshot" "scripts/growth_snapshot.py"
run_job "cp-health-report" "scripts/post_deploy_health_report.py"
run_job "cp-shopier-verify" "scripts/verify_shopier_checkout.py"
run_job "cp-alexandria-genesis" "scripts/alexandria_genesis.py"

# Scheduler bindings (UTC)
create_schedule "cp-revenue-sync" "0 */4 * * *" "cp-revenue-sync"
create_schedule "cp-ledger-monitor" "0 * * * *" "cp-ledger-monitor"
create_schedule "cp-growth-snapshot" "15 9 * * *" "cp-growth-snapshot"
create_schedule "cp-health-report" "0 10 * * *" "cp-health-report"
create_schedule "cp-shopier-verify" "30 10 * * *" "cp-shopier-verify"
create_schedule "cp-alexandria-genesis" "30 8 * * 1" "cp-alexandria-genesis"

echo "Cloud Scheduler jobload configured."
