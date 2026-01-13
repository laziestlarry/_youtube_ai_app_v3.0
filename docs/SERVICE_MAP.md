# Service Map

## AutonomaX (core)
- Backend: Cloud Run `autonomax-api` (FastAPI, `services/autonomax_api/`)
- UI: Cloud Run `autonomax-frontend` (Next.js, `frontend_v3/`)
- UI -> API: `NEXT_PUBLIC_BACKEND_URL` baked at build time

## YouTube AI (cash-cow portfolio)
- Backend: Cloud Run `youtube-ai-backend` (FastAPI, `services/youtube_ai_api/`, optional)
- UI: Cloud Run `youtube-ai-frontend` (Vite, `frontend/`)
- UI -> API: `VITE_API_BASE_URL` baked at build time (falls back to same-origin)

## CI/CD Defaults
- GitHub Actions deploys `autonomax-api`, `autonomax-frontend`, `youtube-ai-frontend`.
- `YOUTUBE_BACKEND_URL` secret overrides the YouTube UI API target; otherwise it uses the AutonomaX API URL.

## Service Env Baselines
- Autonomax backend env: `config/cloudrun.autonomax.env.example`
- YouTube backend env: `config/cloudrun.youtube.env.example`
- YouTube UI env (build-time): `config/cloudrun.youtube.frontend.env.example`
