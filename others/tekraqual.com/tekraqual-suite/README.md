# TekraQual Suite

TekraQual is an AI-assisted readiness and quality scanning platform built to
support the Larry CoPilot Setup and TekraQual Readiness Scan offers.

## 1. Repository Structure

```
tekraqual-suite/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  └─ v1/
│  │  │     ├─ api.py
│  │  │     └─ routes_assessments.py
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  └─ main.py
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ src/
│  │  ├─ api/
│  │  ├─ pages/
│  │  ├─ App.tsx
│  │  └─ main.tsx
│  ├─ package.json
│  └─ .env.example
└─ docs/
   ├─ INSTALL.md
   └─ RUNBOOK.md
```

## 2. Backend – Local Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` based on `.env.example`, then start the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000/api/v1`.

Note: For development, tables and seed data auto-create on startup (see
`AUTO_CREATE_TABLES` in `app/core/config.py`). For production, disable this and
use Alembic migrations.

## 3. Frontend – Local Setup

```bash
cd frontend
npm install
```

Create `.env` or `.env.local` with `VITE_API_BASE_URL=http://localhost:8000/api/v1`
and start the dev server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

## 4. Core Flow

1. Landing page drives users to the scanner.
2. Scanner creates an assessment, posts answers, then submits for scoring.
3. Results page shows overall score, readiness level, and dimension breakdown,
   with a CTA to book implementation.

## 5. Next Steps

- Add Alembic migrations and seed dimensions/questions (auto-seeded in dev by
  default).
- Replace mock questions in the scanner with API-fed questions once API routes
  are available.
- Fill `docs/INSTALL.md` and `docs/RUNBOOK.md` with your deployment and ops
  specifics.
