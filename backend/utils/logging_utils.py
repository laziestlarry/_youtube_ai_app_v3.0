from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def log_execution(
    action: str,
    status: str = "success",
    details: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Unified execution logger backed by DATA_DIR/logs/execution.log.
    """
    log_entry = {
        "action": action,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {},
        "error": error,
    }

    data_dir = Path(os.getenv("DATA_DIR", ".")).resolve()
    log_file = data_dir / "logs" / "execution.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(log_entry, ensure_ascii=True) + "\n")

    return log_entry
