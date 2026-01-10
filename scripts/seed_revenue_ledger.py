import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select

from backend.core import database as db
from backend.models.revenue import RevenueEvent


def parse_timestamp(value: str) -> datetime | None:
    raw = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_key(source: str, amount: float, occurred_at: datetime) -> str:
    return f"{source}|{amount:.4f}|{occurred_at.isoformat()}"


async def seed_events(history: list[dict]) -> int:
    if db.AsyncSessionLocal is None or db.async_engine is None:
        db.create_database_engines()
    async with db.async_engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)

    async with db.AsyncSessionLocal() as session:
        result = await session.execute(
            select(RevenueEvent.source, RevenueEvent.amount, RevenueEvent.occurred_at)
        )
        existing_rows = result.all()
        existing = {
            build_key(row[0], float(row[1]), row[2])
            for row in existing_rows
            if row[2] is not None
        }

        inserted = 0
        for entry in history:
            timestamp = entry.get("timestamp")
            source = str(entry.get("source") or "Unknown")
            amount = float(entry.get("amount", 0.0) or 0.0)
            if not timestamp or amount <= 0:
                continue
            occurred_at = parse_timestamp(timestamp)
            if occurred_at is None:
                continue

            key = build_key(source, amount, occurred_at)
            if key in existing:
                continue

            metadata = {
                k: v
                for k, v in entry.items()
                if k not in {"timestamp", "amount", "source", "asset_url"}
            }
            kind = str(metadata.get("kind", "seed"))

            session.add(
                RevenueEvent(
                    id=str(uuid4()),
                    amount=amount,
                    currency="USD",
                    source=source,
                    kind=kind,
                    asset_url=entry.get("asset_url"),
                    metadata_json=metadata or None,
                    occurred_at=occurred_at,
                )
            )
            existing.add(key)
            inserted += 1

        await session.commit()
        return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed revenue_events from earnings.json.")
    parser.add_argument("--ledger", default="earnings.json", help="Path to earnings.json")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    if not ledger_path.exists():
        raise SystemExit(f"Ledger not found: {ledger_path}")

    with ledger_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    history = payload.get("history", [])
    if not history:
        print("No ledger history found. Nothing to seed.")
        return

    inserted = asyncio.run(seed_events(history))
    print(f"Seeded {inserted} revenue events.")


if __name__ == "__main__":
    main()
