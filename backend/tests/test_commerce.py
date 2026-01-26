import os
from urllib.parse import urlparse, parse_qs

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.core.database import Base
from backend.services.commerce_service import commerce_service
import backend.models.commerce  # noqa: F401
import backend.models.user  # noqa: F401

def test_catalog_returns_products():
    products = commerce_service.list_products()
    assert isinstance(products, list)
    assert products, "Expected at least one product in catalog"


def test_checkout_resolution_for_known_sku():
    checkout = commerce_service.resolve_checkout("ZEN-ART-BASE")
    assert checkout is not None
    assert checkout.sku == "ZEN-ART-BASE"
    assert checkout.price > 0
    assert checkout.currency


def test_loyalty_tier_thresholds():
    assert commerce_service.calculate_tier(0) == "bronze"
    assert commerce_service.calculate_tier(500) == "silver"
    assert commerce_service.calculate_tier(2000) == "gold"
    assert commerce_service.calculate_tier(10000) == "platinum"


@pytest.mark.asyncio
async def test_offer_checkout_and_delivery_link():
    os.environ["DELIVERY_LINK_TTL_HOURS"] = "1"
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as db:
        asset = await commerce_service.create_asset(
            db,
            name="zen_pack.pdf",
            file_path="/tmp/zen_pack.pdf",
            content_type="application/pdf",
            size_bytes=1234,
            checksum="abc123",
        )
        offer = await commerce_service.create_offer(
            db,
            title="Zen Art Pack",
            description="Minimalist wall art.",
            price=24.0,
            currency="USD",
            asset_id=asset.id,
            offer_type="printable",
            status="active",
            metadata={"file_format": "PDF"},
            created_by=None,
        )
        order = await commerce_service.create_order(
            db,
            offer=offer,
            customer_email="buyer@example.com",
            customer_name="Buyer",
        )
        delivery = await commerce_service.create_delivery(db, order, asset, "http://localhost:8000")

        assert delivery.token
        assert delivery.download_url
        parsed = urlparse(delivery.download_url)
        assert parsed.path.endswith(f"/api/commerce/download/{delivery.id}")
        token = parse_qs(parsed.query).get("token", [None])[0]
        assert token == delivery.token
