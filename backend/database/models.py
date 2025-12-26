from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    channels = relationship("Channel", back_populates="owner")
    subscriptions = relationship("UserSubscription", back_populates="user")
    video_revenues = relationship("VideoRevenue", back_populates="user")
    digital_products = relationship("DigitalProduct", back_populates="creator")
    affiliate_links = relationship("AffiliateLink", back_populates="user")
    payment_transactions = relationship("PaymentTransaction", back_populates="user")

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    youtube_channel_id = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(Text)
    subscriber_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="channels")
    videos = relationship("Video", back_populates="channel")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    tags = Column(Text)  # JSON string
    category = Column(String)
    duration = Column(Integer)  # seconds
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    status = Column(String, default="draft")  # draft, published, scheduled
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    channel_id = Column(Integer, ForeignKey("channels.id"))
    
    # Relationships
    channel = relationship("Channel", back_populates="videos")
    monetization_records = relationship("MonetizationRecord", back_populates="video")
    analytics_records = relationship("AnalyticsRecord", back_populates="video")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id_fk = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

class VideoRevenue(Base):
    __tablename__ = "video_revenue"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    source = Column(String, nullable=False)  # youtube_ads, sponsorship, affiliate, etc.
    currency = Column(String, default="USD")
    date = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text)  # JSON string for additional data
    
    # Foreign Keys
    user_id_fk = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="video_revenues")

class DigitalProduct(Base):
    __tablename__ = "digital_products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    creator_id_fk = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", back_populates="digital_products")

class AffiliateLink(Base):
    __tablename__ = "affiliate_links"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    product_id = Column(String, index=True)  # Optional, for specific product links
    code = Column(String, nullable=False, unique=True)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    total_commission = Column(Float, default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id_fk = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="affiliate_links")
    clicks = relationship("AffiliateClick", back_populates="affiliate_link")
    conversions = relationship("AffiliateConversion", back_populates="affiliate_link")

class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    affiliate_id = Column(String, nullable=False, index=True)
    visitor_ip = Column(String)
    user_agent = Column(Text)
    referrer = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    affiliate_id_fk = Column(String, ForeignKey("affiliate_links.id"))
    
    # Relationships
    affiliate_link = relationship("AffiliateLink", back_populates="clicks")

class AffiliateConversion(Base):
    __tablename__ = "affiliate_conversions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    affiliate_id = Column(String, nullable=False, index=True)
    sale_amount = Column(Float, nullable=False)
    commission_amount = Column(Float, nullable=False)
    product_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    affiliate_id_fk = Column(String, ForeignKey("affiliate_links.id"))
    
    # Relationships
    affiliate_link = relationship("AffiliateLink", back_populates="conversions")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    stripe_payment_intent_id = Column(String, unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False)  # pending, succeeded, failed
    type = Column(String, nullable=False)  # subscription, revenue_share, product_purchase
    metadata_json = Column(Text)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id_fk = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="payment_transactions")

class MonetizationRecord(Base):
    __tablename__ = "monetization"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, nullable=False)
    ad_revenue = Column(Float, default=0.0)
    sponsorship_revenue = Column(Float, default=0.0)
    affiliate_revenue = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)
    rpm = Column(Float, default=0.0)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    video_id_fk = Column(Integer, ForeignKey("videos.id"))
    
    # Relationships
    video = relationship("Video", back_populates="monetization_records")

class AnalyticsRecord(Base):
    __tablename__ = "analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    record_metadata = Column(JSON)
    
    # Foreign Keys
    video_id_fk = Column(Integer, ForeignKey("videos.id"))
    
    # Relationships
    video = relationship("Video", back_populates="analytics_records")

class ContentIdea(Base):
    __tablename__ = "content_ideas"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    target_audience = Column(String)
    keywords = Column(Text)  # JSON string
    estimated_views = Column(Integer, default=0)
    estimated_revenue = Column(Float, default=0.0)
    priority = Column(Integer, default=5)  # 1-10 scale
    status = Column(String, default="pending")  # pending, approved, rejected, completed
    created_by = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    created_by_fk = Column(Integer, ForeignKey("users.id"))

class ScheduledContent(Base):
    __tablename__ = "scheduled_content"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_idea_id = Column(String, nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, processing, completed, failed
    priority = Column(Integer, default=5)
    auto_publish = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    record_metadata = Column(JSON)
    
    # Foreign Keys
    content_idea_id_fk = Column(String, ForeignKey("content_ideas.id"))