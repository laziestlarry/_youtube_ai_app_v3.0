#!/usr/bin/env python3
"""
Test script for the payment system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.payment_service import PaymentService
from backend.models.subscription import UserSubscription, VideoRevenue
import uuid
from datetime import datetime, timedelta

async def test_payment_service():
    """Test the payment service functionality"""
    print("🧪 Testing Payment Service...")
    
    payment_service = PaymentService()
    
    # Test 1: Get pricing tiers
    print("\n1. Testing pricing tiers...")
    try:
        starter_tier = payment_service.get_pricing_tier("starter")
        professional_tier = payment_service.get_pricing_tier("professional")
        enterprise_tier = payment_service.get_pricing_tier("enterprise")
        
        print(f"✅ Starter tier: ${starter_tier['price']}/month")
        print(f"✅ Professional tier: ${professional_tier['price']}/month")
        print(f"✅ Enterprise tier: ${enterprise_tier['price']}/month")
        
        # Test invalid tier
        try:
            payment_service.get_pricing_tier("invalid")
            print("❌ Should have raised an error for invalid tier")
        except Exception as e:
            print(f"✅ Correctly rejected invalid tier: {e}")
            
    except Exception as e:
        print(f"❌ Failed to get pricing tiers: {e}")
    
    # Test 2: Create customer
    print("\n2. Testing customer creation...")
    try:
        test_user_id = str(uuid.uuid4())
        customer = await payment_service.get_or_create_customer(test_user_id)
        print(f"✅ Customer created: {customer.id}")
    except Exception as e:
        print(f"❌ Failed to create customer: {e}")
    
    # Test 3: Revenue share calculation
    print("\n3. Testing revenue share calculation...")
    try:
        # Test with revenue below threshold
        await payment_service.process_revenue_share(test_user_id, 500)
        print("✅ Revenue share processed (below threshold)")
        
        # Test with revenue above threshold
        await payment_service.process_revenue_share(test_user_id, 1500)
        print("✅ Revenue share processed (above threshold)")
        
    except Exception as e:
        print(f"❌ Failed to process revenue share: {e}")
    
    print("\n🎉 Payment service tests completed!")

async def test_database_models():
    """Test the database models"""
    print("\n🧪 Testing Database Models...")
    
    # Test 1: Create sample subscription
    print("\n1. Testing subscription model...")
    try:
        subscription = UserSubscription(
            id=str(uuid.uuid4()),
            user_id="test_user_001",
            plan_id="professional",
            stripe_subscription_id="sub_test_001",
            stripe_customer_id="cus_test_001",
            current_period_start=datetime.now(),
            current_period_end=datetime.now() + timedelta(days=30)
        )
        print(f"✅ Subscription model created: {subscription.id}")
        print(f"   Plan: {subscription.plan_id}")
        print(f"   Status: {subscription.status}")
        
    except Exception as e:
        print(f"❌ Failed to create subscription model: {e}")
    
    # Test 2: Create sample revenue
    print("\n2. Testing revenue model...")
    try:
        revenue = VideoRevenue(
            id=str(uuid.uuid4()),
            video_id="video_001",
            user_id="test_user_001",
            amount=45.50,
            source="youtube_ads"
        )
        print(f"✅ Revenue model created: {revenue.id}")
        print(f"   Amount: ${revenue.amount}")
        print(f"   Source: {revenue.source}")
        
    except Exception as e:
        print(f"❌ Failed to create revenue model: {e}")
    
    print("\n🎉 Database model tests completed!")

async def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    
    import httpx
    
    base_url = "http://localhost:8000"
    
    # Test 1: Get pricing tiers
    print("\n1. Testing /api/pricing endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/pricing")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Pricing endpoint: {len(data.get('pricing_tiers', {}))} tiers found")
            else:
                print(f"❌ Pricing endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to test pricing endpoint: {e}")
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data.get('status')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to test health check: {e}")
    
    print("\n🎉 API endpoint tests completed!")

async def main():
    """Run all tests"""
    print("🚀 Starting Payment System Tests")
    print("=" * 50)
    
    await test_payment_service()
    await test_database_models()
    await test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Set up Stripe test keys in environment variables")
    print("2. Run the database migration script")
    print("3. Start the backend server")
    print("4. Test the frontend integration")

if __name__ == "__main__":
    asyncio.run(main()) 