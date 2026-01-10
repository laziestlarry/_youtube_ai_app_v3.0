# Golden Sales Routes (Empathy-Led Purchase + Delivery)

This playbook describes why a customer buys, what they experience in each session, and how marketing and operations guide them to a clean purchase and delivery. It also defines recurring cycles so successful flows are recorded and repeated.

## 1) Empathy Sessions: where and why they buy
These are the real-world moments that drive purchase intent.

1) Late-night clarity
- Feeling: "I need a clean path, fast."
- Need: instant access, simple checkout, no surprises.
- Trigger content: short, confident promise + 1 proof point.
- Channel touch: main page hero, Shopier product URL.

2) Deadline rescue
- Feeling: "I must fix this today."
- Need: quick setup, templates, or service kickoff.
- Trigger content: "Launch in 48h" + deliverables list.
- Channel touch: Fiverr listing, Shopify landing.

3) Aspirational upgrade
- Feeling: "I want a premium system, not hacks."
- Need: structured roadmap, expert guidance, status signals.
- Trigger content: case study, tiered offer, ROI anchors.
- Channel touch: main page featured section, Shopier high ticket.

4) Curious explorer
- Feeling: "Show me a clear example first."
- Need: previews, bundles, low-risk starter.
- Trigger content: bundles, sample assets, before/after.
- Channel touch: Etsy or Shopify listing, UTM link.

5) Gift or share moment
- Feeling: "I want something beautiful and easy to share."
- Need: polished visuals, instant delivery, simple checkout.
- Trigger content: elegant mockups, one click CTA.
- Channel touch: Shopier digital bundle.

## 2) Attention grabber content properties
Use these properties across every channel:
- Pattern interrupt: bold headline, large visual, clean contrast.
- Promise: one sentence with time or outcome.
- Proof: review, metric, or screenshot.
- Clarity: 3 bullet deliverables.
- Frictionless CTA: "Buy now" or "Start now".

## 3) Who does what, and when
Use the existing bot roles as the operating team.

- Chimera-LaunchBot (weekly):
  - Publishes listings, verifies Shopier URLs, refreshes pricing.
- Chimera-ContentBot (daily):
  - Posts teasers, bundles, and UTM links.
- Chimera-FulfillBot (real time):
  - Delivers assets, queues fallbacks, triggers onboarding.
- Chimera-InsightBot (weekly):
  - Reviews KPI shifts and best-sellers.

## 4) Main page purchase flow (Shopier first)
1) Attention: hero promise + preview grid.
2) Intent: featured offers with clear price anchor.
3) Decision: benefit bullets + delivery promise.
4) Action: direct Shopier product URL.
5) Confirmation: checkout success page.
6) Fulfillment: delivery link + onboarding.
7) After sales: review request + next offer.

Acceptance:
- Checkout can complete without API key/secret (Shopier URL).
- Delivery sent within minutes (or queued with manual fallback).
- Order is logged with an order ID and SKU.

## 5) Channel flows: before and after sales

### Shopier (primary)
Before sale:
- Landing page -> Shopier product URL.
- UTM links for attribution.
After sale:
- Callback verified -> delivery -> review request.
- Record in logs and earnings.

### Shopify (storefront + bundles)
Before sale:
- SEO page + bundle upsell + FAQ.
After sale:
- Instant download + follow-up offer.

### Etsy (discovery + keywords)
Before sale:
- SEO tags + visual cover + short benefit list.
After sale:
- Bonus asset + review request.

### Fiverr (service trust)
Before sale:
- Gig packages + clear scopes + proof.
After sale:
- Requirements intake + milestone updates + upsell.

## 6) Reverse engineered scenes (from result back to source)
Scene F: Paid order + delivery completed
- Proof: order in panel, delivery log, earnings entry.

Scene E: Checkout success
- Requirements: Shopier URL, correct price, active listing.

Scene D: Decision moment
- Requirements: price anchor, FAQ, delivery promise.

Scene C: Trust building
- Requirements: proof, screenshots, reviews, sample assets.

Scene B: Attention grab
- Requirements: headline + visual + 1 outcome promise.

Scene A: Distribution
- Requirements: UTM links + posting schedule + outreach.

## 7) Golden sales routes (organized)
Route 1: Main page -> Shopier -> digital delivery -> review
Route 2: Social post -> Shopier UTM -> bundle -> review
Route 3: Fiverr gig -> upsell -> Shopier upgrade
Route 4: Shopify bundle -> email follow-up -> Shopier high ticket
Route 5: Etsy discovery -> Shopier bundle for upsell

## 8) Alexandria Protocol Partnering (YouTube AI + BizOp + AutonomaX)
These systems work together as a single revenue engine.

### YouTube AI (Demand Capture)
- Role: attention + trust + lead generation.
- Inputs: BizOp signal list, product catalog, featured offers.
- Outputs: content briefs, CTA destinations, lead magnets.
- Flow: YouTube content -> link to AutonomaX main page -> Shopier checkout.

### BizOp (Opportunity Intelligence)
- Role: decides what to sell and how to position it.
- Inputs: trend signals, competitor pricing, conversion data.
- Outputs: product variants, pricing bands, bundle strategy.
- Flow: BizOp insights -> product catalog updates -> listing updates on Shopier/Shopify/Etsy.

### AutonomaX Ticaret Stüdyosu (Conversion Hub)
- Role: main storefront, narrative, and conversion UX.
- Inputs: updated catalog, listings, previews, reviews.
- Outputs: Shopier traffic, checkout conversions, delivery triggers.
- Flow: main page offers -> Shopier product URL -> fulfillment.

### Alexandria Protocol (Partner Network)
- Role: partnerships, co‑sell, and distribution leverage.
- Inputs: offer catalog + BizOp briefs + success stories.
- Outputs: referral traffic, joint launches, amplified reach.
- Flow: partner posts -> UTM links -> Shopier checkout -> delivery + review.

## 9) Recurring cycles with recorded success
Daily:
- Verify Shopier URLs.
- Post 1 teaser + 1 bundle offer.
- Confirm delivery queue is empty.

Weekly:
- Refresh listings and assets.
- Ingest Shopier exports to logs and earnings.
- Promote top 3 offers.

Monthly:
- Price audit and SKU pruning.
- Update best seller visuals.
- Review KPI shifts and adjust offers.

## 10) Operational ingestion (record success)
Use Shopier exports to keep receipts consistent:
```bash
python3 scripts/ingest_shopier_csv.py --csv /path/to/shopier_orders.csv --mode orders --record net
python3 scripts/ingest_shopier_csv.py --csv /path/to/shopier_payouts.csv --mode payouts --record net
```

Outcome: every successful sale is logged, delivered, and tied to a repeatable route.
