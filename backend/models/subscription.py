from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from backend.core.database import Base

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    plan_id = Column(String, nullable=False)
    stripe_subscription_id = Column(String, nullable=False, unique=True)
    stripe_customer_id = Column(String, nullable=False)
    status = Column(String, default="active")
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    videos_used_this_month = Column(Integer, default=0)
    total_revenue_this_month = Column(Float, default=0.0)
    revenue_share_paid = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class VideoRevenue(Base):
    __tablename__ = "video_revenue"
    
    id = Column(String, primary_key=True)
    video_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    source = Column(String, nullable=False)  # youtube_ads, sponsorship, affiliate, etc.
    currency = Column(String, default="USD")
    date = Column(DateTime, server_default=func.now())
    metadata_json = Column(Text)  # JSON string for additional data

class DigitalProduct(Base):
    __tablename__ = "digital_products"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # course, template, tool
    file_url = Column(String)
    thumbnail_url = Column(String)
    creator_id = Column(String, nullable=False, index=True)
    sales_count = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    commission_rate = Column(Float, default=0.30)  # 30% platform fee
    status = Column(String, default="active")  # active, inactive, deleted
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class AffiliateLink(Base):
    __tablename__ = "affiliate_links"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    product_id = Column(String, index=True)  # Optional, for specific product links
    code = Column(String, nullable=False, unique=True)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    total_commission = Column(Float, default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())

class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"
    
    id = Column(String, primary_key=True)
    affiliate_id = Column(String, nullable=False, index=True)
    visitor_ip = Column(String)
    user_agent = Column(Text)
    referrer = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

class AffiliateConversion(Base):
    __tablename__ = "affiliate_conversions"
    
    id = Column(String, primary_key=True)
    affiliate_id = Column(String, nullable=False, index=True)
    sale_amount = Column(Float, nullable=False)
    commission_amount = Column(Float, nullable=False)
    product_id = Column(String, index=True)
    timestamp = Column(DateTime, server_default=func.now())

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    stripe_payment_intent_id = Column(String, unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False)  # pending, succeeded, failed
    type = Column(String, nullable=False)  # subscription, revenue_share, product_purchase
    metadata_json = Column(Text)  # JSON string for additional data
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now()) 