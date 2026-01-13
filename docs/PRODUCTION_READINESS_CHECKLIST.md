# Production Readiness Checklist

Use this checklist to validate 9-10 score readiness for autonomous operation on Google Cloud.

## Deployment & Infrastructure
- [ ] Cloud Run service deployed from `backend/Dockerfile`
- [ ] Cloud Run uses persistent storage or Cloud SQL for production data
- [ ] `BACKEND_ORIGIN` and `FRONTEND_ORIGIN` set to production domains
- [ ] `DATA_DIR` points to persistent storage mount
- [ ] CI smoke test passes on every deploy

## Payments & Delivery
- [ ] Shopier real callback validated (no mock bypass)
- [ ] `/api/payment/shopier/pay` returns real form (not mock link)
- [ ] Digital delivery map matches assets in `static/downloads`
- [ ] SMTP app password validated or `EMAIL_ENABLED=false`
- [ ] Delivery queue empty after test run

## Revenue Integrity
- [ ] `REVENUE_REAL_ONLY=true` in production
- [ ] Reporting excludes simulated entries
- [ ] Ledger entries show `kind=real` for live orders
- [ ] Payout proof captured (Shopier payout or bank transfer evidence)

## AI Pipeline Safety
- [ ] `VIDEO_PIPELINE_ALLOW_PLACEHOLDERS=false` in production
- [ ] Real TTS/video rendering configured, or pipeline scopes media stages off
- [ ] Thumbnail generation uses real provider

## Monitoring & Ops
- [ ] Cloud Run logs captured for payment, delivery, and payout flows
- [ ] Alerts configured for payment callback failures
- [ ] Incident response playbook published
