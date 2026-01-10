from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from backend.config.enhanced_settings import settings


class KPIDatabaseResolver:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or self._resolve_db_path()

    def resolve(self, kpi: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
        if not self.db_path or not self.db_path.exists():
            return None, None
        metric = str(kpi.get("metric") or "").strip()
        if not metric:
            return None, None

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if metric == "subscription_mrr":
                    return self._subscription_mrr(cursor)
                if metric == "subscription_arpu":
                    return self._subscription_arpu(cursor)
                if metric == "subscription_retention_rate":
                    return self._subscription_retention(cursor)
                if metric == "affiliate_conversion_rate":
                    return self._affiliate_conversion(cursor)
                if metric == "workflow_velocity":
                    return self._workflow_velocity(cursor)
        except Exception:
            return None, None

        return None, None

    @staticmethod
    def _resolve_db_path() -> Optional[Path]:
        url = settings.database.url if hasattr(settings, "database") else os.getenv("DATABASE_URL", "")
        if not url:
            return Path("youtube_ai.db")
        if url.startswith("sqlite:///"):
            return Path(url.replace("sqlite:///", "", 1))
        if url.startswith("sqlite:////"):
            return Path(url.replace("sqlite:////", "/", 1))
        return Path("youtube_ai.db")

    @staticmethod
    def _table_exists(cursor: sqlite3.Cursor, name: str) -> bool:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cursor.fetchone() is not None

    def _subscription_mrr(self, cursor: sqlite3.Cursor) -> Tuple[Optional[float], Optional[str]]:
        if not self._table_exists(cursor, "user_subscriptions"):
            return None, None
        cursor.execute("SELECT COALESCE(SUM(total_revenue_this_month), 0) AS total FROM user_subscriptions WHERE status = 'active'")
        row = cursor.fetchone()
        return float(row["total"]), "Sum of active subscription revenue"

    def _subscription_arpu(self, cursor: sqlite3.Cursor) -> Tuple[Optional[float], Optional[str]]:
        if not self._table_exists(cursor, "user_subscriptions"):
            return None, None
        cursor.execute("SELECT COUNT(*) AS cnt, COALESCE(SUM(total_revenue_this_month), 0) AS total FROM user_subscriptions WHERE status = 'active'")
        row = cursor.fetchone()
        if not row["cnt"]:
            return None, None
        return float(row["total"]) / float(row["cnt"]), "Average revenue per active subscriber"

    def _subscription_retention(self, cursor: sqlite3.Cursor) -> Tuple[Optional[float], Optional[str]]:
        if not self._table_exists(cursor, "user_subscriptions"):
            return None, None
        cursor.execute("SELECT COUNT(*) AS cnt FROM user_subscriptions")
        total = cursor.fetchone()["cnt"]
        if not total:
            return None, None
        cursor.execute("SELECT COUNT(*) AS cnt FROM user_subscriptions WHERE status = 'active'")
        active = cursor.fetchone()["cnt"]
        return float(active) / float(total), "Active subscriptions / total subscriptions"

    def _affiliate_conversion(self, cursor: sqlite3.Cursor) -> Tuple[Optional[float], Optional[str]]:
        if not self._table_exists(cursor, "affiliate_clicks") or not self._table_exists(cursor, "affiliate_conversions"):
            return None, None
        cursor.execute("SELECT COUNT(*) AS cnt FROM affiliate_clicks")
        clicks = cursor.fetchone()["cnt"]
        if not clicks:
            return None, None
        cursor.execute("SELECT COUNT(*) AS cnt FROM affiliate_conversions")
        conversions = cursor.fetchone()["cnt"]
        return float(conversions) / float(clicks), "Conversions / clicks"

    def _workflow_velocity(self, cursor: sqlite3.Cursor) -> Tuple[Optional[float], Optional[str]]:
        if not self._table_exists(cursor, "workflow_cards"):
            return None, None
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM workflow_cards WHERE created_at >= datetime('now', '-7 days')"
        )
        row = cursor.fetchone()
        return float(row["cnt"]), "Workflow cards created in last 7 days"
