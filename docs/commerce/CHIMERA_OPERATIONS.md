# Chimera Operations Playbook

This playbook turns the Chimera entity into a repeatable revenue machine.
It defines bot responsibilities, cadence, and the first-income runbook.

## Roles -> Bots
- Chimera-LaunchBot: listing sync + pricing alignment.
- Chimera-ContentBot: UTM links + campaign copy.
- Chimera-FulfillBot: delivery + onboarding triggers.
- Chimera-InsightBot: KPI digest + best-seller alerts.

## Daily cadence
Command:
```bash
python3 scripts/chimera_ops.py daily
```
Tasks:
1) Verify storefront + top-5 Shopier URLs.
2) Sync Shopier listings (PAT-only).
3) Regenerate channel assets + UTM links.
4) (Optional) Validate Looker Action endpoint with a test payload.
   - Enable with `CHIMERA_LOOKER_TEST=1`.

## Weekly cadence
Command:
```bash
python3 scripts/chimera_ops.py weekly
```
Tasks:
1) Update Shopify listings + images.
2) Rebuild channel CSVs for Etsy/Gumroad.
3) Ingest Shopier order/payout exports (see `docs/commerce/PURCHASE_DELIVERY_RESILIENCE.md`).

## Monthly cadence
Command:
```bash
python3 scripts/chimera_ops.py monthly
```
Tasks:
1) Pricing audit (psychological pricing).
2) SKU pruning + best-seller focus.

## First-Income Runbook (Shopier)
1) Choose a top-5 SKU (recommended: ZEN-ART-BASE).
2) Open its Shopier URL from `docs/commerce/shopier_product_map.json`.
3) Place a real purchase (smallest price tier).
4) Confirm:
   - Order appears in Shopier panel.
   - `/api/payment/shopier/callback` receives success (server logs).
   - Fulfillment sent (delivery email or download link).
5) Capture proof:
   - Screenshot: order confirmation page.
   - Timestamp + order ID.

## Digital delivery automation
- Delivery map: `docs/commerce/digital_delivery_map.json`
- Download asset: `static/downloads/`
- Queue fallback: `logs/delivery_queue.jsonl`
- Manual delivery (if needed): `python3 scripts/manual_shopier_delivery.py --order-id <id> --sku ZEN-ART-BASE --email <email> --amount <amount>`

## Looker Action Orchestration (optional)
Endpoint:
```
POST https://youtube-ai-backend-lenljbhrqq-uc.a.run.app/api/looker/trigger
```
Test command:
```bash
python3 scripts/looker_action_trigger.py
```
If you want token protection, set `LOOKER_ACTION_TOKEN` and send it as `X-Looker-Token`.
Use `LOOKER_ACTION_MODE=queue` to store triggers without executing workflows.

## KPI targets (Golden State)
- Checkout start rate ≥ 8%
- Paid conversion ≥ 2.5%
- Refund rate ≤ 3%
- 3+ recurring offers active

## Quick references
- Shopier URLs: `docs/commerce/shopier_product_map.json`
- Listings CSVs: `marketing_assets/`
- Storefront: `https://youtube-ai-backend-lenljbhrqq-uc.a.run.app/`
