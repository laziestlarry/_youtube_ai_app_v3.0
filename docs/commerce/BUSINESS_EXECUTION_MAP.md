# Business Execution Map

This document maps opportunities to execution, separates products vs engines vs subscriptions,
and defines the CI/CD and operational setup for stable, income-generating delivery.

## 1) Simplified Business Map

### Products (digital + service offers)
- Digital: Zen Art bundles, Creator Kits, Launch Kits, SOP Vault, Notion dashboards.
- Services: Fiverr AI gigs, YouTube Automation, Shopify setup, Consulting/Training offers.

### Engines (systems that move offers from discovery to delivery)
- Opportunity Engine: BizOp refresh, scoring, selection.
- Listing Engine: Shopier/Shopify/Etsy listing prep + publishing.
- Fulfillment Engine: digital delivery, service scheduling, ticketing.
- Support Engine: support triage, SLA, refunds, reviews.
- Growth Engine: SEO content, social, partnerships, community.
- Insight Engine: KPI reporting, best-seller tracking, conversion alerts.

### Subscriptions (recurring revenue)
- AutonomaX SaaS.
- Bopper Income Platform.
- Commander API Ops (managed access).

## 2) Autonomous Execution Loop (Opportunity -> Revenue)
1) Intake: refresh opportunities (BizOp) and update scores.
2) Selection: choose top 3 (fastest time-to-market, low risk, high margin).
3) Packaging: finalize offer, pricing, and assets.
4) Listing: publish to Shopier, Shopify, Etsy (per channel playbook).
5) Fulfillment: auto-deliver digital goods or schedule services.
6) Support: SLA response, refund policy, review collection.
7) Growth: weekly content + conversion optimization.
8) Review: measure KPIs, promote best-sellers, sunset weak offers.

## 3) First List of Business Cases (Top-Tier Execution Plan)
Aligned to Alexandria Tier-1 and ranked opportunities.

### Case 1: Fiverr AI Automation & Content Services (7-day launch)
Steps:
1) Prepare gig assets and SEO copy.
2) Publish Fiverr gigs and connect Shopier checkout for upgrades.
3) Enable fulfillment pipeline for service delivery milestones.

Status: Queued
Primary assets: `docs/commerce/LISTING_COPY.md`, `docs/commerce/PRODUCT_PORTFOLIO.md`

### Case 2: ZentronomaX Minimalist Digital Art Shop (7-day launch)
Steps:
1) Export art bundles and thumbnails.
2) Publish listings on Shopier and Shopify; prep Etsy CSV.
3) Activate instant digital delivery and review flow.

Status: Shopier and Shopify live, Etsy prepared
Primary assets: `docs/commerce/product_catalog.json`, `marketing_assets/channel_etsy.csv`

### Case 3: AutonomaX Universal Automation SaaS (30-day beta)
Steps:
1) Define beta offer and pricing tiers.
2) Launch onboarding flow and waitlist.
3) Run first cohort and collect feedback for v1.1.

Status: Planned
Primary assets: `docs/commerce/PRODUCT_PORTFOLIO.md`, `docs/commerce/OPERATIONAL_AUTOMATION.md`

## 3.1) Top 5 Business Cases (Execution Parameters)

| Rank | Offer | SKU | Primary Channel | Checkout Path | Price Band | Cover Asset | KPI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Fiverr AI Automation & Content Services | FIVERR-KIT-01 | Fiverr + Shopier | Shopier product URL | TRY 2.899 - 7.699 | `static/assets/` (Google/YouTube cover) | Checkout start rate |
| 2 | ZentronomaX Minimalist Digital Art | ZEN-ART-BASE | Shopier + Shopify | Shopier product URL | TRY 1.499 - 4.999 | `static/assets/` (collections cover) | Paid conversion |
| 3 | AutonomaX SaaS | AX-SAAS-01 | Shopier | Shopier product URL | TRY 7.699 - 9.799 | `static/assets/` (SaaS cover) | Subscription start |
| 4 | YouTube Automation Studio | YT-AUTO-01 | Shopier | Shopier product URL | TRY 4.999 - 9.799 | `static/assets/` (YouTube cover) | Qualified lead rate |
| 5 | Bopper Income Platform | BOP-SAAS-01 | Shopier | Shopier product URL | TRY 2.899 - 6.999 | `static/assets/` (platform cover) | Subscription start |

## 4) CI/CD and Operational Prerequisites

### Required supplies
- Environment files: `config/cloudrun.backend.env`, `config/cloudrun.frontend.env`
- Secrets in Cloud Run: Shopier PAT, Shopify tokens, AI keys
- Catalog data: `docs/commerce/product_catalog.json`
- Pricing overrides: `docs/commerce/shopier_price_overrides.json`
- Listing exports: `marketing_assets/`

### CI/CD pipeline (minimal, stable path)
1) Test: `./scripts/cloud_run_launch.sh test`
2) Build + deploy: `./scripts/cloud_run_launch.sh deploy`
3) Smoke checks: `/health`, `/api/status`, storefront load, chat endpoint

### Job runners (operational execution)
- Daily: listing sync, revenue logs, best-seller refresh
- Weekly: new SKU batch, Etsy export, Shopify image refresh
- Monthly: pricing review, refunds review, portfolio pruning

## 5) Localization and Pricing Matrix

### Current state
- Primary locale: Turkish (TR)
- Currency: TRY on Shopier storefront
- Price rounding: psychological pricing in `scripts/shopier_catalog_import.py`

### Adjustments for international ops
- Shopify/Etsy: USD + EUR listings via channel exports
- Translation source: `docs/commerce/product_catalog.json`
- Pricing strategy:
  - Local: TRY with .99 endings and 500-1000 band rounding
  - International: USD/EUR with tiered pricing bands by product type

## 6) Current Status and Activation Tests

### Live endpoints
- Backend: `https://youtube-ai-backend-lenljbhrqq-uc.a.run.app`
- Storefront: `https://youtube-ai-backend-lenljbhrqq-uc.a.run.app/`

### Activation checks (latest)
- `/health`: 200
- `/api/status`: 200
- `/`: 200

### CI smoke checks
- `./scripts/cloud_run_launch.sh test`: passed (backend health + frontend build)

### Channel sync (latest)
- Shopier: products updated and mapped to direct URLs.
- Shopify: listings updated from catalog (14 items).
- Etsy: CSV ready at `marketing_assets/channel_etsy.csv`.

### Channel readiness
| Channel | Status | Next action |
| --- | --- | --- |
| Shopier | Live | Keep listings synced |
| Shopify | Live | Add new SKUs + refresh images |
| Etsy | Prepared | Upload CSV from `marketing_assets/channel_etsy.csv` |
| Fiverr | Queued | Publish gigs, connect upsell checkout |
