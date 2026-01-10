# Shopier Real-Money Readiness Plan

Before you can realize "real $" in your Shopier account, you must fulfill several legal and technical obligations. This plan outlines the necessary steps to transition from experimental mock data to a production-ready payment flow.

## User Review Required

> [!IMPORTANT]
> **Legal Compliance (Turkey-specific):** Since you are selling digital products/services through Shopier (a Turkish company), you are legally obligated to issue invoices for every sale. While Shopier allows individual sellers, regular commercial activity typically requires establishing a "Şahıs Şirketi" (Sole Proprietorship) to remain compliant with Turkish Tax Law.

> [!WARNING]
> **Digital Goods Refund Policy:** Per Shopier and Turkish Consumer Law, digital goods are generally non-refundable once delivered. However, you must explicitly state this in your "Distance Sales Contract" to avoid disputes.

## Proposed Changes

No immediate code changes are required for the "obligations" themselves, but your environment configuration must be updated.

### [Module] Environment Configuration

Update your `.env` file with production credentials once the Shopier Dashboard steps are complete.

#### [MODIFY] [.env](file:///Users/pq/_youtube_ai_app_v3.0/.env)

- Replace `SHOPIER_API_KEY` with your production key.
- Replace `SHOPIER_API_SECRET` with your production secret.
- **Add** `SHOPIER_WEBHOOK_TOKEN` from the "Settings > Automation" section of Shopier.

### [Module] Shopier Service

#### [MODIFY] [shopier_service.py](file:///Users/pq/_youtube_ai_app_v3.0/modules/ai_agency/shopier_service.py)

- Ensure the `verify_callback` logic uses the `SHOPIER_WEBHOOK_TOKEN` for production verification.

### [Module] Production Deployment Fixes

Correct the structural deployment issues causing 503 errors.

#### [MODIFY] [Dockerfile](file:///Users/pq/_youtube_ai_app_v3.0/backend/Dockerfile)

- Switch base image from `python:alpine` to `python:3.11-slim`.
- Move the Dockerfile execution context to the **Root** of the project to include `modules/` and `static/`.
- Adjust `uvicorn` startup command to `backend.main:app`.

#### [MODIFY] [cloudbuild.yaml](file:///Users/pq/_youtube_ai_app_v3.0/cloudbuild.yaml)

- Use the root-level cloudbuild to ensure all project folders are bundled into the container.

## Online Automation Strategy (Optimum Cron)

To ensure the YouTube AI Platform operates autonomously in production, we have implemented a **Master Pulse** endpoint. This allows you to trigger all essential operations (Sales Refresh + Quantum Scaling) with a single scheduled job.

### Master Revenue Pulse

- **Schedule:** `0 */4 * * *` (Every 4 Hours)
- **Action:** POST to `/api/agency/orchestrate/master`
- **Body:** `{}` (Authentication required)
- **Goal:** Executes a full cycle of storefront optimization and market scaling.

### Secondary: Content Engine

- **Schedule:** `0 8,20 * * *` (Twice Daily)
- **Action:** POST to `/api/agency/orchestrate/service`
- **Body:** `{"workflow_id": "youtube_automation"}`
- **Goal:** Manages the AI video generation pipeline.

> [!TIP]
> **Authentication:** Use an **OIDC Token** in Google Cloud Scheduler for secure access.

## Verification Plan

1. **Dashboard Check:** Verify that Shopier status shows "Active" and "Verified".
2. **$1 Transaction Test:** Create a test product listed at 1 TL. Purchase it using a real credit card.
3. **Ledger Check:** Verfiy that the transaction appears in your backend ledger and the `FulfillmentEngine` triggers the digital asset delivery.
