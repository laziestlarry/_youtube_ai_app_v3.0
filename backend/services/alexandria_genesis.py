from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Dict, Optional


DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "venv",
    "dist",
    "build",
    "coverage",
    "logs",
    "backups",
    "legacy",
}


DATA_EXTENSIONS = {".json", ".csv", ".yaml", ".yml", ".db", ".sql"}
DOC_EXTENSIONS = {".md", ".txt", ".pdf"}
CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".sh"}
ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".mp4", ".mp3", ".zip"}


@dataclass
class GenesisConfig:
    root: Path
    max_files: int = 2000
    include_dirs: Optional[List[str]] = None
    exclude_dirs: Optional[List[str]] = None


def _normalize_dirs(values: Optional[Iterable[str]]) -> List[str]:
    if not values:
        return []
    return [str(value).strip().strip("/") for value in values if str(value).strip()]


def _iter_files(config: GenesisConfig) -> Iterable[Path]:
    excludes = set(DEFAULT_EXCLUDE_DIRS)
    excludes.update(_normalize_dirs(config.exclude_dirs))
    includes = _normalize_dirs(config.include_dirs)

    count = 0
    for path in config.root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(config.root)
        except ValueError:
            continue
        parts = set(rel.parts)
        if parts & excludes:
            continue
        if includes and not any(str(rel).startswith(include) for include in includes):
            continue
        yield path
        count += 1
        if config.max_files and count >= config.max_files:
            break


def _format_label(path: Path, size_bytes: int) -> Dict[str, str]:
    extension = path.suffix.lower()
    if extension in CODE_EXTENSIONS:
        fmt = "code"
    elif extension in DOC_EXTENSIONS:
        fmt = "document"
    elif extension in DATA_EXTENSIONS:
        fmt = "data"
    elif extension in ASSET_EXTENSIONS:
        fmt = "asset"
    else:
        fmt = "file"

    if size_bytes > 500_000:
        complexity = "high"
    elif size_bytes > 50_000:
        complexity = "medium"
    else:
        complexity = "low"

    domain = "general"
    rel = path.as_posix()
    if rel.startswith("docs/commerce/"):
        domain = "commerce"
    elif rel.startswith("docs/alexandria_protocol/"):
        domain = "alexandria"
    elif rel.startswith("backend/"):
        domain = "backend"
    elif rel.startswith("frontend_v3/"):
        domain = "frontend"
    elif rel.startswith("frontend/"):
        domain = "frontend"
    elif rel.startswith("modules/"):
        domain = "modules"
    elif rel.startswith("scripts/"):
        domain = "automation"
    elif rel.startswith("autonomax/"):
        domain = "autonomax"
    elif rel.startswith("services/"):
        domain = "services"

    return {
        "domain": domain,
        "format": fmt,
        "complexity": complexity,
    }


def _content_type(path: Path) -> str:
    rel = path.as_posix()
    if rel.startswith("docs/commerce/"):
        return "commerce-doc"
    if rel.startswith("docs/alexandria_protocol/"):
        return "alexandria-protocol"
    if rel.startswith("docs/"):
        return "documentation"
    if rel.startswith("backend/"):
        return "backend-service"
    if rel.startswith("frontend_v3/"):
        return "frontend-next"
    if rel.startswith("frontend/"):
        return "frontend-vite"
    if rel.startswith("modules/"):
        return "module"
    if rel.startswith("scripts/"):
        return "automation-script"
    if rel.startswith("autonomax/"):
        return "autonomax-workflow"
    if rel.startswith("services/"):
        return "service-entrypoint"
    if rel.startswith("static/") or rel.startswith("marketing_assets/"):
        return "asset"
    return "file"


def _tags(path: Path) -> List[str]:
    tags = []
    rel = path.as_posix()
    ext = path.suffix.lower().lstrip(".")
    if ext:
        tags.append(ext)
    for part in rel.split("/"):
        if part and part not in {"", ".", ".."}:
            if part.endswith(path.suffix):
                continue
            tags.append(part.replace("_", "-"))
    return sorted(set(tags))


def _value_signals(path: Path) -> Dict[str, bool]:
    rel = path.as_posix()
    return {
        "sellable": "docs/commerce" in rel or "marketing_assets" in rel,
        "service_ready": "modules" in rel or "backend" in rel,
        "automation_ready": "scripts" in rel,
    }


def build_genesis_log(config: GenesisConfig) -> Dict[str, object]:
    entries = []
    root = config.root
    for idx, path in enumerate(_iter_files(config), start=1):
        rel = path.relative_to(root).as_posix()
        file_type = path.suffix.lower().lstrip(".") or "unknown"
        size_bytes = path.stat().st_size if path.exists() else 0

        entry = {
            "id": f"AX-{idx:05d}",
            "file_path": rel,
            "file_type": file_type,
            "content_type": _content_type(path),
            "tags": _tags(path),
            "labels": _format_label(path, size_bytes),
            "collection": rel.split("/", 1)[0] if "/" in rel else rel,
            "copyright_status": "owned",
            "potential_use": ["direct-use"],
            "value_signals": _value_signals(path),
        }
        entries.append(entry)

    payload = {
        "protocol_version": "1.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "system_name": "Project Alexandria",
        "description": "AutonomaX Chimera Genesis Log",
        "source_root": str(root),
        "generated_by": "backend.services.alexandria_genesis",
        "genesis_log": entries,
    }
    return payload


def resolve_genesis_output(root: Path) -> Path:
    data_dir = os.getenv("DATA_DIR", "").strip()
    if not data_dir:
        data_dir = str(root / "data")
    return Path(data_dir) / "alexandria" / "genesis_log.json"


def write_genesis_log(payload: Dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def load_genesis_log(root: Path) -> Optional[Dict[str, object]]:
    data_dir = os.getenv("DATA_DIR", "").strip()
    if not data_dir:
        data_dir = str(root / "data")
    data_path = Path(data_dir) / "alexandria" / "genesis_log.json"
    candidates = [data_path, root / "docs" / "alexandria_protocol" / "genesis_log.json"]
    for path in candidates:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None
