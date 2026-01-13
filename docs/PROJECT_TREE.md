# Project Tree (Authoritative)

This repo separates Autonomax (core) from YouTube AI (portfolio) while sharing the backend.

## Autonomax
- UI: `frontend_v3/` (Next.js)
- API: `services/autonomax_api/` (FastAPI entrypoint, shared backend)
- Ops: `autonomax/` (workflows, audits)
- Entry point: `apps/autonomax/`
- Cloud Run: `autonomax-api`, `autonomax-frontend`

## YouTube AI
- UI: `frontend/` (Vite)
- API: `services/youtube_ai_api/` (FastAPI entrypoint, shared backend)
- Storefront assets: `static/`
- Entry point: `apps/youtube-ai/`
- Cloud Run: `youtube-ai-frontend`, `youtube-ai-backend` (optional)

## Shared
- `backend/`: shared API implementation
- `services/`: service entrypoints (per-product)
- `modules/`: shared AI + revenue modules
- `scripts/`: deployment, orchestration, ops
- `config/`: env templates + Cloud Run configs
