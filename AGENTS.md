# AGENTS.md - Agent Development Guide

This document provides essential information for AI agents working on this repository.

## Repository Overview

**Name**: AutonomaX + YouTube AI Platform v3.0  
**Type**: Monorepo with shared backend and multiple frontends  
**Primary Languages**: Python (backend), TypeScript (frontends)

### Applications

| App | Path | Framework | Purpose |
|-----|------|-----------|---------|
| Backend API | `backend/` | FastAPI | Shared API for both products |
| AutonomaX UI | `frontend_v3/` | Next.js | Business operations dashboard |
| YouTube AI UI | `frontend/` | React + Vite | Content automation dashboard |

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Cloud Project (for YouTube Data API)

### Setup (Single Command)
```bash
bash scripts/setup.sh
```

This command:
1. Creates Python virtual environment
2. Installs backend dependencies
3. Installs frontend dependencies
4. Initializes the database

### Environment Configuration
```bash
cp config/.env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `SECRET_KEY` - Application secret
- `OPENAI_API_KEY` - OpenAI API key
- `DATABASE_URL` - Database connection string
- `YOUTUBE_API_KEY` - YouTube Data API key (optional)

## Development Commands

### Backend (FastAPI)

```bash
# Start backend server
make start
# Or directly:
python -m uvicorn backend.main:app --reload --port 8000

# Run tests
python -m pytest backend/tests -v

# Run specific test file
python -m pytest backend/tests/test_commerce.py -v

# Run tests with coverage
python -m pytest backend/tests --cov=backend --cov-report=term-missing
```

### Frontend (Next.js - AutonomaX)

```bash
cd frontend_v3

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Run tests (when configured)
npm run test
```

### Frontend (Vite - YouTube AI)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Full Stack Development

```bash
# Start both backend and AutonomaX UI
make dev-autonomax

# Start both backend and YouTube AI UI
make dev-youtube

# Kill processes on ports 8000 and 3001
make kill-port
```

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── api/routes/         # API route handlers
│   ├── models/             # SQLAlchemy models
│   ├── services/           # Business logic services
│   └── tests/              # Pytest test files
├── frontend_v3/            # Next.js AutonomaX UI
│   └── src/
│       ├── app/            # Next.js app router pages
│       ├── components/     # React components
│       └── lib/            # Utilities and helpers
├── frontend/               # Vite YouTube AI UI
├── services/               # Product-specific API entrypoints
├── scripts/                # Setup and maintenance scripts
├── config/                 # Configuration templates
├── docs/                   # Documentation
└── modules/                # Advanced platform modules
```

## Code Style & Conventions

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for function signatures
- Async functions for database operations
- SQLAlchemy 2.0 style queries

### TypeScript (Frontend)
- Use TypeScript strict mode
- React functional components with hooks
- Tailwind CSS for styling
- shadcn/ui component library

### Naming Conventions
- Python: `snake_case` for functions/variables, `PascalCase` for classes
- TypeScript: `camelCase` for functions/variables, `PascalCase` for components
- Files: `snake_case.py` for Python, `kebab-case.tsx` for React components

## Testing

### Backend Tests
```bash
# Run all tests
python -m pytest backend/tests -v

# Run with verbose output
python -m pytest backend/tests -v --tb=short

# Run specific test
python -m pytest backend/tests/test_commerce.py::test_catalog_returns_products -v
```

### Test Files Location
- Backend: `backend/tests/test_*.py`
- Frontend: `frontend_v3/src/**/*.test.tsx` (when added)

## API Reference

- OpenAPI spec: `openapi.json` (auto-generated)
- Swagger UI: `http://localhost:8000/docs` (when backend running)
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints
- `GET /health` - Health check
- `POST /api/auth/login` - User authentication
- `GET /api/commerce/catalog` - Product catalog
- `POST /api/commerce/checkout` - Initiate checkout

## Database

### Schema Location
- Models: `backend/models/`
- Migrations: `backend/migrations/` (Alembic)

### Database Commands
```bash
# Initialize database
python -m backend.scripts.init_db

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head
```

## Deployment

### CI/CD Pipeline
- Triggered on push to `main` branch
- Runs tests via pytest
- Deploys to Google Cloud Run

### Manual Deployment
```bash
# Build and deploy backend
gcloud builds submit --config cloudbuild.yaml

# Deploy frontend
cd frontend_v3 && npm run build
```

## Common Tasks for Agents

### Adding a New API Endpoint
1. Create route handler in `backend/api/routes/`
2. Register route in `backend/main.py`
3. Add Pydantic schemas in `backend/models/schemas.py`
4. Write tests in `backend/tests/`

### Adding a New UI Page
1. Create page in `frontend_v3/src/app/[route]/page.tsx`
2. Add components in `frontend_v3/src/components/`
3. Update navigation if needed

### Modifying Database Schema
1. Update models in `backend/models/`
2. Create Alembic migration
3. Run migration locally to test
4. Update related API endpoints

## Troubleshooting

### Port Already in Use
```bash
make kill-port
```

### Database Connection Issues
```bash
# Check DATABASE_URL in .env
# For local dev, use SQLite:
DATABASE_URL=sqlite:///./app.db
```

### Missing Dependencies
```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend_v3 && npm install
```

## Contact & Support

- Repository: https://github.com/laziestlarry/_youtube_ai_app_v3.0
- Documentation: See `docs/` directory
