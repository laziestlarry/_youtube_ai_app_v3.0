#!/usr/bin/env python3
"""
Database migration script to create subscription and revenue tracking tables
"""

import sqlite3
import os
from datetime import datetime

def create_subscription_tables():
    """Create all subscription and revenue tracking tables"""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "youtube_ai.db")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Creating subscription and revenue tracking tables...")
    
    # Create user_subscriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            plan_id VARCHAR NOT NULL,
            stripe_subscription_id VARCHAR NOT NULL UNIQUE,
            stripe_customer_id VARCHAR NOT NULL,
            status VARCHAR DEFAULT 'active',
            current_period_start TIMESTAMP NOT NULL,
            current_period_end TIMESTAMP NOT NULL,
            videos_used_this_month INTEGER DEFAULT 0,
            total_revenue_this_month DECIMAL(10,2) DEFAULT 0.0,
            revenue_share_paid DECIMAL(10,2) DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on user_id
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id)")
    
    # Create video_revenue table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_revenue (
            id VARCHAR PRIMARY KEY,
            video_id VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            source VARCHAR NOT NULL,
            currency VARCHAR DEFAULT 'USD',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_revenue_video_id ON video_revenue(video_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_revenue_user_id ON video_revenue(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_revenue_date ON video_revenue(date)")
    
    # Create digital_products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS digital_products (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            category VARCHAR NOT NULL,
            file_url VARCHAR,
            thumbnail_url VARCHAR,
            creator_id VARCHAR NOT NULL,
            sales_count INTEGER DEFAULT 0,
            total_revenue DECIMAL(10,2) DEFAULT 0.0,
            commission_rate DECIMAL(5,2) DEFAULT 0.30,
            status VARCHAR DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_digital_products_creator_id ON digital_products(creator_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_digital_products_category ON digital_products(category)")
    
    # Create affiliate_links table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS affiliate_links (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            product_id VARCHAR,
            code VARCHAR NOT NULL UNIQUE,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            total_commission DECIMAL(10,2) DEFAULT 0.0,
            status VARCHAR DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_links_user_id ON affiliate_links(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_links_code ON affiliate_links(code)")
    
    # Create affiliate_clicks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS affiliate_clicks (
            id VARCHAR PRIMARY KEY,
            affiliate_id VARCHAR NOT NULL,
            visitor_ip VARCHAR,
            user_agent TEXT,
            referrer VARCHAR,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_clicks_affiliate_id ON affiliate_clicks(affiliate_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_clicks_timestamp ON affiliate_clicks(timestamp)")
    
    # Create affiliate_conversions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS affiliate_conversions (
            id VARCHAR PRIMARY KEY,
            affiliate_id VARCHAR NOT NULL,
            sale_amount DECIMAL(10,2) NOT NULL,
            commission_amount DECIMAL(10,2) NOT NULL,
            product_id VARCHAR,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_conversions_affiliate_id ON affiliate_conversions(affiliate_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_affiliate_conversions_timestamp ON affiliate_conversions(timestamp)")
    
    # Create payment_transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            stripe_payment_intent_id VARCHAR UNIQUE,
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR DEFAULT 'USD',
            status VARCHAR NOT NULL,
            type VARCHAR NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON payment_transactions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_transactions_type ON payment_transactions(type)")
    
    # Commit changes
    conn.commit()
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%subscription%' OR name LIKE '%revenue%' OR name LIKE '%affiliate%' OR name LIKE '%payment%'")
    tables = cursor.fetchall()
    
    print(f"✅ Created {len(tables)} tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Close connection
    conn.close()
    
    print("🎉 Database migration completed successfully!")

def insert_sample_data():
    """Insert sample data for testing"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "youtube_ai.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📝 Inserting sample data...")
    
    # Insert sample pricing tiers (these would normally be in Stripe)
    sample_products = [
        ("prod_001", "YouTube Monetization Masterclass", "Complete guide to monetizing YouTube content", 99.99, "course", "creator_001"),
        ("prod_002", "AI Content Templates", "Professional templates for AI-generated content", 29.99, "template", "creator_002"),
        ("prod_003", "Analytics Dashboard Pro", "Advanced analytics and reporting tools", 49.99, "tool", "creator_003")
    ]
    
    for product in sample_products:
        cursor.execute("""
            INSERT OR IGNORE INTO digital_products 
            (id, name, description, price, category, creator_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, product)
    
    # Insert sample revenue data
    sample_revenue = [
        ("rev_001", "video_001", "user_001", 45.50, "youtube_ads"),
        ("rev_002", "video_002", "user_001", 32.75, "sponsorship"),
        ("rev_003", "video_003", "user_002", 28.90, "youtube_ads"),
        ("rev_004", "video_004", "user_002", 15.25, "affiliate")
    ]
    
    for revenue in sample_revenue:
        cursor.execute("""
            INSERT OR IGNORE INTO video_revenue 
            (id, video_id, user_id, amount, source) 
            VALUES (?, ?, ?, ?, ?)
        """, revenue)
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data inserted successfully!")

if __name__ == "__main__":
    create_subscription_tables()
    insert_sample_data() 