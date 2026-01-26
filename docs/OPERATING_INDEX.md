# Operating Index

Purpose: a single reference tying culture, KPI execution, process workflows, and live services together.

**Last Updated:** 2026-01-22

## Live Services
- AutonomaX API: https://autonomax-api-71658389068.us-central1.run.app
- AutonomaX UI (frontend_v3): Cloud Run service `autonomax-frontend`
- YouTube AI API: https://youtube-ai-backend-71658389068.us-central1.run.app
- YouTube AI UI (Vite): https://youtube-ai-frontend-71658389068.us-central1.run.app
- Alexandria UI: https://youtube-ai-frontend-71658389068.us-central1.run.app/alexandria
- Alexandria API: https://youtube-ai-backend-71658389068.us-central1.run.app/api/ai/alexandria

## Business Growth Accelerator Toolkit (NEW)
- **Master Toolkit:** `docs/BUSINESS_GROWTH_ACCELERATOR_TOOLKIT.md`
- **AI Framework Architecture:** `docs/AI_FRAMEWORK_ARCHITECTURE.md`
- **Transformation Roadmap:** `docs/TRANSFORMATION_ROADMAP.md`
- **Training Modules Catalog:** `docs/commerce/TRAINING_MODULES_CATALOG.md`

## Core Operating Docs
- `docs/CULTURE_OPERATING_SYSTEM.md`
- `docs/KPI_EXECUTION_ENGINE.md`
- `docs/REVENUE_STREAMS_WORKFLOW.md`
- `docs/PROCESS_WORKFLOWS.md`
- `docs/RUNNING_SUCCESS_STORY.md`
- `docs/SERVICE_MAP.md`
- `docs/PROJECT_TREE.md`
- `docs/PROJECT_BRIEF_VALUATION_REPORT.md`

## Alexandria Protocol
- Protocol: `docs/alexandria_protocol/THE_ALEXANDRIA_PROTOCOL.md`
- Execution: `docs/alexandria_protocol/EXECUTION_READY_DELIVERY.md`
- Value propositions: `docs/alexandria_protocol/value_propositions.json`

## KPI System
- Config targets: `backend/config/kpi_targets.json`
- API: `/api/kpi/targets`
- Summary: `/api/kpi/summary`

## Outcome Pulse
- API: `/api/outcomes/summary`
- Sync: `POST /api/outcomes/sync?days=30`
- Health: `/api/outcomes/health`
- UI: Opportunity dashboard > Outcome Pulse card (frontend_v3)
- Revenue ledger: `backend/models/revenue.py` (`revenue_events` table)
- Seed script: `scripts/seed_revenue_ledger.py --ledger earnings.json`
- Sync script: `scripts/run_revenue_sync.py --days 30`
