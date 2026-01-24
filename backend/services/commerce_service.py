import json
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.commerce import (
    CommerceAsset,
    CommerceDelivery,
    CommerceOffer,
    CommerceOrder,
    CustomerContract,
    CustomerJourneyEvent,
    LoyaltyAccount,
    LoyaltyLedger,
)


CATALOG_FILE = Path("docs/commerce/product_catalog.json")
PRICE_OVERRIDE_FILE = Path("docs/commerce/shopier_price_overrides.json")
SHOPIER_MAP_FILE = Path("docs/commerce/shopier_product_map.json")


@dataclass
class CheckoutInfo:
    sku: str
    title: str
    price: float
    currency: str
    order_id: str


class CommerceService:
    def __init__(self) -> None:
        self._catalog_cache: Optional[dict] = None
        self._price_override_cache: Optional[dict] = None
        self._shopier_map_cache: Optional[dict] = None

    def _load_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _catalog(self) -> dict:
        if self._catalog_cache is None:
            self._catalog_cache = self._load_json(CATALOG_FILE)
        return self._catalog_cache or {}

    def _price_overrides(self) -> dict:
        if self._price_override_cache is None:
            self._price_override_cache = self._load_json(PRICE_OVERRIDE_FILE)
        return self._price_override_cache or {}

    def _shopier_map(self) -> dict:
        if self._shopier_map_cache is None:
            self._shopier_map_cache = self._load_json(SHOPIER_MAP_FILE)
        return self._shopier_map_cache or {}

    def list_products(self) -> list[dict]:
        catalog = self._catalog()
        products = []
        shopier_map = self._shopier_map()
        overrides = self._price_overrides()
        for product in catalog.get("products", []):
            sku = str(product.get("sku") or "").strip()
            override = overrides.get(sku, {})
            shopier_entry = shopier_map.get(sku, {})
            price_block = product.get("price") or {}
            products.append(
                {
                    **product,
                    "checkout_price": override.get("price", price_block.get("min")),
                    "checkout_currency": override.get("currency", price_block.get("currency", "USD")),
                    "shopier_url": shopier_entry.get("url"),
                }
            )
        return products

    def resolve_checkout(self, sku: str, order_id: Optional[str] = None) -> Optional[CheckoutInfo]:
        catalog = self._catalog()
        product = next((item for item in catalog.get("products", []) if item.get("sku") == sku), None)
        if not product:
            return None

        price_block = product.get("price") or {}
        overrides = self._price_overrides().get(sku, {})
        price = overrides.get("price", price_block.get("min"))
        currency = overrides.get("currency", price_block.get("currency", "USD"))
        if price is None:
            return None

        resolved_order_id = order_id or f"{sku}-{uuid.uuid4().hex[:10]}"
        return CheckoutInfo(
            sku=sku,
            title=str(product.get("title") or sku),
            price=float(price),
            currency=str(currency),
            order_id=resolved_order_id,
        )

    async def create_asset(
        self,
        db: AsyncSession,
        name: str,
        file_path: str,
        content_type: Optional[str],
        size_bytes: Optional[int],
        checksum: Optional[str],
    ) -> CommerceAsset:
        asset = CommerceAsset(
            name=name,
            file_path=file_path,
            content_type=content_type,
            size_bytes=size_bytes,
            checksum=checksum,
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset

    async def create_offer(
        self,
        db: AsyncSession,
        title: str,
        description: Optional[str],
        price: float,
        currency: str,
        asset_id: Optional[int],
        offer_type: str,
        status: str,
        metadata: Optional[Dict[str, Any]],
        created_by: Optional[int],
        sku: Optional[str] = None,
    ) -> CommerceOffer:
        sku_value = sku or f"ZEN-{uuid.uuid4().hex[:8].upper()}"
        offer = CommerceOffer(
            sku=sku_value,
            title=title,
            description=description,
            price=price,
            currency=currency,
            asset_id=asset_id,
            offer_type=offer_type,
            status=status,
            metadata_json=metadata,
            created_by=created_by,
        )
        db.add(offer)
        await db.commit()
        await db.refresh(offer)
        return offer

    async def list_offers(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        offer_type: Optional[str] = None,
        limit: int = 200,
    ) -> list[CommerceOffer]:
        query = select(CommerceOffer).order_by(CommerceOffer.created_at.desc())
        if status:
            query = query.where(CommerceOffer.status == status)
        if offer_type:
            query = query.where(CommerceOffer.offer_type == offer_type)
        result = await db.execute(query.limit(limit))
        return list(result.scalars().all())

    async def get_offer(self, db: AsyncSession, offer_id: int) -> Optional[CommerceOffer]:
        result = await db.execute(select(CommerceOffer).where(CommerceOffer.id == offer_id))
        return result.scalars().first()

    async def create_order(
        self,
        db: AsyncSession,
        offer: CommerceOffer,
        customer_email: Optional[str],
        customer_name: Optional[str],
        order_id: Optional[str] = None,
    ) -> CommerceOrder:
        resolved_order_id = order_id or f"{offer.sku}-{uuid.uuid4().hex[:10]}"
        order = CommerceOrder(
            order_id=resolved_order_id,
            offer_id=offer.id,
            customer_email=customer_email,
            customer_name=customer_name,
            status="initiated",
            amount=offer.price,
            currency=offer.currency,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    async def get_order_by_order_id(self, db: AsyncSession, order_id: str) -> Optional[CommerceOrder]:
        result = await db.execute(select(CommerceOrder).where(CommerceOrder.order_id == order_id))
        return result.scalars().first()

    async def mark_order_paid(
        self,
        db: AsyncSession,
        order: CommerceOrder,
        amount: Optional[float],
        currency: Optional[str],
    ) -> CommerceOrder:
        if amount is not None:
            order.amount = amount
        if currency:
            order.currency = currency
        order.status = "paid"
        order.paid_at = datetime.utcnow()
        await db.commit()
        await db.refresh(order)
        return order

    async def get_asset(self, db: AsyncSession, asset_id: int) -> Optional[CommerceAsset]:
        result = await db.execute(select(CommerceAsset).where(CommerceAsset.id == asset_id))
        return result.scalars().first()

    def _delivery_ttl_hours(self) -> int:
        value = os.getenv("DELIVERY_LINK_TTL_HOURS") or "72"
        try:
            ttl = int(value)
        except ValueError:
            ttl = 72
        return max(ttl, 1)

    def delivery_ttl_hours(self) -> int:
        return self._delivery_ttl_hours()

    def _build_download_url(self, base_url: str, delivery_id: int, token: str) -> str:
        base = base_url.rstrip("/")
        return f"{base}/api/commerce/download/{delivery_id}?token={token}"

    async def create_delivery(
        self,
        db: AsyncSession,
        order: CommerceOrder,
        asset: Optional[CommerceAsset],
        base_url: str,
        method: str = "signed_link",
    ) -> CommerceDelivery:
        token = secrets.token_urlsafe(24)
        expires_at = datetime.utcnow() + timedelta(hours=self._delivery_ttl_hours())
        delivery = CommerceDelivery(
            order_id=order.id,
            asset_id=asset.id if asset else None,
            method=method,
            status="ready",
            token=token,
            expires_at=expires_at,
        )
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        delivery.download_url = self._build_download_url(base_url, delivery.id, token)
        await db.commit()
        await db.refresh(delivery)
        return delivery

    async def get_delivery(self, db: AsyncSession, delivery_id: int) -> Optional[CommerceDelivery]:
        result = await db.execute(select(CommerceDelivery).where(CommerceDelivery.id == delivery_id))
        return result.scalars().first()

    async def get_delivery_for_order(self, db: AsyncSession, order_id: int) -> Optional[CommerceDelivery]:
        result = await db.execute(
            select(CommerceDelivery)
            .where(CommerceDelivery.order_id == order_id)
            .order_by(CommerceDelivery.created_at.desc())
        )
        return result.scalars().first()

    @staticmethod
    def calculate_tier(points: int) -> str:
        if points >= 10000:
            return "platinum"
        if points >= 2000:
            return "gold"
        if points >= 500:
            return "silver"
        return "bronze"

    async def record_journey_event(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        stage: str,
        channel: Optional[str] = None,
        sku: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CustomerJourneyEvent:
        event = CustomerJourneyEvent(
            user_id=user_id,
            stage=stage,
            channel=channel,
            sku=sku,
            metadata_json=metadata,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    async def get_or_create_loyalty_account(self, db: AsyncSession, user_id: int) -> LoyaltyAccount:
        result = await db.execute(select(LoyaltyAccount).where(LoyaltyAccount.user_id == user_id))
        account = result.scalars().first()
        if account:
            return account
        account = LoyaltyAccount(user_id=user_id, points_balance=0, tier="bronze")
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    async def award_loyalty_points(
        self,
        db: AsyncSession,
        user_id: int,
        points: int,
        reason: str,
        reference: Optional[str] = None,
    ) -> LoyaltyAccount:
        account = await self.get_or_create_loyalty_account(db, user_id)
        account.points_balance = int(account.points_balance or 0) + int(points)
        account.tier = self.calculate_tier(account.points_balance)
        ledger = LoyaltyLedger(
            account_id=account.id,
            delta=points,
            reason=reason,
            reference=reference,
        )
        db.add(ledger)
        await db.commit()
        await db.refresh(account)
        return account

    async def list_loyalty_ledger(self, db: AsyncSession, account_id: int, limit: int = 50) -> list[LoyaltyLedger]:
        result = await db.execute(
            select(LoyaltyLedger)
            .where(LoyaltyLedger.account_id == account_id)
            .order_by(LoyaltyLedger.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_contract(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        org_name: str,
        status: str,
        value: float,
        currency: str,
        start_date: Optional[Any],
        end_date: Optional[Any],
        terms: Optional[str],
    ) -> CustomerContract:
        contract = CustomerContract(
            user_id=user_id,
            org_name=org_name,
            status=status,
            value=value,
            currency=currency,
            start_date=start_date,
            end_date=end_date,
            terms=terms,
        )
        db.add(contract)
        await db.commit()
        await db.refresh(contract)
        return contract

    async def count_journey_events(self, db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(func.count(CustomerJourneyEvent.id)).where(CustomerJourneyEvent.user_id == user_id)
        )
        return int(result.scalar() or 0)

    async def count_active_contracts(self, db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(func.count(CustomerContract.id)).where(
                CustomerContract.user_id == user_id,
                CustomerContract.status.in_(["active", "in_progress", "signed"]),
            )
        )
        return int(result.scalar() or 0)


commerce_service = CommerceService()
