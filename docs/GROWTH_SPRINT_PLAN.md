# Growth Sprint Plan (Income-First)

Purpose: prioritize the fastest path to a real, verified income transfer while building a durable revenue engine.

## Objective
Achieve a first confirmed paid transaction and log it into the DB-ledger (`revenue_events`) within 7 days, then scale with automated sync and KPI visibility.

## Priority A: First Real Income Transfer (Day 0-7)
1) Confirm Shopier is fully wired
   - Ensure `SHOPIER_PERSONAL_ACCESS_TOKEN` or API key/secret + webhook token are set.
   - Update `docs/commerce/shopier_product_map.json` with real product URLs.
2) Launch a real payment
   - Use `/api/payment/shopier/pay?amount=...&order_id=...&product_name=...`
   - Complete a low-amount test purchase with a real card.
3) Verify callback + ledger
   - Confirm `POST /api/payment/shopier/callback` returns success.
   - Confirm `POST /api/outcomes/sync?days=30` (if needed).
   - Confirm `GET /api/outcomes/summary` shows revenue and sources.

Success Criteria:
- One payment completed in Shopier.
- Revenue visible in `revenue_events` and Outcome Pulse.

## Priority B: Persistent Revenue Sync (Day 3-10)
- Schedule recurring sync
  - Cloud Scheduler posts `POST /api/outcomes/sync?days=30` every 6 hours.
- Backfill Shopier CSV exports into ledger
  - `scripts/ingest_shopier_csv.py --record net --csv <file>`
- Ensure revenue windows are visible
  - `last_24h`, `last_7d`, `last_30d`, `mtd`.

## Priority C: Scale & Conversion (Day 7-30)
- Stripe subscriptions (MRR)
  - Implement webhook-driven PaymentTransaction inserts.
  - Map to `revenue_events` via sync.
- Shopify / Storefront revenue
  - Use Shopify Admin API for product and order ingestion.
- YouTube monetization ingestion
  - Use `VideoRevenue` as the ingestion channel for content earnings.

## Community Building Activities
- Weekly “Outcome Pulse” update post with KPI progress + revenue signal.
- Live demo or build stream once per week; capture clips for short-form.
- Create a private operators group for early adopters (Telegram/Discord).

## Marketing Strategies (Income-First)
- Lead magnet: “Outcome Pulse Starter Pack” with KPI + revenue templates.
- Case-study landing page: before/after revenue graph + automation stack.
- Partnership outreach: micro-influencers + niche SaaS communities.

## KPI Objectives (30 Days)
- KPI unknown ratio < 40%
- Revenue events > 30 in ledger
- 2+ revenue streams active (Shopier + subscription or affiliate)
- 1 stable recurring income source (MRR or weekly orders)

## Reverse-Engineered Task Extraction
Signal → Convert → Fulfill → Record → Scale
- Signal: publish offer + collect intent.
- Convert: payment link + checkout completed.
- Fulfill: automated delivery + confirmation.
- Record: ledger + DB event + KPI update.
- Scale: scheduler + campaign loops + weekly conversion reviews.

## Financial Targets (Baseline)
- First transfer: $10–$50 test order (Shopier).
- Week 2: $200–$500 from productized service.
- Month 1: $1k–$3k combined from Shopier + subscriptions.

## Risks & Mitigation
- Payment not verified: ensure callback tokens are valid.
- Revenue not showing: confirm `revenue_events` inserts and sync job.
- KPI drift: add `/api/outcomes/health` alerts and weekly review.
