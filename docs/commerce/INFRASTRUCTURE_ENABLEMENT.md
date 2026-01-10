# Infrastructure Enablement Plan

This plan hardens the stack for reliable commercialization across Shopier, Shopify, Etsy, Fiverr, and YouTube.

## Environments
- Local: developer validation, mock data
- Staging: production-like settings, test payments
- Production: real payments + real fulfillment

## Services
- Backend API (FastAPI)
- Storefront (Shopier static store or Next.js)
- Business ops dashboards (Next.js)
- Job runners (orchestrate master workflows)

## Core Configuration
- Secrets: store in env or secret manager
- Shopier PAT + webhook token (API key/secret optional)
- Backend/Frontend origins for CORS
- Database URL for persistent ops data

## Deployment Model
- Containerized backend on Cloud Run
- Static storefront hosted by backend or static host
- Scheduler triggers for revenue ops

## Monitoring
- Health endpoint checks
- API error logging + rate-limits
- Revenue ledger integrity checks
- Payment callback verification

## Data Reliability
- Daily export of earnings ledger
- Weekly backups of catalog and orders
- Asset catalog versioning in `docs/commerce/product_catalog.json`

## Security Practices
- Disable hardcoded backdoor keys in production
- Require strong JWT secret
- Lock down CORS in production
- Enforce signature verification for payment callbacks
