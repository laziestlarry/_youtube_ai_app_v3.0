from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from backend.core.database import Base


class CustomerJourneyEvent(Base):
    __tablename__ = "customer_journey_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    stage = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=True)
    sku = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    points_balance = Column(Integer, nullable=False, default=0)
    tier = Column(String, nullable=False, default="bronze")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LoyaltyLedger(Base):
    __tablename__ = "loyalty_ledger"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("loyalty_accounts.id"), nullable=False, index=True)
    delta = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    reference = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CustomerContract(Base):
    __tablename__ = "customer_contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    org_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    value = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    terms = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommerceAsset(Base):
    __tablename__ = "commerce_assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    checksum = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CommerceOffer(Base):
    __tablename__ = "commerce_offers"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    status = Column(String, nullable=False, default="active")
    offer_type = Column(String, nullable=False, default="printable")
    asset_id = Column(Integer, ForeignKey("commerce_assets.id"), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommerceOrder(Base):
    __tablename__ = "commerce_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    offer_id = Column(Integer, ForeignKey("commerce_offers.id"), nullable=True)
    customer_email = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    status = Column(String, nullable=False, default="initiated")
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=False, default="USD")
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommerceDelivery(Base):
    __tablename__ = "commerce_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("commerce_orders.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("commerce_assets.id"), nullable=True)
    method = Column(String, nullable=False, default="signed_link")
    status = Column(String, nullable=False, default="pending")
    token = Column(String, nullable=True, index=True)
    download_url = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
