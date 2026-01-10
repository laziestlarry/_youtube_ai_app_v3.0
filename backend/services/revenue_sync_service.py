from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.revenue import RevenueEvent
from backend.models.subscription import (
    AffiliateConversion,
    PaymentTransaction,
    VideoRevenue,
)


class RevenueSyncService:
    def __init__(self) -> None:
        self._now = datetime.now(timezone.utc)

    async def sync(self, session: AsyncSession, lookback_days: int = 30) -> Dict[str, Any]:
        start = self._now - timedelta(days=max(1, lookback_days))

        candidates: List[RevenueEvent] = []
        sources: List[str] = []
        counts: Dict[str, int] = {
            "payment_transactions": 0,
            "video_revenue": 0,
            "affiliate_conversions": 0,
        }

        payment_rows = await session.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.status == "succeeded",
                PaymentTransaction.created_at >= start,
            )
        )
        for row in payment_rows.scalars().all():
            if not row.id:
                continue
            if not row.amount or row.amount <= 0:
                continue
            source = f"payment_transaction:{row.id}"
            sources.append(source)
            candidates.append(
                self._build_event(
                    amount=row.amount,
                    currency=row.currency or "USD",
                    source=source,
                    kind="payment",
                    occurred_at=row.created_at,
                    metadata={
                        "type": row.type,
                        "stripe_payment_intent_id": row.stripe_payment_intent_id,
                    },
                )
            )
            counts["payment_transactions"] += 1

        video_rows = await session.execute(
            select(VideoRevenue).where(VideoRevenue.date >= start)
        )
        for row in video_rows.scalars().all():
            if not row.id:
                continue
            if not row.amount or row.amount <= 0:
                continue
            source = f"video_revenue:{row.id}"
            sources.append(source)
            candidates.append(
                self._build_event(
                    amount=row.amount,
                    currency=row.currency or "USD",
                    source=source,
                    kind="video",
                    occurred_at=row.date,
                    metadata={
                        "video_id": row.video_id,
                        "user_id": row.user_id,
                        "source_type": row.source,
                    },
                )
            )
            counts["video_revenue"] += 1

        affiliate_rows = await session.execute(
            select(AffiliateConversion).where(AffiliateConversion.timestamp >= start)
        )
        for row in affiliate_rows.scalars().all():
            if not row.id:
                continue
            if not row.commission_amount or row.commission_amount <= 0:
                continue
            source = f"affiliate_conversion:{row.id}"
            sources.append(source)
            candidates.append(
                self._build_event(
                    amount=row.commission_amount,
                    currency="USD",
                    source=source,
                    kind="affiliate",
                    occurred_at=row.timestamp,
                    metadata={
                        "affiliate_id": row.affiliate_id,
                        "product_id": row.product_id,
                        "sale_amount": row.sale_amount,
                    },
                )
            )
            counts["affiliate_conversions"] += 1

        if not sources:
            return {
                "inserted": 0,
                "skipped": 0,
                "lookback_days": lookback_days,
                "sources": counts,
            }

        existing_sources = await self._fetch_existing_sources(session, sources)
        inserted = 0
        for event in candidates:
            if event.source in existing_sources:
                continue
            session.add(event)
            existing_sources.add(event.source)
            inserted += 1

        await session.commit()

        return {
            "inserted": inserted,
            "skipped": len(candidates) - inserted,
            "lookback_days": lookback_days,
            "sources": counts,
        }

    async def _fetch_existing_sources(
        self,
        session: AsyncSession,
        sources: Iterable[str],
    ) -> set[str]:
        result = await session.execute(
            select(RevenueEvent.source).where(RevenueEvent.source.in_(list(sources)))
        )
        return {row[0] for row in result.all()}

    @staticmethod
    def _build_event(
        amount: float,
        currency: str,
        source: str,
        kind: str,
        occurred_at: datetime | None,
        metadata: Dict[str, Any],
    ) -> RevenueEvent:
        timestamp = RevenueSyncService._normalize_timestamp(occurred_at)
        return RevenueEvent(
            id=str(uuid4()),
            amount=float(amount or 0.0),
            currency=currency,
            source=source,
            kind=kind,
            asset_url=None,
            metadata_json=metadata,
            occurred_at=timestamp,
        )

    @staticmethod
    def _normalize_timestamp(value: datetime | None) -> datetime:
        if value is None:
            return datetime.now(timezone.utc)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
