# Channel Launch Playbook

This playbook defines how each channel should be launched, marketed, and maintained for reliable income generation.

## Brand Focus (AutonomaX Commerce)
- Positioning: premium automation + revenue execution studio.
- Voice: confident, precise, outcome-led, no fluff.
- Primary audience: hybrid millennial operators (digital products) + executive teams (consulting/training).
- Visual system: use `static/assets/listings/<SKU>/listing.png` across channels; IntelliWealth uses the two preview PNGs.

## Shopier (Primary Checkout)
- Storefront: served from `/` when `SHOPIER_APP_MODE=true` (Cloud Run backend URL).
- Checkout: use Shopier product URLs when available; fallback `/api/payment/shopier/pay` requires API key/secret.
- Listings: upload from `marketing_assets/channel_shopier.csv`.
- Upload pack: `marketing_assets/shopier_upload_pack.zip` (CSV + listing images + preview PNGs).
- Auth: PAT-only (`SHOPIER_PERSONAL_ACCESS_TOKEN`); API key/secret optional.
- PAT-only batch import: `python3 scripts/shopier_catalog_import.py --env-file .env.shopier`
- Export products: `python3 scripts/shopier_catalog_export.py --env-file .env.shopier`
- Product map: `docs/commerce/shopier_product_map.json` (SKU -> Shopier URL)
- Start: `ENV_FILE=.env.shopier ./scripts/start_shopier_app.sh` (local launch).
- KPI: checkout start rate, paid conversion, refund rate.

## Etsy (Digital Products)
- Listing set: Zen Art Printables, Creator Kit, Hybrid Stack, Notion Dashboard
- SEO tags: 13 tags per listing (color, style, mood, room type)
- Listing assets: 5-10 mockups, 1 bundle preview PDF, usage license text
- Cadence: 3 listings/week for 4 weeks
- KPI: conversion rate, favorites, CTR from tags

## Shopify (Digital + Bundles + SaaS)
- Product pages: clear benefit bullets, FAQ, delivery details
- Bundles: Zen Art Mega, Creator Pro, Commerce Launch Stack
- Upsells: add bundle at checkout, recommend complementary kit
- Publish (update existing SKUs): `python3 scripts/publish_shopify_catalog.py --env-file .env2 --backend-url <backend> --update-existing --update-images`
- Publish (new only): `python3 scripts/publish_shopify_catalog.py --env-file .env2 --backend-url <backend> --skip-existing`
- KPI: AOV, checkout completion, repeat purchase rate

## Fiverr (Services)
- Gigs: YouTube Automation Studio, Shopify Launch Kit
- Packages: Basic/Standard/Premium with delivery timelines
- Assets: portfolio samples, process diagrams, outcome screenshots
- KPI: impressions to clicks, clicks to orders, delivery rating

## Printbelle (Print-on-Demand)
- Products: Zen Art variants
- Listing assets: 4 mockups, 1 wall preview, 1 close-up
- Variants: size and paper options
- KPI: CTR, conversion rate, refund rate

## YouTube (Lead Engine)
- Content themes: automation tips, digital product creation, case studies
- CTA: lead magnet + Shopify store + Fiverr gig links
- Cadence: 2 short-form + 1 long-form weekly
- KPI: subscriber growth, click-through to store, email signups

## Consultancy (Direct + LinkedIn)
- Offers: IntelliWealth Consulting, Profit OS Consulting, Commander API Ops
- Funnel: lead magnet -> discovery call -> scoped proposal
- Collateral: one-page offer + case study PDF + onboarding checklist
- KPI: discovery call bookings, close rate, average deal size

## Training (Direct + Shopify)
- Offers: IntelliWealth Executive Training
- Funnel: webinar -> cohort waitlist -> enrollment
- Assets: curriculum PDF, module previews, testimonials
- KPI: webinar attendance, enrollment conversion, completion rate

## Marketing Support Stack
- SEO: keyword clusters per product (3-5 core phrases)
- Email: 5-step nurture sequence (lead magnet -> product -> bundle -> service)
- Social: 10 reusable templates for reels and posts
- Retargeting: pixel setup for Shopify/YouTube

## Fulfillment & Returns
- Digital: instant delivery + 14-day support window
- Services: scope agreement + milestone delivery
- Returns: clear policy per channel; process exceptions via support inbox

## BizOp Integration
- Refresh catalog: `POST /api/bizop/refresh`
- Use top-ranked opportunities as new product ideas and YouTube content topics
- Cycle: weekly opportunity review -> publish 2 new listings
