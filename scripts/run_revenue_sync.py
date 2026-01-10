import argparse
import asyncio
import json

from backend.core import database as db
from backend.services.revenue_sync_service import RevenueSyncService


async def run(days: int) -> None:
    if db.AsyncSessionLocal is None or db.async_engine is None:
        db.create_database_engines()
    async with db.AsyncSessionLocal() as session:
        payload = await RevenueSyncService().sync(session, lookback_days=days)
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync revenue events from core DB tables.")
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days.")
    args = parser.parse_args()
    asyncio.run(run(args.days))


if __name__ == "__main__":
    main()
