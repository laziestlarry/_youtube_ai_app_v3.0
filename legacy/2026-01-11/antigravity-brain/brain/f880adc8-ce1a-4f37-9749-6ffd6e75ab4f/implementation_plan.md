# Synchronizing Real-World Asset Previews

This plan outlines the steps to replace mock images and stats with real-world visual proof of the AI Agency's operations.

## User Action Required

The user will need to monitor the "Asset Gallery" on the dashboard once the synchronization is active.

## Proposed Changes

### Fulfillment Engine

#### [MODIFY] [fulfillment_engine.py](file:///Users/pq/_youtube_ai_app_v3.0/modules/ai_agency/fulfillment_engine.py)

- Integrate image generation logic for Tier 3 assets.
- Store "Real World Screens" (generated assets) in a `static/assets` directory for synchronization.
- Update the ledger to include paths to these visual assets.

### Dashboard API

#### [MODIFY] [dashboard.py](file:///Users/pq/_youtube_ai_app_v3.0/backend/api/dashboard.py)

- Update `/analytics/videos` and `/content` endpoints to serve real data from the fulfillment history.
- Add a new `/assets/previews` endpoint to serve the generated "Real World Screens".

### Storefront Automation

#### [MODIFY] [deploy_storefront.py](file:///Users/pq/_youtube_ai_app_v3.0/scripts/deploy_storefront.py)

- Ensure the deployment script prioritized "Real" generated assets over Unsplash placeholders.

## Verification Plan

1. **Trigger Fulfillment**: Run a market sprint that includes asset generation.
2. **Verify Asset Persistence**: Ensure images are saved to `static/assets`.
3. **Verify Dashboard Sync**: Call `/api/dashboard/content` and check if the new assets appear in the response.
