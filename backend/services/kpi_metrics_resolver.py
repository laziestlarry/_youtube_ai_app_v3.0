from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

try:
    from backend import metrics as prom_metrics
except Exception:  # pragma: no cover - optional dependency
    prom_metrics = None


class KPIMetricsResolver:
    def resolve(self, kpi: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
        if prom_metrics is None:
            return None, None
        metric = str(kpi.get("metric") or "").strip()
        if not metric:
            return None, None

        if metric == "revenue_generated_total":
            total = self._sum_counter(prom_metrics.revenue_generated_total)
            if total is None:
                return None, None
            return float(total), "Prometheus revenue counter (lifetime total)"

        if metric == "http_error_rate":
            total, errors = self._http_request_totals()
            if total is None or total == 0:
                return None, None
            return float(errors / total), "HTTP error rate from request counters"

        if metric == "video_upload_success_rate":
            success = self._sum_counter(prom_metrics.video_upload_success_total)
            failures = self._sum_counter(prom_metrics.video_upload_failure_total)
            if success is None and failures is None:
                return None, None
            success = success or 0.0
            failures = failures or 0.0
            total = success + failures
            if total == 0:
                return None, None
            return float(success / total), "Video upload success rate from counters"

        return None, None

    @staticmethod
    def _sum_counter(metric: Any) -> Optional[float]:
        try:
            total = 0.0
            for family in metric.collect():
                for sample in family.samples:
                    if sample.name != family.name:
                        continue
                    total += float(sample.value)
            return total
        except Exception:
            return None

    @staticmethod
    def _http_request_totals() -> Tuple[Optional[float], Optional[float]]:
        try:
            total = 0.0
            errors = 0.0
            for family in prom_metrics.http_requests_total.collect():
                for sample in family.samples:
                    if sample.name != family.name:
                        continue
                    total += float(sample.value)
                    status = sample.labels.get("status", "")
                    if status.startswith("4") or status.startswith("5"):
                        errors += float(sample.value)
            return total, errors
        except Exception:
            return None, None
