# Execution Jobload (Critical Path)

This maps the critical-path delivery sequence to online schedules.

```mermaid
gantt
  dateFormat  YYYY-MM-DD
  title  Critical Path Execution (Start = 2026-01-20)
  section Revenue Spine
  Shopier callback live + verify          :crit, a1, 2026-01-20, 1d
  Digital delivery map verified           :crit, a2, after a1, 1d
  Ledger real-only integrity check        :crit, a3, after a2, 1d
  section Stability
  Cloud Run env + secrets locked          :crit, b1, 2026-01-20, 1d
  Persistent storage configured           :crit, b2, after b1, 1d
  Smoke test (health + checkout)          :crit, b3, after b2, 1d
  section Execution
  Revenue sync + ledger reconciliation    :crit, c1, 2026-01-21, 5d
  KPI snapshot + anomaly scan             :crit, c2, after c1, 5d
  section Delivery Close
  20 sales milestone                       :crit, d1, after c2, 3d
```

## Online Jobload (Cloud Scheduler)
Configured via HTTP calls to the ops endpoints (preferred for Cloud Scheduler):

- `POST /api/ops/run/revenue-sync`
- `POST /api/ops/run/ledger-monitor`
- `POST /api/ops/run/growth-snapshot`
- `POST /api/ops/run/health-report`
- `POST /api/ops/run/shopier-verify`
- `POST /api/ops/run/alexandria-genesis`
- `POST /api/ops/run/global-revenue-sync`
- `POST /api/ops/run/payout-orchestrator`

Use `scripts/cloud_scheduler_http_jobload.sh` to create the schedules.
Optional flags:
- `ENABLE_GLOBAL_SYNC=true` to schedule `global-revenue-sync`.
- `ENABLE_PAYOUT_JOB=true` to schedule `payout-orchestrator`.
- `ENABLE_HOURLY_BATCH=true` with `HOURLY_TASKS=task1,task2` to schedule the batch endpoint.

Example:
`ENABLE_HOURLY_BATCH=true HOURLY_TASKS=revenue-sync,ledger-monitor bash scripts/cloud_scheduler_http_jobload.sh`

## Batch Trigger (Optional)
You can call a single batch endpoint to fan-out tasks:

`POST /api/ops/run`

Example body:
```json
{
  "tasks": ["revenue-sync", "ledger-monitor", "growth-snapshot"],
  "background": true
}
```
