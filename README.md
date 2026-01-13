# Autonomax + YouTube AI Platform

## Overview

This repo hosts two linked products:
- **Autonomax**: core business engine for consultancy, operations, and automation.
- **YouTube AI**: portfolio cash-cow product focused on content automation and monetization.

## System Architecture

Shared backend with separate UIs:

- **Backend**: FastAPI (Python 3.10+) with Pydantic v2.
- **Autonomax UI**: Next.js (`frontend_v3`).
- **YouTube AI UI**: React + Vite (`frontend`).
- **Database**: SQLAlchemy with support for SQLite (dev) and PostgreSQL (prod).
- **AI Engine**: Pluggable provider system supporting OpenAI, Groq, and Google Gemini.
- **Integrations**: Direct YouTube Data API v3 and Google OAuth 2.0 integration.

## Folder Structure

- `/backend`: Core API and AI services (shared).
- `/services`: Product-specific API entrypoints.
- `/frontend`: YouTube AI Vite dashboard.
- `/frontend_v3`: Autonomax Next.js dashboard.
- `/autonomax`: Autonomax workflows and ops assets.
- `/apps`: Product-level entry points (symlinks).
- `/config`: Configuration templates and environment settings.
- `/scripts`: Setup, building, and maintenance tools.
- `/modules`: Advanced platform modules.
- `/docs`: Architecture notes, deployment guides, and commercialization strategies.

## Product Map

See `apps/README.md` and `docs/SERVICE_MAP.md` for the authoritative service + folder map.

## Getting Started

### 1. Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher (for frontend development)
- Google Cloud Project with YouTube Data API v3 enabled

### 2. Setup

Run the consolidated setup script to prepare the environment:

```bash
bash scripts/setup.sh
```

### 3. Configuration

Copy the environment template and configure your API keys:

```bash
cp config/.env.example .env
# Edit .env with your credentials
```

### 4. Launch

Start the shared backend:

```bash
APP_TARGET=autonomax bash scripts/start_app.sh
```

Start a UI:

```bash
# Autonomax UI (Next.js)
APP_TARGET=autonomax bash scripts/dev.sh

# YouTube AI UI (Vite)
APP_TARGET=youtube bash scripts/dev.sh
```

## Quick Start (Performance Suite)

The platform is equipped with a professional `Makefile` to handle complex orchestration:

- `make setup`: Automated environment & database preparation.
- `make start`: Launch the full-stack system.
- `make dev`: Hot-reload development environment.
- `make kill-port`: Reset local ports (8000, 3001).
- `make test-shopier`: Verify license key authentication.

## Local AI (Ollama)

- Start Ollama locally: `ollama serve` then `ollama pull llama3.2` (or your `OLLAMA_MODEL`).
- In `.env`, set `OLLAMA_URL`, `OLLAMA_MODEL`, and `CHIMERA_DEFAULT_MODE=hybrid` for local-first with cloud fallback.
- Run `make dev` for dual backend/frontend hot-reload (ports 8000 and 3001) with the Chimera Engine preferring Ollama.

## Payments / Shopier Status

- Shopier gateway remains approval-gated; real payments require `PAYMENT_SHOPIER_*` credentials. `make test-shopier` will only succeed after approval.
- Until approval completes, the `/api/payment/shopier/pay` endpoint returns the mock link; continue using other configured channels (e.g., admin master key login or alternative processors) for access and fulfillment.

## Shopier App Mode

- Run a Shopier-only storefront + backend by copying `config/shopier.env.example` to `.env.shopier`.
- Start it with `make shopier` (or `ENV_FILE=.env.shopier bash scripts/start_shopier_app.sh`).
- The storefront is served from `static/store.html` when `SHOPIER_APP_MODE=true`.

## Professional Modules

- **YouTube Income Commander**: A standalone revenue module located in `/modules/mini_app`. Launch via `make mini-app`.
- **Shopier Integration**: Integrated "Plug-and-Play" license key bypass for immediate launch without Stripe.

## Professional Features

- **Projected Revenue Forecasting**: AI-driven predictive analytics.
- **Automated Workflow Engine**: Move content from idea to production via the Workflow board.
- **Multi-Model Support**: Switch between AI providers for cost and quality optimization.
- **Revenue Dashboard**: Track multi-source income including subscription and affiliate revenue.

---
**Senior Architect Note**: Version 3.0 represents a clean, audited, and hardened deliverable. It is the single authoritative source for platform execution.
