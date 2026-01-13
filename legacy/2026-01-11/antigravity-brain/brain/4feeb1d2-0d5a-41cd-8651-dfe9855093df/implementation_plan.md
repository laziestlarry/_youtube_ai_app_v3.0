# Implementation Plan: AutonomaX Foundation & Money Maker Migration

Consolidate multiple project versions into a canonical FastAPI/Celery monorepo (`autonomaX/`) as defined in the `monorepo_scaffold_v_1.ts` blueprint. This will enable scalable "Money Maker" executions and professional-grade financial tracking.

## User Review Required

> [!IMPORTANT]
> This plan will migrate logic from `workflow_codebase_updated` and other subfolders into a new `autonomaX/` directory. The existing `tasks.db` should be backed up before migration.

## Proposed Changes

### [NEW] AutonomaX Monorepo Structure

#### [NEW] `autonomaX/apps/api/main.py`

High-speed entry point for the AI Agency.

#### [NEW] `autonomaX/apps/workers/tasks/publish.py`

Shopify worker to push generated "Money Makers" to market.

#### [NEW] `autonomaX/libs/models/schemas.py`

Unified data models for Tasks, Results, and Settlements.

### Base Settlement Layer

#### [MODIFY] `autonomaX/libs/models/schemas.py`

Add `Settlement` table to track:

- `task_id`
- `compute_cost` (OpenAI tokens used)
- `revenue_potential` (Expected Shopify price)
- `status` (Draft, Published, Sold)

---

## Verification Plan

### Automated Tests

1. **Health Check**: Run `curl localhost:8080/health` after starting the API.
2. **Scaffold Dry-Run**: Execute `make draft` to ensure the LangGraph agent can generate a product draft from a brief.

### Manual Verification

1. **Data Integrity**: Verify that the 304 tasks from the old `tasks.db` are recognized or migrated to the new schema.
2. **API Reachability**: Access the Swagger UI at `http://localhost:8080/docs`.
