# Operational Automation Plan

This plan defines the automated workflows needed to support multi-channel commerce and reliable delivery.

## Core Pipelines
1) Product Launch Pipeline
- Source asset -> create listing copy -> export images -> publish to channel
- Triggers: new BizOp entry, weekly launch cycle

2) Order Fulfillment Pipeline
- Payment confirmed -> deliver digital link -> log delivery -> request review
- For services: create ticket -> schedule delivery -> send handoff
- For training: enroll user -> send curriculum -> schedule cohort

3) Customer Support Pipeline
- Automated response -> triage -> human escalation if needed
- SLA: respond within 24h, resolve within 72h

4) Reporting Pipeline
- Daily: revenue, orders, channel performance
- Weekly: best-sellers, conversion rates, refund rates
- Weekly: ingest Shopier exports to reconcile payouts and orders

## Automation Hooks (Backend)
- Shopier payment callback -> fulfillment engine
- BizOp refresh -> opportunity list -> product creation prompts
- YouTube content queue -> social posts
- Commander API onboarding -> provision keys -> send docs

## Shopier Auth Strategy
- Use PAT-only auth (`SHOPIER_PERSONAL_ACCESS_TOKEN`).
- API key/secret are optional and not required for core flows.

## Suggested Endpoints
- `POST /api/bizop/refresh` -> refresh opportunity catalog
- `POST /api/payment/shopier/callback` -> order verification
- `POST /api/agency/orchestrate/master` -> recurring revenue ops

## Operational Ingestion
See `docs/commerce/PURCHASE_DELIVERY_RESILIENCE.md` for CSV ingestion of Shopier orders and payouts.
