# Install

1. Backend
   - Create virtual environment.
   - Install from `backend/requirements.txt`.
   - Configure `.env` using `.env.example`.
   - For dev, tables/seed data are auto-created (see `AUTO_CREATE_TABLES`).
   - For production, add Alembic migrations and run them instead of auto-create.

2. Frontend
   - Run `npm install` in `frontend/`.
   - Set `VITE_API_BASE_URL` in `.env`.
   - Start with `npm run dev`.

3. Deployment
   - Containerize backend and host at `api.tekraqual.com`.
   - Deploy frontend static build to CDN host and map `tekraqual.com`.
