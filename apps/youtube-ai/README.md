# YouTube AI (portfolio)

Revenue-focused product UI for the YouTube AI platform.

## Code entry points
- `apps/youtube-ai/ui` -> Vite dashboard (`frontend/`)
- `apps/youtube-ai/api` -> FastAPI entrypoint (`services/youtube_ai_api/`)
- `apps/youtube-ai/static` -> Storefront + assets (`static/`)

## Cloud Run
- UI service: `youtube-ai-frontend`
- API service: `youtube-ai-backend` (optional, can target Autonomax API)

## Local run
- Backend: `APP_TARGET=youtube bash scripts/start_app.sh`
- UI: `APP_TARGET=youtube bash scripts/dev.sh`
