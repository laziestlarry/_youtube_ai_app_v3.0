# Autonomax (core)

Primary business engine: consultancy + operations stack.

## Code entry points
- `apps/autonomax/api` -> FastAPI entrypoint (`services/autonomax_api/`)
- `apps/autonomax/ui` -> Next.js UI (`frontend_v3/`)
- `apps/autonomax/ops` -> Autonomax workflows (`autonomax/`)
- `apps/autonomax/static` -> Shopier storefront + assets (`static/`)

## Cloud Run
- API service: `autonomax-api`
- UI service: `autonomax-frontend`

## Local run
- Backend: `APP_TARGET=autonomax bash scripts/start_app.sh`
- UI: `APP_TARGET=autonomax bash scripts/dev.sh`
