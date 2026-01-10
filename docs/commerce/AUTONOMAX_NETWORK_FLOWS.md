# AutonomaX API Integration (Network Flows)

This guide connects AutonomaX API with the Commerce Studio to orchestrate pricing, campaigns, growth, and ops signals.

## Configuration
Set these environment variables (Cloud Run or local):
- `AUTONOMAX_API_URL=https://autonomax-api-71658389068.us-central1.run.app`
- `AUTONOMAX_API_KEY=...` (optional if the API requires auth)

## Benefits Payload (from prior generations)
We use existing catalog data as the "benefits" payload:
- `short_description`
- `long_description`
- `tags`
- `channels`

Source: `docs/commerce/product_catalog.json`

## Orchestration Script
Use the orchestrator to submit portfolio, pricing, campaign, and ops signals.

```bash
python3 scripts/autonomax_orchestrate.py --mode all --dry-run
python3 scripts/autonomax_orchestrate.py --mode all
```

Modes:
- `portfolio` -> `/portfolio/score`
- `pricing` -> `/monetization/price_suggest`
- `campaigns` -> `/marketing/campaigns/suggest`
- `ops` -> `/ops/lifecycle/batch`

## Event Wiring (Shopier → AutonomaX)
On successful Shopier payment, a lifecycle event is sent to:
- `/growth/lifecycle`
- `/ops/lifecycle/batch`

This is handled in `backend/api/routes/payment.py` via `backend/services/autonomax_api_service.py`.

## Suggested Network Flow
1) Sync portfolio: score the catalog.
2) Suggest pricing: align with psychological pricing.
3) Suggest campaigns: align channel + offer.
4) Execute ops batch: catalog + UTM + pricing audits.
5) Capture real sales: Shopier callback sends lifecycle events.

## Troubleshooting
- If calls fail, check `AUTONOMAX_API_URL` and `AUTONOMAX_API_KEY`.
- Use `--dry-run` to inspect payloads before sending.
