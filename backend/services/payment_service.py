import os
import stripe
from fastapi import HTTPException
from typing import Dict, Any, Optional
from sqlalchemy import select, update
from backend.config.enhanced_settings import settings
from backend.models.subscription import UserSubscription, VideoRevenue
from backend.core.database import get_async_db as get_db
import logging

logger = logging.getLogger(__name__)
from modules.ai_agency.shopier_service import shopier_service

# Pricing Tiers Configuration (could be moved to DB or settings)
PRICING_TIERS = {
    "starter": {
        "price_id": "price_starter_monthly", # Replace with actual Stripe Price ID
        "features": {"revenue_share": 0.0}
    },
    "professional": {
        "price_id": "price_pro_monthly",
        "features": {"revenue_share": 0.10}
    },
    "enterprise": {
        "price_id": "price_enterprise_monthly",
        "features": {"revenue_share": 0.05}
    }
}

class PaymentService:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.payment.stripe_secret_key
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET") or os.getenv("PAYMENT_STRIPE_WEBHOOK_SECRET")

    def _ensure_stripe_configured(self) -> None:
        if not self.stripe.api_key:
            raise HTTPException(status_code=400, detail="Stripe secret key is not configured")
        
    async def create_subscription(self, user_id: str, plan_id: str, email: str = None) -> Dict[str, Any]:
        """Create subscription for user"""
        try:
            self._ensure_stripe_configured()
            # Create or get customer
            customers = self.stripe.Customer.list(email=email).data if email else []
            if customers:
                customer_id = customers[0].id
            else:
                customer_id = self.stripe.Customer.create(email=email, metadata={"user_id": user_id}).id

            # Get price ID from configuration
            price_id = PRICING_TIERS.get(plan_id, {}).get("price_id")
            if not price_id:
                raise HTTPException(status_code=400, detail="Invalid plan ID")

            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
                metadata={"user_id": user_id, "plan_id": plan_id}
            )
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "customer_id": customer_id
            }
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def create_shopier_payment(self, amount: float, currency: str, order_id: str, product_name: str) -> str:
        """Generate a Shopier payment link"""
        return shopier_service.generate_payment_link(amount, currency, order_id, product_name)

    def get_pricing_tier(self, plan_id: str) -> Dict[str, Any]:
        """Return pricing tier details for a plan."""
        if plan_id not in PRICING_TIERS:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        tier = PRICING_TIERS[plan_id]
        return {
            "plan_id": plan_id,
            "price_id": tier.get("price_id"),
            "features": tier.get("features", {}),
            "billing_interval": "month",
        }

    def retrieve_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a subscription from Stripe."""
        if not subscription_id:
            return None
        self._ensure_stripe_configured()
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
            }
        except Exception as e:
            logger.warning("Stripe subscription fetch failed: %s", e)
            return None

    def cancel_stripe_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Stripe subscription by ID."""
        if not subscription_id:
            raise HTTPException(status_code=400, detail="Subscription ID is required")
        self._ensure_stripe_configured()
        try:
            subscription = self.stripe.Subscription.cancel(subscription_id)
            return {"status": subscription.status, "subscription_id": subscription.id}
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def process_webhook(self, payload: bytes, sig_header: str, db=None) -> Dict[str, Any]:
        """Process Stripe webhook event."""
        if not self.webhook_secret:
            raise HTTPException(status_code=400, detail="Stripe webhook secret is not configured")
        try:
            event = self.stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=self.webhook_secret,
            )
        except Exception as e:
            logger.error("Webhook signature verification failed: %s", e)
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        event_type = event.get("type")
        data_object = (event.get("data") or {}).get("object", {})
        subscription_id = data_object.get("id")

        if db is not None and subscription_id:
            if event_type in ("customer.subscription.updated", "customer.subscription.created"):
                status = data_object.get("status", "active")
                await db.execute(
                    update(UserSubscription)
                    .where(UserSubscription.stripe_subscription_id == subscription_id)
                    .values(status=status)
                )
                await db.commit()
            elif event_type == "customer.subscription.deleted":
                await db.execute(
                    update(UserSubscription)
                    .where(UserSubscription.stripe_subscription_id == subscription_id)
                    .values(status="cancelled")
                )
                await db.commit()

        return {"status": "ok", "event_type": event_type}
    
    async def process_revenue_share(self, user_id: str, monthly_revenue: float, db):
        """Process revenue share for eligible users"""
        # Get user subscription from DB
        query = select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.status == 'active'
        )
        result = await db.execute(query)
        subscription = result.scalars().first()
        
        if not subscription or subscription.plan_id not in ["professional", "enterprise"]:
            return
            
        revenue_share_rate = PRICING_TIERS[subscription.plan_id]["features"]["revenue_share"]
        
        # Threshold for revenue share
        if monthly_revenue > 1000:
            revenue_share_amount = monthly_revenue * revenue_share_rate
            # Here we would trigger a payout via Payoneer or Stripe Connect
            logger.info(f"CALCULATED REVENUE SHARE for {user_id}: {revenue_share_amount}")
            # await self.charge_revenue_share(user_id, revenue_share_amount) # Placeholder
            
            # Record it
            subscription.revenue_share_paid += revenue_share_amount
            await db.commit()
