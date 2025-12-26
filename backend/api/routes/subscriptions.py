from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import uuid
from datetime import datetime, timedelta

from backend.core.database import get_async_db as get_db
from backend.services.payment_service import PaymentService
from backend.models.subscription import UserSubscription, VideoRevenue

router = APIRouter()

@router.post("/subscriptions/create")
async def create_subscription(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription"""
    try:
        user_id = request.get("user_id", str(uuid.uuid4()))  # Generate if not provided
        plan_id = request.get("plan_id")
        
        if not plan_id:
            raise HTTPException(status_code=400, detail="plan_id is required")
        
        payment_service = PaymentService()
        
        # Create subscription in Stripe
        subscription_data = await payment_service.create_subscription(user_id, plan_id)
        
        # Get pricing tier for period dates
        pricing_tier = payment_service.get_pricing_tier(plan_id)
        
        # Create subscription record in database
        subscription = UserSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            plan_id=plan_id,
            stripe_subscription_id=subscription_data["subscription_id"],
            stripe_customer_id=subscription_data["customer_id"],
            current_period_start=datetime.now(),
            current_period_end=datetime.now() + timedelta(days=30)
        )
        
        db.add(subscription)
        await db.commit()
        
        return {
            "subscription_id": subscription.id,
            "client_secret": subscription_data["client_secret"],
            "plan_id": plan_id,
            "pricing_tier": pricing_tier
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions/{user_id}")
async def get_user_subscription(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user's subscription details"""
    try:
        # Get from database
        result = await db.execute(
            "SELECT * FROM user_subscriptions WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        subscription = result.fetchone()
        
        if not subscription:
            return {"subscription": None}
        
        # Get from Stripe for latest status
        payment_service = PaymentService()
        stripe_subscription = await payment_service.get_user_subscription(user_id)
        
        return {
            "subscription": {
                "id": subscription.id,
                "plan_id": subscription.plan_id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start.isoformat(),
                "current_period_end": subscription.current_period_end.isoformat(),
                "videos_used_this_month": subscription.videos_used_this_month,
                "total_revenue_this_month": subscription.total_revenue_this_month,
                "stripe_status": stripe_subscription.get("status") if stripe_subscription else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscriptions/{user_id}/cancel")
async def cancel_subscription(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel user subscription"""
    try:
        payment_service = PaymentService()
        
        # Cancel in Stripe
        result = await payment_service.cancel_subscription(user_id)
        
        # Update database
        await db.execute(
            "UPDATE user_subscriptions SET status = 'cancelled' WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        await db.commit()
        
        return result
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revenue/track")
async def track_video_revenue(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Track revenue from a video"""
    try:
        video_id = request.get("video_id")
        user_id = request.get("user_id")
        amount = request.get("amount")
        source = request.get("source", "youtube_ads")
        
        if not all([video_id, user_id, amount]):
            raise HTTPException(status_code=400, detail="video_id, user_id, and amount are required")
        
        # Create revenue record
        revenue = VideoRevenue(
            id=str(uuid.uuid4()),
            video_id=video_id,
            user_id=user_id,
            amount=amount,
            source=source
        )
        
        db.add(revenue)
        
        # Update user's monthly revenue
        await db.execute(
            "UPDATE user_subscriptions SET total_revenue_this_month = total_revenue_this_month + ? WHERE user_id = ? AND status = 'active'",
            (amount, user_id)
        )
        
        await db.commit()
        
        # Process revenue share if applicable
        payment_service = PaymentService()
        await payment_service.process_revenue_share(user_id, amount)
        
        return {
            "message": "Revenue tracked successfully",
            "revenue_id": revenue.id,
            "amount": amount
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue/{user_id}")
async def get_user_revenue(
    user_id: str,
    period: str = "month",
    db: AsyncSession = Depends(get_db)
):
    """Get user's revenue analytics"""
    try:
        # Calculate date range
        end_date = datetime.now()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get revenue data
        result = await db.execute(
            """
            SELECT 
                SUM(amount) as total_revenue,
                COUNT(*) as total_videos,
                source,
                DATE(date) as revenue_date
            FROM video_revenue 
            WHERE user_id = ? AND date >= ?
            GROUP BY source, DATE(date)
            ORDER BY revenue_date DESC
            """,
            (user_id, start_date)
        )
        
        revenue_data = result.fetchall()
        
        # Calculate totals
        total_revenue = sum(row.total_revenue for row in revenue_data)
        total_videos = sum(row.total_videos for row in revenue_data)
        
        # Group by source
        revenue_by_source = {}
        for row in revenue_data:
            if row.source not in revenue_by_source:
                revenue_by_source[row.source] = 0
            revenue_by_source[row.source] += row.total_revenue
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_revenue": total_revenue,
            "total_videos": total_videos,
            "revenue_by_source": revenue_by_source,
            "daily_revenue": [
                {
                    "date": row.revenue_date.isoformat(),
                    "revenue": row.total_revenue,
                    "videos": row.total_videos,
                    "source": row.source
                }
                for row in revenue_data
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        payment_service = PaymentService()
        result = await payment_service.process_webhook(payload, sig_header)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pricing")
async def get_pricing_tiers():
    """Get available pricing tiers"""
    try:
        payment_service = PaymentService()
        
        pricing_tiers = {}
        for plan_id in ["starter", "professional", "enterprise"]:
            pricing_tiers[plan_id] = payment_service.get_pricing_tier(plan_id)
        
        return {
            "pricing_tiers": pricing_tiers,
            "currency": "USD",
            "billing_interval": "month"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 