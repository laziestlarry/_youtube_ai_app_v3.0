# Runbook (Draft)

- Health check: GET `/health` on the backend.
- Logs: check application host logs for FastAPI and frontend errors.
- Common actions:
  - Restart API service if `/health` fails.
  - Roll back to last known-good deployment if errors persist.
- Data: SQLite by default; switch to Postgres for production deployments.
- Security: restrict CORS to your domains before launch.
