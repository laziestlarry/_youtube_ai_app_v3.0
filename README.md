# YouTube AI Platform v3.0

## Overview

YouTube AI Platform v3.0 is a professional-grade, profit-centric content creation and management suite. It leverages advanced AI models (GPT-4, DeepSeek, Gemini) to automate the entire YouTube workflow—from niche research and script generation to video production and revenue optimization.

## System Architecture

The platform is built on a modern full-stack architecture:

- **Backend**: FastAPI (Python 3.10+) with Pydantic v2 for robust configuration and schema validation.
- **Frontend**: React with TypeScript, Vite, and Material UI for a high-performance, responsive executive dashboard.
- **Database**: SQLAlchemy with support for SQLite (dev) and PostgreSQL (prod).
- **AI Engine**: Pluggable provider system supporting OpenAI, Groq, and Google Gemini.
- **Integrations**: Direct YouTube Data API v3 and Google OAuth 2.0 integration.

## Folder Structure

- `/src/backend`: Core API and AI services.
- `/src/frontend`: Executive dashboard and user interface.
- `/config`: Configuration templates and environment settings.
- `/scripts`: Setup, building, and maintenance tools.
- `/modules`: Advanced platform modules (marketing, analytics, data simulation).
- `/docs`: Detailed architectural notes, deployment guides, and commercialization strategies.

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

Start the unified platform:

```bash
bash scripts/start_app.sh
```

## Quick Start (Performance Suite)

The platform is equipped with a professional `Makefile` to handle complex orchestration:

- `make setup`: Automated environment & database preparation.
- `make start`: Launch the full-stack system.
- `make dev`: Hot-reload development environment.
- `make kill-port`: Reset local ports (8000, 3001).
- `make test-shopier`: Verify license key authentication.

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
# _youtube_ai_app_v3.0
