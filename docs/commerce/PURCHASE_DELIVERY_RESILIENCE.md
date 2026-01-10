# Purchase + Delivery Resilience (Real World)

This guide formalizes the real-world purchase flow, delivery completion resilience, and customer success loops. It also defines how operational ingestion keeps logs, payouts, and growth metrics aligned.

## 1) Purchase Flow (Customer → Revenue)
1) **Discovery**: social, YouTube, marketplace, or direct link.
2) **Offer selection**: product page + value summary + pricing anchor.
3) **Checkout**:
   - Shopier: direct product URL (PAT-only).
   - Shopify/Etsy: channel-native checkout.
4) **Payment success**: Shopier callback received, order logged.
5) **Fulfillment**:
   - Digital: download link delivered immediately.
   - Service/training: kickoff + intake within 24-48 hours.
6) **Customer confirmation**: post-delivery check-in.
7) **Retention**: follow-up offers, bundle upgrades, reviews.

## 2) Delivery Resilience (No Single Point of Failure)
- **Primary**: automatic delivery via `backend/services/delivery_service.py`.
- **Fallback**: queued delivery when SMTP/API fails (`logs/delivery_queue.jsonl`).
- **Manual override**: `python3 scripts/manual_shopier_delivery.py --order-id <id> --sku <SKU> --email <email> --amount <amount>`.
- **Verification**: `scripts/verify_shopier_checkout.py` checks storefront + key URLs.
- **Idempotency**: delivery queue + order logs prevent duplicate delivery.

## 3) Customer Success Loop
- **Onboarding**: confirmation + first action steps sent immediately.
- **Progress**: 24h check-in for digital, 48h kickoff for services.
- **Support SLA**: 24h response, 72h resolution.
- **Growth**: review request + cross-sell + upsell campaigns.

## 4) Operational Ingestion (Keep Systems Aligned)
When Shopier exports are downloaded, ingest them to keep logs, payouts, and earnings consistent.

### Ingest Orders CSV
```bash
python3 scripts/ingest_shopier_csv.py --csv /path/to/shopier_orders.csv --mode orders --record net
```
- Logs: `logs/shopier_orders_ingested.jsonl`
- Earnings: adds net amounts to `earnings.json` (if `--record net`).

### Ingest Payouts CSV
```bash
python3 scripts/ingest_shopier_csv.py --csv /path/to/shopier_payouts.csv --mode payouts --record net
```
- Logs: `logs/shopier_payouts.jsonl`
- Earnings: adds payout totals to `earnings.json` (if `--record net`).

### Suggested Cadence
- Daily: ingest new orders and delivery queue.
- Weekly: ingest payout report and reconcile with `earnings.json`.

### Optional Automation (Chimera Ops)
Set paths to Shopier exports and let weekly ops ingest automatically:
```bash
export SHOPIER_ORDERS_CSV=/path/to/shopier_orders.csv
export SHOPIER_PAYOUTS_CSV=/path/to/shopier_payouts.csv
export SHOPIER_RECORD_MODE=net
python3 scripts/chimera_ops.py weekly
```

## 5) Growth Metrics (Tracked)
- Checkout start rate
- Paid conversion rate
- Refund rate
- Delivery success rate
- Review rate
- Repeat purchase rate

## 6) Owner Checklist (Weekly)
- Run order + payout ingestion.
- Validate top Shopier URLs.
- Review delivery queue.
- Confirm weekly payout totals.
- Launch 1 new offer or bundle.
