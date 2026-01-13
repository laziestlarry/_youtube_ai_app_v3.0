import json
import os
import sqlite3
import subprocess
from datetime import datetime


def _read_jsonl_tail(path: str, limit: int = 5) -> list[dict]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = [line.strip() for line in handle.readlines() if line.strip()]
        payloads = []
        for raw in lines[-limit:]:
            try:
                payloads.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return payloads
    except FileNotFoundError:
        return []


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}


def _inspect_growth_db(db_path: str) -> dict:
    if not os.path.exists(db_path):
        return {"status": "missing", "path": db_path}
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        summary = {"status": "ok", "path": db_path}
        cur.execute("SELECT COUNT(*) AS count FROM growth_ledger_entries")
        summary["ledger_count"] = cur.fetchone()["count"]
        cur.execute(
            "SELECT COUNT(*) AS count FROM growth_ledger_entries WHERE status = 'CLEARED'"
        )
        summary["cleared_count"] = cur.fetchone()["count"]
        cur.execute(
            "SELECT payout_id, amount_cents, status, ledger_count, created_at "
            "FROM growth_payouts ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            summary["latest_payout"] = {
                "payout_id": row["payout_id"],
                "amount": (row["amount_cents"] or 0) / 100.0,
                "status": row["status"],
                "ledger_count": row["ledger_count"],
                "created_at": row["created_at"],
            }
        conn.close()
        return summary
    except Exception as exc:
        return {"status": "error", "path": db_path, "error": str(exc)}


def _read_cloud_run_logs(project_id: str, service: str) -> str:
    if not project_id or not service:
        return "Skip: CLOUD_RUN_SERVICE or GCP_PROJECT_ID not set."
    try:
        result = subprocess.run(
            [
                "gcloud",
                "logging",
                "read",
                f'resource.type="cloud_run_revision" '
                f'resource.labels.service_name="{service}"',
                "--limit",
                "10",
                "--format=json",
                f"--project={project_id}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Skip: gcloud not installed."
    except subprocess.CalledProcessError as exc:
        return f"Skip: gcloud logging read failed ({exc.returncode})."


def main() -> None:
    data_dir = os.getenv("DATA_DIR", ".")
    orders_log = os.path.join(data_dir, "logs", "shopier_orders.jsonl")
    queue_log = os.path.join(data_dir, "logs", "delivery_queue.jsonl")
    earnings_path = os.path.join(data_dir, "earnings.json")
    growth_db = os.getenv("GROWTH_DATABASE_URL", "sqlite:///./growth_engine.db").replace(
        "sqlite:///", ""
    )

    print("== Delivery Logs ==")
    orders_tail = _read_jsonl_tail(orders_log)
    queue_tail = _read_jsonl_tail(queue_log)
    print(json.dumps({"orders_tail": orders_tail, "queue_tail": queue_tail}, indent=2))

    print("\n== Earnings Ledger ==")
    earnings = _read_json(earnings_path)
    if earnings:
        print(json.dumps(earnings, indent=2))
    else:
        print("No earnings ledger found.")

    print("\n== Growth Engine DB ==")
    print(json.dumps(_inspect_growth_db(growth_db), indent=2))

    print("\n== Cloud Run Logs (optional) ==")
    project_id = os.getenv("GCP_PROJECT_ID", "")
    service = os.getenv("CLOUD_RUN_SERVICE", "")
    logs_output = _read_cloud_run_logs(project_id, service)
    if logs_output.startswith("[") or logs_output.startswith("{"):
        try:
            logs_json = json.loads(logs_output)
            print(json.dumps(logs_json, indent=2))
        except json.JSONDecodeError:
            print(logs_output)
    else:
        print(logs_output)

    print(f"\nVerification completed at {datetime.utcnow().isoformat()}Z")


if __name__ == "__main__":
    main()
