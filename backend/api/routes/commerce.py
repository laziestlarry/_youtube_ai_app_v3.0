import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_optional_current_user
from backend.core.database import get_async_db
from backend.models import (
    CommerceJourneyEventCreate,
    CommerceJourneyEventResponse,
    CommerceSummaryResponse,
    CommerceAssetResponse,
    ContractCreate,
    ContractResponse,
    DeliveryResendRequest,
    DeliveryResponse,
    LoyaltyAccountResponse,
    LoyaltyAwardRequest,
    LoyaltyLedgerResponse,
    OfferCreate,
    OfferResponse,
    OrderResponse,
)
from backend.models.commerce import CustomerContract, CustomerJourneyEvent
from backend.models.user import User
from backend.services.commerce_service import commerce_service
from backend.services.delivery_service import delivery_service


router = APIRouter()

DATA_DIR = Path(os.getenv("DATA_DIR", "."))
ASSET_DIR = DATA_DIR / "commerce/assets"
ALLOWED_PRINTABLE_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}
MAX_ASSET_BYTES = int(os.getenv("PRINTABLE_MAX_BYTES", "25000000"))

class CheckoutRequest(BaseModel):
    sku: Optional[str] = Field(None, min_length=2, max_length=64)
    offer_id: Optional[int] = None
    order_id: Optional[str] = Field(None, max_length=120)
    customer_email: Optional[str] = Field(None, max_length=200)
    customer_name: Optional[str] = Field(None, max_length=200)


@router.get("/catalog")
def list_catalog():
    """Return catalog data enriched with checkout metadata."""
    products = commerce_service.list_products()
    return {
        "count": len(products),
        "products": products,
    }


