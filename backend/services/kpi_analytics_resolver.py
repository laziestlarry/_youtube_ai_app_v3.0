from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.subscription import UserSubscription, AffiliateClick, AffiliateConversion
from backend.models.workflow import WorkflowCard


class KPIAnalyticsResolver:
    async def resolve(self, session: AsyncSession, kpi: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
        metric = str(kpi.get("metric") or "").strip()
        if not metric:
            return None, None

        if metric == "subscription_mrr":
            stmt = select(func.coalesce(func.sum(UserSubscription.total_revenue_this_month), 0)).where(
                UserSubscription.status == "active"
            )
            result = await session.execute(stmt)
            return float(result.scalar() or 0), "Live subscription MRR"

        if metric == "subscription_arpu":
            stmt = select(
                func.count(UserSubscription.id).label("count"),
                func.coalesce(func.sum(UserSubscription.total_revenue_this_month), 0).label("total"),
            ).where(UserSubscription.status == "active")
            result = await session.execute(stmt)
            row = result.first()
            if not row or not row.count:
                return None, None
            return float(row.total) / float(row.count), "Live ARPU from active subscriptions"

        if metric == "subscription_retention_rate":
            total_stmt = select(func.count(UserSubscription.id))
            active_stmt = select(func.count(UserSubscription.id)).where(UserSubscription.status == "active")
            total_result = await session.execute(total_stmt)
            active_result = await session.execute(active_stmt)
            total = total_result.scalar() or 0
            active = active_result.scalar() or 0
            if total == 0:
                return None, None
            return float(active) / float(total), "Active subscriptions / total subscriptions"

        if metric == "affiliate_conversion_rate":
            clicks_stmt = select(func.count(AffiliateClick.id))
            conversions_stmt = select(func.count(AffiliateConversion.id))
            clicks_result = await session.execute(clicks_stmt)
            conversions_result = await session.execute(conversions_stmt)
            clicks = clicks_result.scalar() or 0
            conversions = conversions_result.scalar() or 0
            if clicks == 0:
                return None, None
            return float(conversions) / float(clicks), "Affiliate conversions / clicks"

        if metric == "workflow_velocity":
            cutoff = datetime.utcnow() - timedelta(days=7)
            stmt = select(func.count(WorkflowCard.id)).where(WorkflowCard.created_at >= cutoff)
            result = await session.execute(stmt)
            return float(result.scalar() or 0), "Workflow cards created in last 7 days"

        return None, None
