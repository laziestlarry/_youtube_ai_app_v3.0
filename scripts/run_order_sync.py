#!/usr/bin/env python3
"""
Order Sync Script - Automated Shopier Order Synchronization

This script:
1. Fetches paid orders from Shopier API
2. Processes unfulfilled orders
3. Triggers digital delivery
4. Records revenue

Usage:
    python scripts/run_order_sync.py --limit 100
    python scripts/run_order_sync.py --force-reprocess
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ROOT / "logs" / "order_sync.log", mode="a")
    ]
)
logger = logging.getLogger("order_sync")


async def main(args):
    """Main sync execution."""
    logger.info("=" * 60)
    logger.info("ORDER SYNC STARTED")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
    logger.info(f"Limit: {args.limit}, Force Reprocess: {args.force_reprocess}")
    logger.info("=" * 60)

    try:
        from backend.services.order_sync_service import order_sync_service

        # Run order sync
        result = await order_sync_service.sync_orders(
            limit=args.limit,
            status_filter=args.status,
            force_reprocess=args.force_reprocess
        )

        # Log results
        logger.info("-" * 40)
        logger.info("SYNC RESULTS:")
        logger.info(f"  Total Fetched: {result.total_fetched}")
        logger.info(f"  New Orders: {result.new_orders}")
        logger.info(f"  Fulfilled: {result.fulfilled}")
        logger.info(f"  Already Processed: {result.already_processed}")
        logger.info(f"  Errors: {result.errors}")
        logger.info(f"  Revenue Recorded: ${result.revenue_recorded:.2f}")
        logger.info("-" * 40)

        # Run delivery retry if requested
        if args.retry_deliveries:
            logger.info("Retrying failed deliveries...")
            retry_result = await order_sync_service.retry_failed_deliveries(max_items=50)
            logger.info(f"Retry result: {retry_result}")

        # Output JSON for programmatic consumption
        if args.json_output:
            print(json.dumps({
                "status": "success",
                "timestamp": result.sync_timestamp,
                "total_fetched": result.total_fetched,
                "new_orders": result.new_orders,
                "fulfilled": result.fulfilled,
                "already_processed": result.already_processed,
                "errors": result.errors,
                "revenue_recorded": result.revenue_recorded,
                "details": result.details if args.verbose else []
            }, indent=2))

        logger.info("=" * 60)
        logger.info("ORDER SYNC COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

        return 0 if result.errors == 0 else 1

    except Exception as e:
        logger.error(f"Order sync failed: {e}", exc_info=True)
        if args.json_output:
            print(json.dumps({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2))
        return 1


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Shopier Order Sync Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Standard sync (fetch last 100 paid orders)
    python scripts/run_order_sync.py

    # Sync with higher limit
    python scripts/run_order_sync.py --limit 500

    # Force reprocess all orders
    python scripts/run_order_sync.py --force-reprocess

    # Include delivery retry
    python scripts/run_order_sync.py --retry-deliveries

    # JSON output for automation
    python scripts/run_order_sync.py --json-output
        """
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of orders to fetch (default: 100)"
    )

    parser.add_argument(
        "--status",
        type=str,
        default="paid",
        choices=["paid", "pending", "shipped", "completed", "all"],
        help="Order status filter (default: paid)"
    )

    parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Reprocess already processed orders"
    )

    parser.add_argument(
        "--retry-deliveries",
        action="store_true",
        help="Also retry any failed deliveries"
    )

    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Include detailed results in output"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    # Ensure logs directory exists
    (ROOT / "logs").mkdir(parents=True, exist_ok=True)
    
    exit_code = asyncio.run(main(args))
    sys.exit(exit_code)
