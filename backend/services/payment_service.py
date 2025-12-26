import stripe
from fastapi import HTTPException
from typing import Dict, Any, Optional
from backend.config.enhanced_settings import settings
from backend.models.subscription import UserSubscription, VideoRevenue
from backend.core.database import get_async_db as get_db
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

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
        
    async def create_subscription(self, user_id: str, plan_id: str, email: str = None) -> Dict[str, Any]:
        """Create subscription for user"""
        try:
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
    
    async def process_revenue_share(self, user_id: str, monthly_revenue: float, db):
        """Process revenue share for eligible users"""
        # Get user subscription from DB
        query = select(UserSubscription).where(UserSubscription.user_id == user_id, UserSubscription.status == 'active')
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