from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bizop import BizOpportunity
from backend.models.revenue import RevenueEvent
from backend.models.workflow import WorkflowCard
from backend.services.kpi_service import KPIService


class OutcomeService:
    def __init__(self) -> None:
        self._kpi_service = KPIService()

    async def summary(self, session: AsyncSession) -> Dict[str, Any]:
        kpi_payload = await self._kpi_service.list_kpis_async(session)
        revenue_payload = await self._revenue_summary(session)
        pipeline_payload = await self._pipeline_summary(session)

        return {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "kpi": {
                "updated_at": kpi_payload.get("updated_at"),
                "summary": kpi_payload.get("summary", {}),
            },
            "revenue": revenue_payload,
            "pipeline": pipeline_payload,
        }

    async def _revenue_summary(self, session: AsyncSession) -> Dict[str, Any]:
        db_payload = await self._revenue_summary_db(session)
        if db_payload is not None:
            return db_payload
        return self._revenue_summary_ledger()

    def _revenue_summary_ledger(self) -> Dict[str, Any]:
        try:
            from modules.ai_agency.fulfillment_engine import fulfillment_engine

            data = fulfillment_engine.get_earnings_summary()
        except Exception:
            return {
                "total": 0.0,
                "daily": 0.0,
                "last_24h": 0.0,
                "last_7d": 0.0,
                "last_30d": 0.0,
                "mtd": 0.0,
                "top_sources": [],
            }

        total = float(data.get("total_earnings", 0.0) or 0.0)
        daily = float(data.get("daily", 0.0) or 0.0)
        history = data.get("history", [])

        last_24h, last_7d, last_30d, mtd, top_sources = self._summarize_revenue_history(history)

        return {
            "total": total,
            "daily": daily,
            "last_24h": last_24h,
            "last_7d": last_7d,
            "last_30d": last_30d,
            "mtd": mtd,
            "top_sources": top_sources,
        }

    async def _revenue_summary_db(self, session: AsyncSession) -> Dict[str, Any] | None:
        try:
            count_stmt = select(func.count(RevenueEvent.id))
            count_result = await session.execute(count_stmt)
            total_events = int(count_result.scalar() or 0)
            if total_events == 0:
                return None

            now = datetime.now(timezone.utc)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            last_24h_cutoff = now - timedelta(hours=24)
            last_7d_cutoff = now - timedelta(days=7)
            last_30d_cutoff = now - timedelta(days=30)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            total_stmt = select(func.coalesce(func.sum(RevenueEvent.amount), 0.0))
            daily_stmt = select(func.coalesce(func.sum(RevenueEvent.amount), 0.0)).where(
                RevenueEvent.occurred_at >= start_of_day
            )
            last_24h_stmt = select(func.coalesce(func.sum(RevenueEvent.amount), 0.0)).where(
                RevenueEvent.occurred_at >= last_24h_cutoff
            )
            last_7d_stmt = select(func.coalesce(func.sum(RevenueEvent.amount), 0.0)).where(
                RevenueEvent.occurred_at >= last_7d_cutoff
            )
            last_30d_stmt = select(func.coalesce(func.sum(RevenueEvent.amount), 0.0)).where(
                RevenueEvent.occurred_at >= last_30d_cutoff
            )
            mtd_stmt = select(func.coalesce(func.sum(RevenueEvent.amount), 0.0)).where(
                RevenueEvent.occurred_at >= month_start
            )

            top_stmt = (
                select(
                    RevenueEvent.source,
                    func.coalesce(func.sum(RevenueEvent.amount), 0.0).label("amount"),
                )
                .group_by(RevenueEvent.source)
                .order_by(desc("amount"))
                .limit(5)
            )

            total = float((await session.execute(total_stmt)).scalar() or 0.0)
            daily = float((await session.execute(daily_stmt)).scalar() or 0.0)
            last_24h = float((await session.execute(last_24h_stmt)).scalar() or 0.0)
            last_7d = float((await session.execute(last_7d_stmt)).scalar() or 0.0)
            last_30d = float((await session.execute(last_30d_stmt)).scalar() or 0.0)
            mtd = float((await session.execute(mtd_stmt)).scalar() or 0.0)

            top_rows = (await session.execute(top_stmt)).all()
            top_sources = [
                {"source": row[0], "amount": float(row[1] or 0.0)} for row in top_rows
            ]

            return {
                "total": total,
                "daily": daily,
                "last_24h": last_24h,
                "last_7d": last_7d,
                "last_30d": last_30d,
                "mtd": mtd,
                "top_sources": top_sources,
            }
        except Exception:
            return None

    @staticmethod
    def _summarize_revenue_history(
        history: List[Dict[str, Any]]
    ) -> Tuple[float, float, float, float, List[Dict[str, Any]]]:
        now = datetime.now(timezone.utc)
        last_24h_cutoff = now - timedelta(hours=24)
        last_7d_cutoff = now - timedelta(days=7)
        last_30d_cutoff = now - timedelta(days=30)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        last_24h = 0.0
        last_7d = 0.0
        last_30d = 0.0
        mtd = 0.0
        source_totals: Dict[str, float] = defaultdict(float)

        for entry in history:
            timestamp_raw = entry.get("timestamp")
            amount = float(entry.get("amount", 0.0) or 0.0)
            if not timestamp_raw:
                continue
            parsed = OutcomeService._parse_timestamp(timestamp_raw)
            if parsed is None:
                continue
            if parsed >= last_24h_cutoff:
                last_24h += amount
            if parsed >= last_7d_cutoff:
                last_7d += amount
            if parsed >= last_30d_cutoff:
                last_30d += amount
            if parsed >= month_start:
                mtd += amount
            source = str(entry.get("source") or "Unknown")
            source_totals[source] += amount

        top_sources = [
            {"source": source, "amount": amount}
            for source, amount in sorted(
                source_totals.items(), key=lambda item: item[1], reverse=True
            )[:5]
        ]
        return last_24h, last_7d, last_30d, mtd, top_sources

    @staticmethod
    def _parse_timestamp(value: str) -> datetime | None:
        raw = value.replace("Z", "+00:00") if value.endswith("Z") else value
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    async def _pipeline_summary(session: AsyncSession) -> Dict[str, Any]:
        bizop_stmt = select(func.count(BizOpportunity.id))
        workflow_stmt = select(func.count(WorkflowCard.id)).where(
            WorkflowCard.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
        )

        bizop_result = await session.execute(bizop_stmt)
        workflow_result = await session.execute(workflow_stmt)

        return {
            "bizop_total": int(bizop_result.scalar() or 0),
            "workflow_velocity": int(workflow_result.scalar() or 0),
        }
