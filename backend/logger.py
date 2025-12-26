# backend/logger.py
import datetime

log_file = "backend/system.log"

def write_log(event: str):
    with open(log_file, "a") as f:
        now = datetime.datetime.now().isoformat()
        f.write(f"[{now}] {event}\n")

def read_logs(limit: int = 100):
    try:
        with open(log_file, "r") as f:
            return f.readlines()[-limit:]
    except FileNotFoundError:
        return []
