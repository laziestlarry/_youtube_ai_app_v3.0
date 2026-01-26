import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List
from threading import Lock

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel

from backend.config.enhanced_settings import settings
from backend.services.config_audit import run_config_audit


router = APIRouter(prefix="/api/ops", tags=["ops"])

ROOT = Path(__file__).resolve().parents[3]
PYTHON = sys.executable


TASKS: Dict[str, Dict[str, object]] = {
    "order-sync": {
        "cmd": [PYTHON, "scripts/run_order_sync.py", "--limit", "100"],
        "log": "logs/order_sync.log",
    },
    "revenue-sync": {
        "cmd": [PYTHON, "scripts/run_revenue_sync.py", "--days", "7"],
        "log": "logs/revenue_sync.log",
    },
    "ledger-monitor": {
        "cmd": [PYTHON, "scripts/monitor_ledger.py"],
        "log": "logs/ledger_monitor.log",
    },
    "growth-snapshot": {
        "cmd": [PYTHON, "scripts/growth_snapshot.py"],
        "log": "logs/growth_snapshot.log",
    },
    "delivery-retry": {
        "cmd": [PYTHON, "scripts/retry_delivery_queue.py", "--max-items", "50"],
        "log": "logs/delivery_retry.log",
    },
    "health-report": {
        "cmd": [PYTHON, "scripts/post_deploy_health_report.py"],
        "log": "logs/health_report.log",
        "env": {"BASE_URL": "BACKEND_ORIGIN"},
    },
    "shopier-verify": {
        "cmd": [PYTHON, "scripts/verify_shopier_checkout.py"],
        "log": "logs/shopier_verify.log",
        "env": {"STOREFRONT_URL": "BACKEND_ORIGIN"},
    },
    "alexandria-genesis": {
        "cmd": [PYTHON, "scripts/alexandria_genesis.py"],
        "log": "logs/alexandria_genesis.log",
    },
    "config-audit": {
        "cmd": [PYTHON, "scripts/config_audit.py"],
        "log": "logs/config_audit.log",
    },
    "global-revenue-sync": {
        "cmd": [PYTHON, "scripts/global_revenue_sync.py"],
        "log": "logs/global_revenue_sync.log",
    },
    "payout-orchestrator": {
        "cmd": [PYTHON, "scripts/orchestrate_bank_payout.py"],
        "log": "logs/payout_orchestrator.log",
    },
    "chimera-daily": {
        "cmd": [PYTHON, "scripts/chimera_ops.py", "daily"],
        "log": "logs/chimera_daily.log",
    },
    "chimera-weekly": {
        "cmd": [PYTHON, "scripts/chimera_ops.py", "weekly"],
        "log": "logs/chimera_weekly.log",
    },
    "chimera-monthly": {
        "cmd": [PYTHON, "scripts/chimera_ops.py", "monthly"],
        "log": "logs/chimera_monthly.log",
    },
}

_last_run: Dict[str, float] = {}
_last_run_lock = Lock()


class OpsBatchRequest(BaseModel):
    tasks: List[str]
    background: bool = True


def _require_admin(request: Request, admin_key: Optional[str]) -> None:
    expected = settings.security.admin_secret_key or os.getenv("ADMIN_SECRET_KEY")
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_SECRET_KEY not configured")
    provided = admin_key or request.headers.get("X-Admin-Key")
    if provided != expected:
        raise HTTPException(status_code=403, detail="Invalid admin key")


def _check_rate_limit(task_name: str) -> None:
    window = int(os.getenv("OPS_RATE_LIMIT_SECONDS", "60") or "60")
    if window <= 0:
        return
    now = time.monotonic()
    with _last_run_lock:
        last = _last_run.get(task_name, 0.0)
        if now - last < window:
            raise HTTPException(status_code=429, detail="Rate limit active for task")
        _last_run[task_name] = now


def _resolve_env(extra: Optional[Dict[str, str]]) -> Dict[str, str]:
    env = os.environ.copy()
    if not extra:
        return env
    for key, env_var in extra.items():
        value = os.getenv(env_var)
        if value:
            env[key] = value
    return env


def _run_task(task_name: str) -> None:
    task = TASKS[task_name]
    log_path = ROOT / str(task.get("log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = task["cmd"]
    env = _resolve_env(task.get("env"))
    started = datetime.now(timezone.utc).isoformat()

    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n[{started}] TASK={task_name} CMD={' '.join(cmd)}\n")
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            handle.write(result.stdout)
        if result.stderr:
            handle.write(result.stderr)
        handle.write(f"[{datetime.now(timezone.utc).isoformat()}] EXIT={result.returncode}\n")


@router.get("/tasks")
def list_tasks():
    return {"tasks": sorted(TASKS.keys())}


@router.post("/run/{task_name}")
def run_task(task_name: str, request: Request, admin_key: Optional[str] = None, background_tasks: BackgroundTasks = None):
    if task_name not in TASKS:
        raise HTTPException(status_code=404, detail="Unknown task")
    _require_admin(request, admin_key)
    _check_rate_limit(task_name)
    if background_tasks is None:
        _run_task(task_name)
        return {"status": "completed", "task": task_name}
    background_tasks.add_task(_run_task, task_name)
    return {"status": "queued", "task": task_name}


@router.post("/run")
def run_batch(request: Request, payload: OpsBatchRequest, admin_key: Optional[str] = None, background_tasks: BackgroundTasks = None):
    _require_admin(request, admin_key)
    results = []
    for task_name in payload.tasks:
        if task_name not in TASKS:
            results.append({"task": task_name, "status": "unknown"})
            continue
        try:
            _check_rate_limit(task_name)
        except HTTPException as exc:
            results.append({"task": task_name, "status": "rate_limited", "detail": exc.detail})
            continue
        if payload.background and background_tasks is not None:
            background_tasks.add_task(_run_task, task_name)
            results.append({"task": task_name, "status": "queued"})
        else:
            _run_task(task_name)
            results.append({"task": task_name, "status": "completed"})
    return {"results": results}


@router.get("/config-audit")
def config_audit(request: Request, admin_key: Optional[str] = None):
    _require_admin(request, admin_key)
    return run_config_audit()
