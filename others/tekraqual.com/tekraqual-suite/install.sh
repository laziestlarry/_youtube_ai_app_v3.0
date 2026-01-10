#!/usr/bin/env bash
set -euo pipefail

# TekraQual Suite setup helper
# Usage: bash install.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[TekraQual] Setting up backend (FastAPI)"
cd "$ROOT_DIR/backend"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "[TekraQual] Setting up frontend (React)"
cd "$ROOT_DIR/frontend"
npm install

echo "[TekraQual] Done. Start backend with 'uvicorn app.main:app --reload' and frontend with 'npm run dev'."
