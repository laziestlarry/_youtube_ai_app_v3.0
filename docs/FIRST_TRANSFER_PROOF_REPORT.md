# First Transfer Proof Report

Report date (UTC): 2026-01-11T01:22:31Z
Project: /Users/pq/_youtube_ai_app_v3.0

## Summary
Local end-to-end payment flow completed with delivery marked as delivered and ledger updated. Growth engine payout state is PROCESSING. Cloud Run log verification succeeded, but the production smoke test hit a 404 on `/api/payment/shopier/pay` (indicating the running service is not the updated backend or routing is misconfigured).

## Environment
- Base URL: http://localhost:8000
- Data dir: default (local)
- Email: enabled (SMTP successful on latest run)

## Test Steps Executed
1) Smoke test: `python scripts/first_transfer_smoke.py`
2) Verification: `python scripts/first_transfer_verify.py`
3) Production smoke test: `BASE_URL=https://autonomax-api-71658389068.us-central1.run.app python scripts/first_transfer_smoke.py` (404)

## Evidence
### Latest Delivered Order
- Order ID: ZEN-ART-BASE-1768094487
- SKU: ZEN-ART-BASE
- Amount: 19.99 USD
- Delivery URL: http://localhost:8000/static/downloads/Zen_Art_Printables.pdf
- Status: delivered (email sent)

### Delivery Logs (Tail)
- `logs/shopier_orders.jsonl` contains delivered record for order ZEN-ART-BASE-1768094487
- `logs/delivery_queue.jsonl` still contains older queued records from prior SMTP failures

### Earnings Ledger
- `earnings.json` includes three "Shopier Order" entries for recent test orders
- Latest real entry: ZEN-ART-BASE-1768094487 (kind=real, channel=shopier)

### Growth Engine Payout
- Growth DB: ./growth_engine.db
- Ledger count: 17, cleared: 17
- Latest payout: TR-DA28DDBD, status=PROCESSING, amount=29100.72, ledger_count=17

### Cloud Run Evidence
- Project: propulse-autonomax
- Service: autonomax-api
- Recent logs show healthy startup and HTTP 200 on `/` (see `scripts/first_transfer_verify.py` output)

## Known Gaps / Risks
- Historical queued delivery records remain from previous SMTP failures.
- Earnings ledger contains both simulated and real entries; production reports should filter to kind=real.
- Cloud Run payment endpoint returned 404 during smoke test; deploy target or routing likely misaligned.

## Next Actions
1) Deploy the updated backend to Cloud Run and re-run the production smoke test.
2) Clear or reconcile queued delivery records after confirming email delivery success.
3) Keep `REVENUE_REAL_ONLY=true` in production reporting paths.
