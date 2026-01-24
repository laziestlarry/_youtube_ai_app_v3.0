"""
Order Sync Service - Automated Shopier Order Synchronization

This service provides:
1. PAT-based order fetching from Shopier API
2. Automatic fulfillment for missed webhook callbacks
3. Revenue ledger synchronization
4. Delivery queue processing
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from backend.services.shopier_api_service import ShopierApiService
from backend.services.delivery_service import delivery_service, DeliveryResult
from modules.ai_agency.fulfillment_engine import fulfillment_engine

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("DATA_DIR", "."))
SYNC_STATE_FILE = DATA_DIR / "logs/order_sync_state.json"
PROCESSED_ORDERS_FILE = DATA_DIR / "logs/processed_orders.json"


@dataclass
class SyncResult:
    """Result of an order sync operation."""
    total_fetched: int = 0
    new_orders: int = 0
    fulfilled: int = 0
    already_processed: int = 0
    errors: int = 0
    revenue_recorded: float = 0.0
    sync_timestamp: str = ""
    details: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []


class OrderSyncService:
    """
    Automated order synchronization service for Shopier.
    
    Features:
    - Fetches orders via PAT API
    - Tracks processed orders to avoid duplicates
    - Triggers fulfillment for unprocessed orders
    - Updates revenue ledger
    - Supports scheduled execution via Cloud Scheduler
    """

    def __init__(self):
        self.shopier_api = ShopierApiService()
        self.base_url = os.getenv("BACKEND_ORIGIN", "")
        self._ensure_directories()
        self._processed_orders = self._load_processed_orders()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _load_processed_orders(self) -> set:
        """Load set of already processed order IDs."""
        if not PROCESSED_ORDERS_FILE.exists():
            return set()
        try:
            data = json.loads(PROCESSED_ORDERS_FILE.read_text(encoding="utf-8"))
            return set(data.get("order_ids", []))
        except Exception as e:
            logger.warning(f"Failed to load processed orders: {e}")
            return set()

    def _save_processed_orders(self):
        """Save processed order IDs."""
        try:
            data = {
                "order_ids": list(self._processed_orders),
                "last_updated": datetime.utcnow().isoformat()
            }
            PROCESSED_ORDERS_FILE.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to save processed orders: {e}")

    def _save_sync_state(self, result: SyncResult):
        """Save sync state for monitoring."""
        try:
            state = {
                "last_sync": result.sync_timestamp,
                "last_result": asdict(result),
                "total_processed_orders": len(self._processed_orders)
            }
            SYNC_STATE_FILE.write_text(
                json.dumps(state, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to save sync state: {e}")

    def _extract_order_data(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standardized order data from Shopier API response."""
        # Shopier API response structure may vary, handle common formats
        order_id = (
            order.get("id") or
            order.get("order_id") or
            order.get("platform_order_id") or
            str(order.get("orderNumber", ""))
        )
        
        # Extract amount
        amount = 0.0
        if "total" in order:
            amount = float(order["total"])
        elif "totalPrice" in order:
            amount = float(order["totalPrice"])
        elif "priceData" in order:
            amount = float(order["priceData"].get("total", 0))
        elif "amount" in order:
            amount = float(order["amount"])

        # Extract currency
        currency = (
            order.get("currency") or
            order.get("currencyCode") or
            (order.get("priceData", {}).get("currency")) or
            "TRY"
        )

        # Extract buyer email
        buyer_email = (
            order.get("buyerEmail") or
            order.get("buyer_email") or
            order.get("email") or
            (order.get("buyer", {}).get("email")) or
            (order.get("customer", {}).get("email"))
        )

        # Extract product/SKU info
        product_name = ""
        sku = ""
        items = order.get("items") or order.get("orderItems") or order.get("products") or []
        if items and len(items) > 0:
            first_item = items[0]
            product_name = first_item.get("title") or first_item.get("name") or first_item.get("productName", "")
            sku = first_item.get("sku") or first_item.get("productSku") or ""

        # Extract status
        status = (
            order.get("status") or
            order.get("orderStatus") or
            order.get("paymentStatus") or
            "unknown"
        )

        return {
            "order_id": str(order_id),
            "platform_order_id": str(order_id),
            "amount": amount,
            "total_order_value": amount,
            "currency": currency,
            "currency_code": currency,
            "buyer_email": buyer_email,
            "email": buyer_email,
            "product_name": product_name,
            "sku": sku,
            "status": status.lower() if isinstance(status, str) else "unknown",
            "created_at": order.get("createdAt") or order.get("created_at") or order.get("orderDate"),
            "raw_data": order
        }

    async def sync_orders(
        self,
        limit: int = 50,
        status_filter: Optional[str] = "paid",
        force_reprocess: bool = False
    ) -> SyncResult:
        """
        Sync orders from Shopier API and process any unfulfilled ones.
        
        Args:
            limit: Maximum orders to fetch
            status_filter: Filter by order status (paid, pending, etc.)
            force_reprocess: If True, reprocess already processed orders
            
        Returns:
            SyncResult with details of the sync operation
        """
        result = SyncResult(sync_timestamp=datetime.utcnow().isoformat())
        
        try:
            # Fetch orders from Shopier API
            logger.info(f"Fetching orders from Shopier (limit={limit}, status={status_filter})")
            orders = self.shopier_api.get_orders(status=status_filter, limit=limit)
            result.total_fetched = len(orders)
            logger.info(f"Fetched {len(orders)} orders from Shopier")

            for order in orders:
                order_data = self._extract_order_data(order)
                order_id = order_data["order_id"]
                
                if not order_id:
                    logger.warning("Order missing ID, skipping")
                    continue

                # Check if already processed
                if order_id in self._processed_orders and not force_reprocess:
                    result.already_processed += 1
                    continue

                result.new_orders += 1
                
                # Check if order is paid/completed
                if order_data["status"] not in ("paid", "completed", "success", "delivered"):
                    logger.info(f"Order {order_id} status is {order_data['status']}, skipping fulfillment")
                    result.details.append({
                        "order_id": order_id,
                        "status": "skipped",
                        "reason": f"Order status: {order_data['status']}"
                    })
                    continue

                # Process the order
                try:
                    delivery_result = await self._process_order(order_data)
                    
                    if delivery_result.status in ("delivered", "queued"):
                        result.fulfilled += 1
                        result.revenue_recorded += order_data.get("amount", 0)
                        
                        # Mark as processed
                        self._processed_orders.add(order_id)
                        
                        result.details.append({
                            "order_id": order_id,
                            "status": delivery_result.status,
                            "sku": delivery_result.sku,
                            "amount": delivery_result.amount,
                            "message": delivery_result.message
                        })
                    else:
                        result.details.append({
                            "order_id": order_id,
                            "status": delivery_result.status,
                            "message": delivery_result.message
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing order {order_id}: {e}")
                    result.errors += 1
                    result.details.append({
                        "order_id": order_id,
                        "status": "error",
                        "error": str(e)
                    })

            # Save state
            self._save_processed_orders()
            self._save_sync_state(result)
            
            logger.info(
                f"Sync complete: fetched={result.total_fetched}, "
                f"new={result.new_orders}, fulfilled={result.fulfilled}, "
                f"errors={result.errors}, revenue=${result.revenue_recorded:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Order sync failed: {e}")
            result.errors += 1
            result.details.append({"error": str(e)})

        return result

    async def _process_order(self, order_data: Dict[str, Any]) -> DeliveryResult:
        """Process a single order - fulfill and record revenue."""
        order_id = order_data["order_id"]
        amount = order_data.get("amount", 0)
        
        logger.info(f"Processing order {order_id} (amount: {amount})")
        
        # Trigger digital delivery
        delivery_result = delivery_service.deliver_digital(
            order_data,
            self.base_url,
            allow_queue=True
        )
        
        # Record revenue if delivery successful
        if delivery_result.status in ("delivered", "queued") and amount > 0:
            fulfillment_engine.record_sale(
                amount=amount,
                source=f"Shopier Order Sync: {order_id}",
                metadata={
                    "order_id": order_id,
                    "sku": delivery_result.sku,
                    "currency": order_data.get("currency", "TRY"),
                    "channel": "shopier",
                    "kind": "real",
                    "sync_source": "order_sync_service"
                }
            )
        
        return delivery_result

    async def retry_failed_deliveries(self, max_items: int = 50) -> Dict[str, int]:
        """Retry any queued/failed deliveries."""
        return delivery_service.retry_queued_deliveries(
            base_url=self.base_url,
            max_items=max_items
        )

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        if not SYNC_STATE_FILE.exists():
            return {
                "status": "never_synced",
                "total_processed": len(self._processed_orders)
            }
        
        try:
            state = json.loads(SYNC_STATE_FILE.read_text(encoding="utf-8"))
            state["status"] = "ok"
            return state
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "total_processed": len(self._processed_orders)
            }

    def clear_processed_orders(self, older_than_days: int = 30) -> int:
        """
        Clear old processed order IDs to prevent unbounded growth.
        
        Note: This is a simple implementation. A production system would
        store timestamps with order IDs for proper aging.
        """
        # For now, just keep the last N orders
        max_orders = 10000
        if len(self._processed_orders) > max_orders:
            # Convert to list, keep last max_orders
            orders_list = list(self._processed_orders)
            removed = len(orders_list) - max_orders
            self._processed_orders = set(orders_list[-max_orders:])
            self._save_processed_orders()
            return removed
        return 0


# Singleton instance
order_sync_service = OrderSyncService()


# Convenience function for scheduled execution
async def run_scheduled_sync() -> SyncResult:
    """
    Run order sync - designed for Cloud Scheduler invocation.
    """
    logger.info("Starting scheduled order sync...")
    result = await order_sync_service.sync_orders(limit=100)
    
    # Also retry any failed deliveries
    retry_result = await order_sync_service.retry_failed_deliveries()
    
    logger.info(f"Scheduled sync complete. Orders: {result.fulfilled}, Retries: {retry_result}")
    return result
