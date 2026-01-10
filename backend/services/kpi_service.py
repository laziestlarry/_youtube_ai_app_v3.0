from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.kpi_metrics_resolver import KPIMetricsResolver
from backend.services.kpi_db_resolver import KPIDatabaseResolver
from backend.services.kpi_analytics_resolver import KPIAnalyticsResolver

DEFAULT_KPI_PATH = Path(__file__).resolve().parents[1] / "config" / "kpi_targets.json"


@dataclass
class KPIActual:
    value: float
    note: Optional[str]
    updated_at: str


class KPIService:
    def __init__(self, config_path: Optional[Path] = None) -> None:
        env_path = os.getenv("KPI_TARGETS_PATH")
        self.config_path = Path(env_path) if env_path else (config_path or DEFAULT_KPI_PATH)
        self._cache: Dict[str, Any] = {}
        self._cache_mtime: Optional[float] = None
        self._actuals: Dict[str, KPIActual] = {}
        self._resolver = KPIMetricsResolver()
        self._db_resolver = KPIDatabaseResolver()
        self._analytics_resolver = KPIAnalyticsResolver()

    def list_kpis(self) -> Dict[str, Any]:
        config = self._load_config()
        items = []
        status_counts = {
            "on_track": 0,
            "at_risk": 0,
            "off_track": 0,
            "unknown": 0,
        }
        for kpi in config.get("kpis", []):
            actual_value, actual_note, actual_updated = self._resolve_actual(kpi)
            status, status_label = self._status_for(kpi, actual_value)
            status_counts[status] += 1
            items.append(
                {
                    **kpi,
                    "actual": actual_value,
                    "actual_note": actual_note,
                    "actual_updated_at": actual_updated,
                    "status": status,
                    "status_label": status_label,
                }
            )

        return {
            "updated_at": config.get("updated_at") or datetime.utcnow().isoformat(),
            "kpis": items,
            "summary": {
                "total": len(items),
                **status_counts,
            },
        }

    async def list_kpis_async(self, session: AsyncSession) -> Dict[str, Any]:
        config = self._load_config()
        items = []
        status_counts = {
            "on_track": 0,
            "at_risk": 0,
            "off_track": 0,
            "unknown": 0,
        }
        for kpi in config.get("kpis", []):
            actual_value, actual_note, actual_updated = await self._resolve_actual_async(kpi, session)
            status, status_label = self._status_for(kpi, actual_value)
            status_counts[status] += 1
            items.append(
                {
                    **kpi,
                    "actual": actual_value,
                    "actual_note": actual_note,
                    "actual_updated_at": actual_updated,
                    "status": status,
                    "status_label": status_label,
                }
            )

        return {
            "updated_at": config.get("updated_at") or datetime.utcnow().isoformat(),
            "kpis": items,
            "summary": {
                "total": len(items),
                **status_counts,
            },
        }

    def update_actuals(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        updated = []
        for item in updates:
            kpi_id = str(item.get("id") or "").strip()
            if not kpi_id:
                continue
            actual = self._parse_float(item.get("actual"))
            if actual is None:
                continue
            note = str(item.get("note") or "").strip() or None
            timestamp = datetime.utcnow().isoformat()
            self._actuals[kpi_id] = KPIActual(value=actual, note=note, updated_at=timestamp)
            updated.append({"id": kpi_id, "actual": actual, "updated_at": timestamp, "note": note})
        return updated

    def _load_config(self) -> Dict[str, Any]:
        path = self.config_path
        if not path.exists():
            return {"kpis": []}
        mtime = path.stat().st_mtime
        if self._cache and self._cache_mtime == mtime:
            return self._cache
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        self._cache = data
        self._cache_mtime = mtime
        return data

    async def _resolve_actual_async(
        self,
        kpi: Dict[str, Any],
        session: AsyncSession
    ) -> Tuple[Optional[float], Optional[str], Optional[str]]:
        kpi_id = str(kpi.get("id") or "")
        if kpi_id in self._actuals:
            actual = self._actuals[kpi_id]
            return actual.value, actual.note, actual.updated_at

        env_key = f"KPI_ACTUAL_{kpi_id.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            parsed = self._parse_float(env_value)
            if parsed is not None:
                return parsed, f"from {env_key}", None

        resolved_value, resolved_note = await self._analytics_resolver.resolve(session, kpi)
        if resolved_value is not None:
            return resolved_value, resolved_note, None

        resolved_value, resolved_note = self._db_resolver.resolve(kpi)
        if resolved_value is not None:
            return resolved_value, resolved_note, None

        resolved_value, resolved_note = self._resolver.resolve(kpi)
        if resolved_value is not None:
            return resolved_value, resolved_note, None

        return None, None, None

    def _resolve_actual(self, kpi: Dict[str, Any]) -> Tuple[Optional[float], Optional[str], Optional[str]]:
        kpi_id = str(kpi.get("id") or "")
        if kpi_id in self._actuals:
            actual = self._actuals[kpi_id]
            return actual.value, actual.note, actual.updated_at

        env_key = f"KPI_ACTUAL_{kpi_id.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            parsed = self._parse_float(env_value)
            if parsed is not None:
                return parsed, f"from {env_key}", None

        resolved_value, resolved_note = self._db_resolver.resolve(kpi)
        if resolved_value is not None:
            return resolved_value, resolved_note, None

        resolved_value, resolved_note = self._resolver.resolve(kpi)
        if resolved_value is not None:
            return resolved_value, resolved_note, None

        return None, None, None

    def _status_for(self, kpi: Dict[str, Any], actual: Optional[float]) -> Tuple[str, str]:
        if actual is None:
            return "unknown", "Awaiting data"
        target = self._parse_float(kpi.get("target"))
        if target is None:
            return "unknown", "Target missing"
        direction = str(kpi.get("direction") or "up").lower()
        if direction not in ("up", "down"):
            direction = "up"

        warn_threshold = 0.9
        if direction == "down":
            if actual <= target:
                return "on_track", "On track"
            if actual <= target / warn_threshold:
                return "at_risk", "At risk"
            return "off_track", "Off track"

        if actual >= target:
            return "on_track", "On track"
        if actual >= target * warn_threshold:
            return "at_risk", "At risk"
        return "off_track", "Off track"

    @staticmethod
    def _parse_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
