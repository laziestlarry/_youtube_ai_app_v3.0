#!/usr/bin/env python3
"""
Fake Customer Data Generator for YouTube AI Creator Platform
Generates realistic user data for development and testing
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sqlite3
import os

class FakeCustomerDataGenerator:
    def __init__(self):
        self.db_path = "backend/youtube_ai.db"
        self.fake_data = {
            "users": [],
            "subscriptions": [],
            "revenue": [],
            "videos": [],
            "affiliate_links": [],
            "digital_products": []
        }
        
        # Realistic user data templates
        self.names = [
            "Sarah Johnson", "Mike Chen", "Emma Rodriguez", "David Kim", "Lisa Thompson",
            "Alex Martinez", "Jessica Lee", "Ryan Wilson", "Amanda Davis", "Chris Brown",
            "Maria Garcia", "James Taylor", "Sophie Anderson", "Kevin Nguyen", "Rachel Green",
            "Daniel White", "Nicole Clark", "Andrew Lewis", "Hannah Walker", "Brandon Hall"
        ]
        
        self.channel_names = [
            "Tech Tips Daily", "Business Growth Secrets", "Lifestyle & Travel", "Cooking Masterclass",
            "Fitness Motivation", "Personal Finance Tips", "DIY Crafts & Projects", "Gaming Adventures",
            "Educational Insights", "Product Reviews Pro", "Health & Wellness", "Creative Tutorials",
            "Investment Strategies", "Home Improvement", "Pet Care Guide", "Music Production",
            "Photography Tips", "Language Learning", "Science Explained", "Career Development"
        ]
        
        self.pain_points = [
            "Limited time for content creation",
            "High content creation costs",
            "Inconsistent upload schedule",
            "Low video quality",
            "Poor monetization",
            "Difficulty scaling content",
            "Lack of engagement",
            "SEO optimization challenges",
            "Thumbnail design struggles",
            "Script writing difficulties"
        ]
        
        self.success_stories = [
            "I went from 1 video per week to 5 videos per day!",
            "This platform paid for itself in the first week!",
            "My channel exploded after using this platform!",
            "I finally have time to focus on my business!",
            "My revenue increased by 300% in just 2 months!",
            "I can now create content while traveling!",
            "The AI suggestions are incredibly accurate!",
            "I've never been more productive!",
            "This is a game-changer for content creators!",
            "I'm making more money than ever before!"
        ]
    
    def generate_fake_users(self, count: int = 1000) -> List[Dict[str, Any]]:
        """Generate fake user profiles"""
        users = []
        
        for i in range(count):
            user_id = str(uuid.uuid4())
            name = random.choice(self.names)
            channel_name = random.choice(self.channel_names)
            
            # Realistic subscriber counts with proper ranges
            subscriber_choice = random.random()
            if subscriber_choice < 0.4:
                subscribers = random.randint(100, 1000)
            elif subscriber_choice < 0.7:
                subscribers = random.randint(1000, 10000)
            elif subscriber_choice < 0.9:
                subscribers = random.randint(10000, 100000)
            else:
                subscribers = random.randint(100000, 1000000)
            
            # Realistic revenue based on subscribers
            avg_revenue_per_subscriber = random.uniform(0.01, 0.05)
            monthly_revenue = subscribers * avg_revenue_per_subscriber
            
            user = {
                "id": user_id,
                "name": name,
                "email": f"{name.lower().replace(' ', '.')}@example.com",
                "channel_name": channel_name,
                "subscribers": subscribers,
                "monthly_revenue": round(monthly_revenue, 2),
                "pain_point": random.choice(self.pain_points),
                "success_story": random.choice(self.success_stories),
                "plan": random.choices(
                    ["starter", "professional", "enterprise"],
                    weights=[0.4, 0.5, 0.1]
                )[0],
                "created_at": datetime.now() - timedelta(days=random.randint(1, 90)),
                "last_active": datetime.now() - timedelta(days=random.randint(0, 7)),
                "videos_created": random.randint(1, 50),
                "total_revenue_generated": round(monthly_revenue * random.uniform(1, 6), 2)
            }
            
            users.append(user)
        
        return users
    
    def generate_fake_subscriptions(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate fake subscription data"""
        subscriptions = []
        
        for user in users:
            plan_prices = {"starter": 29, "professional": 99, "enterprise": 299}
            price = plan_prices[user["plan"]]
            
            subscription = {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "plan_id": user["plan"],
                "stripe_subscription_id": f"sub_fake_{random.randint(100000, 999999)}",
                "stripe_customer_id": f"cus_fake_{random.randint(100000, 999999)}",
                "status": "active",
                "current_period_start": user["created_at"],
                "current_period_end": user["created_at"] + timedelta(days=30),
                "videos_used_this_month": user["videos_created"],
                "total_revenue_this_month": user["monthly_revenue"],
                "revenue_share_paid": round(user["monthly_revenue"] * 0.05, 2) if user["plan"] in ["professional", "enterprise"] else 0,
                "created_at": user["created_at"],
                "updated_at": user["last_active"]
            }
            
            subscriptions.append(subscription)
        
        return subscriptions
    
    def generate_fake_revenue(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate fake revenue tracking data"""
        revenue_records = []
        
        for user in users:
            # Generate multiple revenue records per user
            num_records = random.randint(1, 10)
            
            for _ in range(num_records):
                revenue_sources = ["youtube_ads", "sponsorship", "affiliate", "merchandise", "courses"]
                source = random.choice(revenue_sources)
                
                # Realistic revenue amounts based on source
                if source == "youtube_ads":
                    amount = random.uniform(10, user["monthly_revenue"] * 0.6)
                elif source == "sponsorship":
                    amount = random.uniform(50, user["monthly_revenue"] * 0.8)
                elif source == "affiliate":
                    amount = random.uniform(5, user["monthly_revenue"] * 0.3)
                else:
                    amount = random.uniform(20, user["monthly_revenue"] * 0.5)
                
                revenue_record = {
                    "id": str(uuid.uuid4()),
                    "video_id": f"video_{random.randint(100000, 999999)}",
                    "user_id": user["id"],
                    "amount": round(amount, 2),
                    "source": source,
                    "currency": "USD",
                    "date": user["created_at"] + timedelta(days=random.randint(1, 90)),
                    "metadata_json": json.dumps({
                        "video_title": f"Amazing {source.replace('_', ' ').title()} Content",
                        "views": random.randint(1000, 100000),
                        "engagement_rate": round(random.uniform(0.02, 0.08), 3)
                    })
                }
                
                revenue_records.append(revenue_record)
        
        return revenue_records
    
    def generate_fake_videos(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate fake video creation data"""
        videos = []
        
        for user in users:
            num_videos = user["videos_created"]
            
            for i in range(num_videos):
                video = {
                    "id": f"video_{random.randint(100000, 999999)}",
                    "user_id": user["id"],
                    "title": f"Amazing {random.choice(['Tech', 'Business', 'Lifestyle', 'Education'])} Content #{i+1}",
                    "description": f"AI-generated content about {random.choice(['technology', 'business', 'lifestyle', 'education'])}",
                    "views": random.randint(100, user["subscribers"] * 2),
                    "likes": random.randint(10, user["subscribers"] * 0.1),
                    "comments": random.randint(0, user["subscribers"] * 0.05),
                    "duration": random.randint(60, 1800),  # 1-30 minutes
                    "created_at": user["created_at"] + timedelta(days=random.randint(1, 90)),
                    "ai_generated": True,
                    "revenue_generated": round(random.uniform(5, user["monthly_revenue"] * 0.2), 2)
                }
                
                videos.append(video)
        
        return videos
    
    def generate_fake_affiliate_links(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate fake affiliate link data"""
        affiliate_links = []
        
        # 30% of users participate in affiliate program
        affiliate_users = random.sample(users, min(int(len(users) * 0.3), len(users)))
        
        for user in affiliate_users:
            num_links = random.randint(1, 5)
            
            for i in range(num_links):
                affiliate_link = {
                    "id": str(uuid.uuid4()),
                    "user_id": user["id"],
                    "product_id": f"prod_{random.randint(100000, 999999)}",
                    "code": f"{user['name'].lower().replace(' ', '')}{random.randint(100, 999)}",
                    "clicks": random.randint(10, 1000),
                    "conversions": random.randint(1, max(1, int(user["subscribers"] * 0.01))),
                    "total_commission": round(random.uniform(10, 500), 2),
                    "status": "active",
                    "created_at": user["created_at"] + timedelta(days=random.randint(1, 90))
                }
                
                affiliate_links.append(affiliate_link)
        
        return affiliate_links
    
    def generate_fake_digital_products(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate fake digital product marketplace data"""
        digital_products = []
        
        # 20% of users create digital products
        creator_users = random.sample(users, min(int(len(users) * 0.2), len(users)))
        
        product_categories = ["course", "template", "tool", "ebook", "software"]
        product_names = [
            "YouTube Success Masterclass", "AI Content Templates", "Analytics Dashboard Pro",
            "Thumbnail Design Kit", "SEO Optimization Guide", "Monetization Blueprint",
            "Video Editing Templates", "Social Media Strategy", "Brand Building Course",
            "Affiliate Marketing Guide"
        ]
        
        for user in creator_users:
            num_products = random.randint(1, 3)
            
            for i in range(num_products):
                product = {
                    "id": str(uuid.uuid4()),
                    "name": random.choice(product_names),
                    "description": f"Amazing {random.choice(product_categories)} for content creators",
                    "price": round(random.uniform(19.99, 199.99), 2),
                    "category": random.choice(product_categories),
                    "file_url": f"https://example.com/products/{random.randint(100000, 999999)}.pdf",
                    "thumbnail_url": f"https://example.com/thumbnails/{random.randint(100000, 999999)}.jpg",
                    "creator_id": user["id"],
                    "sales_count": random.randint(0, 100),
                    "total_revenue": round(random.uniform(0, 5000), 2),
                    "commission_rate": 0.30,
                    "status": "active",
                    "created_at": user["created_at"] + timedelta(days=random.randint(1, 90)),
                    "updated_at": user["last_active"]
                }
                
                digital_products.append(product)
        
        return digital_products
    
    def insert_fake_data_to_database(self):
        """Insert fake data into the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("🗄️  Inserting fake data into database...")
            
            # Generate fake data
            users = self.generate_fake_users(1000)
            subscriptions = self.generate_fake_subscriptions(users)
            revenue_records = self.generate_fake_revenue(users)
            videos = self.generate_fake_videos(users)
            affiliate_links = self.generate_fake_affiliate_links(users)
            digital_products = self.generate_fake_digital_products(users)
            
            # Insert users (simplified - just store in memory for now)
            print(f"✅ Generated {len(users)} fake users")
            print(f"✅ Generated {len(subscriptions)} fake subscriptions")
            print(f"✅ Generated {len(revenue_records)} fake revenue records")
            print(f"✅ Generated {len(videos)} fake videos")
            print(f"✅ Generated {len(affiliate_links)} fake affiliate links")
            print(f"✅ Generated {len(digital_products)} fake digital products")
            
            # Save to JSON file for easy access
            fake_data = {
                "users": users,
                "subscriptions": subscriptions,
                "revenue": revenue_records,
                "videos": videos,
                "affiliate_links": affiliate_links,
                "digital_products": digital_products,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_users": len(users),
                    "total_revenue": sum(user["total_revenue_generated"] for user in users),
                    "avg_monthly_revenue": sum(user["monthly_revenue"] for user in users) / len(users),
                    "total_videos": len(videos),
                    "total_affiliate_links": len(affiliate_links),
                    "total_digital_products": len(digital_products)
                }
            }
            
            with open("fake_customer_data.json", "w") as f:
                json.dump(fake_data, f, indent=2)
            
            print("✅ Fake data saved to fake_customer_data.json")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error inserting fake data: {e}")
    
    def generate_analytics_report(self):
        """Generate analytics report from fake data"""
        try:
            with open("fake_customer_data.json", "r") as f:
                data = json.load(f)
            
            users = data["users"]
            subscriptions = data["subscriptions"]
            revenue = data["revenue"]
            
            # Calculate key metrics
            total_users = len(users)
            total_revenue = sum(user["total_revenue_generated"] for user in users)
            avg_monthly_revenue = sum(user["monthly_revenue"] for user in users) / len(users)
            
            plan_distribution = {}
            for sub in subscriptions:
                plan = sub["plan_id"]
                plan_distribution[plan] = plan_distribution.get(plan, 0) + 1
            
            revenue_by_source = {}
            for rev in revenue:
                source = rev["source"]
                revenue_by_source[source] = revenue_by_source.get(source, 0) + rev["amount"]
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "metrics": {
                    "total_users": total_users,
                    "total_revenue": round(total_revenue, 2),
                    "avg_monthly_revenue": round(avg_monthly_revenue, 2),
                    "avg_subscribers": round(sum(user["subscribers"] for user in users) / len(users), 0),
                    "avg_videos_created": round(sum(user["videos_created"] for user in users) / len(users), 1)
                },
                "plan_distribution": plan_distribution,
                "revenue_by_source": {k: round(v, 2) for k, v in revenue_by_source.items()},
                "top_performers": sorted(users, key=lambda x: x["monthly_revenue"], reverse=True)[:10]
            }
            
            with open("fake_analytics_report.json", "w") as f:
                json.dump(report, f, indent=2)
            
            print("📊 Analytics report generated: fake_analytics_report.json")
            
            # Print summary
            print(f"\n📈 Fake Data Summary:")
            print(f"   Total Users: {total_users:,}")
            print(f"   Total Revenue: ${total_revenue:,.2f}")
            print(f"   Avg Monthly Revenue: ${avg_monthly_revenue:.2f}")
            print(f"   Plan Distribution: {plan_distribution}")
            
        except Exception as e:
            print(f"❌ Error generating analytics: {e}")

def main():
    """Main function to generate fake customer data"""
    print("🚀 Generating Fake Customer Data for Development")
    print("=" * 50)
    
    generator = FakeCustomerDataGenerator()
    
    # Generate and insert fake data
    generator.insert_fake_data_to_database()
    
    # Generate analytics report
    generator.generate_analytics_report()
    
    print("\n" + "=" * 50)
    print("🎉 Fake Customer Data Generation Complete!")
    print("Ready for development and testing with realistic data!")

if __name__ == "__main__":
    main() 