@router.post("/assets/upload", response_model=CommerceAssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    if file.content_type not in ALLOWED_PRINTABLE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()
    if len(contents) > MAX_ASSET_BYTES:
        raise HTTPException(status_code=413, detail="Asset too large")

    checksum = hashlib.sha256(contents).hexdigest()
    safe_name = Path(file.filename or "asset").name
    ext = Path(safe_name).suffix.lower()
    if not ext:
        ext = ".pdf" if file.content_type == "application/pdf" else ".png"

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    storage_name = f"{uuid.uuid4().hex}{ext}"
    storage_path = ASSET_DIR / storage_name
    storage_path.write_bytes(contents)

    asset = await commerce_service.create_asset(
        db,
        name=safe_name,
        file_path=str(storage_path),
        content_type=file.content_type,
        size_bytes=len(contents),
        checksum=checksum,
    )
    return CommerceAssetResponse.model_validate(asset)


@router.post("/offers", response_model=OfferResponse)
async def create_offer(
    payload: OfferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    metadata = {
        "file_format": payload.file_format,
        "dimensions": payload.dimensions,
        "dpi": payload.dpi,
        "license_terms": payload.license_terms,
        "tags": payload.tags,
    }
    if all(value is None for value in metadata.values()):
        metadata = None

    offer = await commerce_service.create_offer(
        db,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        currency=payload.currency,
        asset_id=payload.asset_id,
        offer_type=payload.offer_type,
        status=payload.status,
        metadata=metadata,
        created_by=current_user.id,
        sku=payload.sku,
    )
    return OfferResponse(
        id=offer.id,
        sku=offer.sku,
        title=offer.title,
        description=offer.description,
        price=offer.price,
        currency=offer.currency,
        status=offer.status,
        offer_type=offer.offer_type,
        asset_id=offer.asset_id,
        metadata=offer.metadata_json,
        created_at=offer.created_at,
        updated_at=offer.updated_at,
    )


@router.get("/offers", response_model=list[OfferResponse])
async def list_offers(
    status: str = "active",
    offer_type: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    offers = await commerce_service.list_offers(db, status=status, offer_type=offer_type, limit=limit)
    return [
        OfferResponse(
            id=offer.id,
            sku=offer.sku,
            title=offer.title,
            description=offer.description,
            price=offer.price,
            currency=offer.currency,
            status=offer.status,
            offer_type=offer.offer_type,
            asset_id=offer.asset_id,
            metadata=offer.metadata_json,
            created_at=offer.created_at,
            updated_at=offer.updated_at,
        )
        for offer in offers
    ]


@router.post("/checkout")
async def create_checkout(
    request: Request,
    payload: CheckoutRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Create a checkout URL for a SKU or offer and record a journey event if possible."""
    base_url = str(request.base_url).rstrip("/")

    if payload.offer_id:
        offer = await commerce_service.get_offer(db, payload.offer_id)
        if not offer or offer.status != "active":
            raise HTTPException(status_code=404, detail="Offer not found")
        order = await commerce_service.create_order(
            db,
            offer=offer,
            customer_email=payload.customer_email,
            customer_name=payload.customer_name,
            order_id=payload.order_id,
        )
        params = urlencode(
            {
                "amount": offer.price,
                "currency": offer.currency,
                "order_id": order.order_id,
                "product_name": offer.title,
            }
        )
        checkout_url = f"{base_url}/api/payment/shopier/pay?{params}"
        sku = offer.sku
        order_id = order.order_id
        price = offer.price
        currency = offer.currency
    else:
        if not payload.sku:
            raise HTTPException(status_code=400, detail="SKU or offer_id required")
        sku = payload.sku.strip()
        order_id = payload.order_id
        checkout = commerce_service.resolve_checkout(sku, order_id=order_id)
        if not checkout:
            raise HTTPException(status_code=404, detail=f"SKU {sku} not found")

        params = urlencode(
            {
                "amount": checkout.price,
                "currency": checkout.currency,
                "order_id": checkout.order_id,
                "product_name": checkout.title,
            }
        )
        checkout_url = f"{base_url}/api/payment/shopier/pay?{params}"
        order_id = checkout.order_id
        price = checkout.price
        currency = checkout.currency

    if current_user:
        try:
            await commerce_service.record_journey_event(
                db,
                user_id=current_user.id,
                stage="checkout_initiated",
                channel="shopier",
                sku=sku,
                metadata={"order_id": order_id, "price": price},
            )
        except Exception:
            pass

    return {
        "checkout_url": checkout_url,
        "order_id": order_id,
        "sku": sku,
        "price": price,
        "currency": currency,
    }


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_status(
    order_id: str,
    token: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    order = await commerce_service.get_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    delivery = await commerce_service.get_delivery_for_order(db, order.id)
    if not current_user:
        if not delivery or not token or delivery.token != token:
            raise HTTPException(status_code=403, detail="Order access denied")

    delivery_payload = None
    if delivery:
        delivery_payload = DeliveryResponse(
            id=delivery.id,
            status=delivery.status,
            method=delivery.method,
            download_url=delivery.download_url,
            expires_at=delivery.expires_at,
            delivered_at=delivery.delivered_at,
        )

    return OrderResponse(
        order_id=order.order_id,
        status=order.status,
        amount=order.amount,
        currency=order.currency,
        paid_at=order.paid_at,
        delivery=delivery_payload,
    )


@router.get("/download/{delivery_id}")
async def download_asset(
    delivery_id: int,
    token: str,
    db: AsyncSession = Depends(get_async_db),
):
    delivery = await commerce_service.get_delivery(db, delivery_id)
    if not delivery or delivery.token != token:
        raise HTTPException(status_code=403, detail="Invalid download token")

    expires_at = delivery.expires_at
    if expires_at and expires_at.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=None)
    if expires_at and expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Download link expired")

    if not delivery.asset_id:
        raise HTTPException(status_code=404, detail="Delivery asset missing")

    asset = await commerce_service.get_asset(db, delivery.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset_path = Path(asset.file_path)
    if not asset_path.exists():
        raise HTTPException(status_code=404, detail="Asset file missing")

    if delivery.status != "delivered":
        delivery.status = "delivered"
        delivery.delivered_at = datetime.utcnow()
        await db.commit()

    return FileResponse(
        path=str(asset_path),
        media_type=asset.content_type or "application/octet-stream",
        filename=asset_path.name,
    )


@router.post("/deliver", response_model=OrderResponse)
async def resend_delivery(
    payload: DeliveryResendRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    order = await commerce_service.get_order_by_order_id(db, payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    offer = None
    asset = None
    if order.offer_id:
        offer = await commerce_service.get_offer(db, order.offer_id)
        if offer and offer.asset_id:
            asset = await commerce_service.get_asset(db, offer.asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Delivery asset missing")

    base_url = str(request.base_url).rstrip("/")
    delivery = await commerce_service.create_delivery(db, order, asset, base_url)

    if order.customer_email:
        title = offer.title if offer else "Download Ready"
        subject, body = delivery_service.build_zen_art_delivery_message(
            title=title,
            download_url=delivery.download_url,
            ttl_hours=commerce_service.delivery_ttl_hours(),
            order_id=order.order_id,
        )
        delivery_service.send_email(order.customer_email, subject, body)
        delivery.status = "sent"
        delivery.delivered_at = datetime.utcnow()
        order.status = "delivered"
        await db.commit()

    delivery_payload = DeliveryResponse(
        id=delivery.id,
        status=delivery.status,
        method=delivery.method,
        download_url=delivery.download_url,
        expires_at=delivery.expires_at,
        delivered_at=delivery.delivered_at,
    )

    return OrderResponse(
        order_id=order.order_id,
        status=order.status,
        amount=order.amount,
        currency=order.currency,
        paid_at=order.paid_at,
        delivery=delivery_payload,
    )


@router.get("/summary", response_model=CommerceSummaryResponse)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Aggregate commerce metrics for the current user."""
    journey_events = await commerce_service.count_journey_events(db, current_user.id)
    active_contracts = await commerce_service.count_active_contracts(db, current_user.id)
    account = await commerce_service.get_or_create_loyalty_account(db, current_user.id)

    return CommerceSummaryResponse(
        journey_events=journey_events,
        loyalty_points=account.points_balance,
        loyalty_tier=account.tier,
        active_contracts=active_contracts,
    )


@router.post("/journeys", response_model=CommerceJourneyEventResponse)
async def create_journey_event(
    payload: CommerceJourneyEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    event = await commerce_service.record_journey_event(
        db,
        user_id=current_user.id,
        stage=payload.stage,
        channel=payload.channel,
        sku=payload.sku,
        metadata=payload.metadata,
    )
    return CommerceJourneyEventResponse(
        id=event.id,
        user_id=event.user_id,
        stage=event.stage,
        channel=event.channel,
        sku=event.sku,
        metadata=event.metadata_json,
        created_at=event.created_at,
    )


@router.get("/journeys", response_model=list[CommerceJourneyEventResponse])
async def list_journey_events(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(CustomerJourneyEvent)
        .where(CustomerJourneyEvent.user_id == current_user.id)
        .order_by(desc(CustomerJourneyEvent.created_at))
        .limit(limit)
    )
    events = result.scalars().all()
    return [
        CommerceJourneyEventResponse(
            id=event.id,
            user_id=event.user_id,
            stage=event.stage,
            channel=event.channel,
            sku=event.sku,
            metadata=event.metadata_json,
            created_at=event.created_at,
        )
        for event in events
    ]


@router.get("/loyalty", response_model=LoyaltyAccountResponse)
async def get_loyalty_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    account = await commerce_service.get_or_create_loyalty_account(db, current_user.id)
    ledger = await commerce_service.list_loyalty_ledger(db, account.id)
    return LoyaltyAccountResponse(
        user_id=account.user_id,
        points_balance=account.points_balance,
        tier=account.tier,
        updated_at=account.updated_at,
        ledger=[
            LoyaltyLedgerResponse(
                id=item.id,
                delta=item.delta,
                reason=item.reason,
                reference=item.reference,
                created_at=item.created_at,
            )
            for item in ledger
        ],
    )


@router.post("/loyalty/award", response_model=LoyaltyAccountResponse)
async def award_loyalty_points(
    payload: LoyaltyAwardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    target_user_id = payload.user_id or current_user.id
    if payload.user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can award points to other users")

    account = await commerce_service.award_loyalty_points(
        db,
        user_id=target_user_id,
        points=payload.points,
        reason=payload.reason,
        reference=payload.reference,
    )
    ledger = await commerce_service.list_loyalty_ledger(db, account.id)
    return LoyaltyAccountResponse(
        user_id=account.user_id,
        points_balance=account.points_balance,
        tier=account.tier,
        updated_at=account.updated_at,
        ledger=[
            LoyaltyLedgerResponse(
                id=item.id,
                delta=item.delta,
                reason=item.reason,
                reference=item.reference,
                created_at=item.created_at,
            )
            for item in ledger
        ],
    )


@router.get("/contracts", response_model=list[ContractResponse])
async def list_contracts(
    all_contracts: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(CustomerContract).order_by(desc(CustomerContract.created_at))
    if not current_user.is_superuser or not all_contracts:
        query = query.where(CustomerContract.user_id == current_user.id)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/contracts", response_model=ContractResponse)
async def create_contract(
    payload: ContractCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    if payload.user_id and payload.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can assign contracts to other users")

    target_user_id = payload.user_id or current_user.id
    contract = await commerce_service.create_contract(
        db,
        user_id=target_user_id,
        org_name=payload.org_name,
        status=payload.status,
        value=payload.value,
        currency=payload.currency,
        start_date=payload.start_date,
        end_date=payload.end_date,
        terms=payload.terms,
    )
    return contract
