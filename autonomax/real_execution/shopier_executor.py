"""
Shopier Real Executor - Push products and manage orders on Shopier
"""

import os
import json
import logging
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProductListing:
    """Product to be listed on Shopier"""
    sku: str
    title: str
    description: str
    price: float
    currency: str = "USD"
    product_type: str = "digital"
    stock: int = 9999
    category_id: int = 1
    is_active: bool = True
    images: List[str] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []


class ShopierExecutor:
    """
    Real executor for Shopier operations.
    Pushes products, manages orders, and handles webhooks.
    """
    
    BASE_URL = "https://api.shopier.com/v1"
    
    def __init__(self):
        self.access_token = os.getenv("SHOPIER_PERSONAL_ACCESS_TOKEN") or os.getenv("PAYMENT_SHOPIER_PERSONAL_ACCESS_TOKEN")
        self.api_key = os.getenv("SHOPIER_API_KEY") or os.getenv("PAYMENT_SHOPIER_API_KEY")
        self.api_secret = os.getenv("SHOPIER_API_SECRET") or os.getenv("PAYMENT_SHOPIER_API_SECRET")
        
        if not self.access_token:
            logger.warning("Shopier access token not found")
        
        self.execution_log: List[Dict] = []
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make authenticated request to Shopier API"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._headers(),
                json=data,
                params=params,
                timeout=30
            )
            
            self._log_execution(method, endpoint, response.status_code, response.text[:500])
            
            if response.status_code >= 400:
                logger.error(f"Shopier API error: {response.status_code} - {response.text}")
                return {"error": response.text, "status_code": response.status_code}
            
            return response.json() if response.text else {"success": True}
            
        except Exception as e:
            logger.error(f"Shopier request failed: {e}")
            return {"error": str(e)}
    
    def _log_execution(self, method: str, endpoint: str, status: int, response: str):
        """Log execution for audit trail"""
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "endpoint": endpoint,
            "status": status,
            "response_preview": response[:200],
        })
    
    def list_products(self) -> List[Dict]:
        """Get all products from Shopier store"""
        result = self._request("GET", "/products")
        if "error" in result:
            return []
        return result.get("data", [])
    
    def create_product(self, product: ProductListing) -> Dict:
        """Create a new product on Shopier"""
        payload = {
            "title": product.title,
            "description": product.description,
            "priceData": {
                "price": str(product.price),
                "currency": product.currency,
            },
            "type": product.product_type,
            "stock": product.stock,
            "category_id": product.category_id,
            "is_active": product.is_active,
            "shippingPayer": "sellerPays",
        }
        
        if product.images:
            payload["media"] = [{"url": img} for img in product.images]
        
        logger.info(f"Creating Shopier product: {product.title}")
        result = self._request("POST", "/products", data=payload)
        
        if "error" not in result:
            logger.info(f"Successfully created product: {product.sku}")
        
        return result
    
    def update_product(self, product_id: str, updates: Dict) -> Dict:
        """Update an existing product"""
        return self._request("PATCH", f"/products/{product_id}", data=updates)
    
    def get_orders(self, status: str = None, limit: int = 50) -> List[Dict]:
        """Get orders from Shopier"""
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = self._request("GET", "/orders", params=params)
        return result.get("data", []) if "error" not in result else []
    
    def get_shop_info(self) -> Dict:
        """Get shop information"""
        return self._request("GET", "/shop")
    
    def push_catalog(self, products: List[ProductListing]) -> Dict[str, Any]:
        """Push multiple products to Shopier"""
        results = {
            "success": [],
            "failed": [],
            "total": len(products),
        }
        
        for product in products:
            result = self.create_product(product)
            if "error" in result:
                results["failed"].append({
                    "sku": product.sku,
                    "error": result.get("error"),
                })
            else:
                results["success"].append({
                    "sku": product.sku,
                    "shopier_id": result.get("id"),
                })
        
        logger.info(f"Catalog push complete: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    def get_execution_log(self) -> List[Dict]:
        """Get execution audit log"""
        return self.execution_log


# Pre-built product catalog for immediate deployment
AUTONOMAX_CATALOG = [
    ProductListing(
        sku="ZEN-ART-BASE",
        title="Zen Art Printables Bundle - 50+ Minimalist Designs",
        description="""Transform any space into a sanctuary of calm with our curated collection of 50+ minimalist zen art prints.

WHAT'S INCLUDED:
• 50+ unique designs across 5 collections
• Multiple sizes: 8x10, 11x14, 16x20, 24x36, A4, A3
• High-resolution files (300 DPI) ready for print
• Room mockups to visualize in your space
• Print guide with recommended paper and framing tips

COLLECTIONS:
1. Cosmic Harmony - Celestial and night sky themes
2. Nature's Serenity - Mountains, forests, and water
3. Mandala Magic - Intricate geometric patterns
4. Minimalist Zen - Simple lines and shapes
5. Abstract Calm - Modern artistic expressions

PERFECT FOR:
✓ Home office walls that inspire focus
✓ Living rooms needing a calming touch
✓ Bedrooms designed for peaceful sleep
✓ Gift-giving for design-conscious friends

INSTANT DIGITAL DOWNLOAD - Start decorating today!""",
        price=29.00,
        currency="USD",
        product_type="digital",
    ),
    ProductListing(
        sku="CREATOR-KIT-01",
        title="Creator Starter Kit - Launch Your Digital Product This Week",
        description="""Everything you need to launch your first digital product. From idea to income in 7 days.

WHAT'S INCLUDED:

📦 LAUNCH TEMPLATES
• Product page template (Shopify, Etsy, Gumroad)
• Sales page wireframe
• Pricing calculator spreadsheet
• Email announcement templates

📋 PLAYBOOKS
• 7-Day Launch Playbook
• Platform Selection Guide
• Pricing Psychology Guide
• First 100 Customers Playbook

✅ CHECKLISTS
• Pre-launch checklist (47 items)
• Launch day checklist
• Post-launch optimization
• Legal/compliance checklist

🎨 DESIGN ASSETS
• Canva templates for mockups
• Social media announcement graphics
• Email header designs
• Thank you page templates

PERFECT FOR:
✓ First-time digital product creators
✓ Course creators launching their first course
✓ Artists selling digital downloads
✓ Consultants productizing expertise

INSTANT ACCESS - Start building today!""",
        price=49.00,
        currency="USD",
        product_type="digital",
    ),
    ProductListing(
        sku="MASTERY-PACK-ULTIMATE",
        title="AutonomaX Mastery Pack - Complete Automation Bundle ($2,847 Value)",
        description="""Your complete system for building automated income streams. Everything in one bundle.

TOTAL VALUE: $2,847
YOUR PRICE: $497
YOU SAVE: 83%

WHAT'S INCLUDED:

🎨 COMPLETE ART COLLECTIONS ($199 value)
• All 50+ Zen Art designs
• Commercial license included
• Room mockups for listings

🚀 CREATOR LAUNCH SYSTEM ($199 value)
• Creator Starter Kit
• Platform-specific playbooks
• Launch templates for every channel

⚙️ AUTOMATION VAULT ($299 value)
• 50+ SOPs for digital businesses
• Zapier automation templates
• Customer service workflows

📊 REVENUE INTELLIGENCE ($499 value)
• Market research templates
• Pricing optimization tools
• Analytics dashboards

🎯 PLATFORM PLAYBOOKS ($299 value)
• Shopify Domination Guide
• Etsy Optimization System
• Fiverr Gig Launch Kit
• YouTube Automation Studio

📱 COMMAND CENTER ($149 value)
• Notion Revenue Dashboard
• Content Planner & Client CRM

🎁 BONUSES ($297 value)
• Private Discord Community
• Weekly Q&A Calls (4 weeks)
• 100+ AI Prompts
• Lifetime Updates

30-DAY MONEY-BACK GUARANTEE

Build your automated income empire starting today!""",
        price=497.00,
        currency="USD",
        product_type="digital",
    ),
    ProductListing(
        sku="YT-AUTO-DIY",
        title="YouTube Automation Studio - Scale Your Channel Without Scaling Hours",
        description="""The complete system to produce YouTube content at scale - without burning out.

WHAT'S INCLUDED:

📋 STRATEGY PACKAGE
• Channel positioning framework
• Content pillar mapping
• Audience research templates
• Competitor analysis tools

✍️ SCRIPT SYSTEM
• Hook formulas that retain viewers
• Script templates by video type
• Call-to-action frameworks
• AI prompt library for script drafts

🖼️ THUMBNAIL FACTORY
• Thumbnail templates (Canva/Figma)
• Color psychology guide
• A/B testing framework
• CTR optimization checklist

📅 PUBLISHING WORKFLOW
• Content calendar template
• Upload optimization checklist
• Description/tag templates
• End screen strategies

📊 ANALYTICS & OPTIMIZATION
• Performance tracking dashboard
• Revenue calculation tools
• Growth projection models

PERFECT FOR:
✓ YouTubers stuck at 1-2 videos/month
✓ Brands building YouTube presence
✓ Agencies managing client channels
✓ Educators creating course content

Go from 1 video/month to 1/day with systems that work!""",
        price=299.00,
        currency="USD",
        product_type="digital",
    ),
    ProductListing(
        sku="NOTION-DASHBOARD",
        title="Notion Passive Income Dashboard - All Revenue Streams in One View",
        description="""Finally, complete visibility into your digital business. One workspace. One source of truth.

WHAT'S INCLUDED:

📊 REVENUE DASHBOARD
• Multi-source income tracking
• Monthly/quarterly/annual views
• Goal progress visualization
• Revenue by product/channel

📦 PRODUCT DATABASE
• Complete catalog management
• Pricing history
• Performance metrics
• Stock/variant tracking

📅 CONTENT PLANNER
• Editorial calendar
• Multi-platform scheduling
• Content status tracking
• Idea capture system

👥 CLIENT CRM
• Customer database
• Order history
• Communication log
• Follow-up reminders

✅ TASK MANAGEMENT
• Kanban boards
• Priority system
• Recurring tasks
• Team collaboration ready

SETUP TIME: ~30 minutes
VIDEO GUIDE: Included
UPDATES: Lifetime

Stop the spreadsheet chaos. See exactly where your money comes from.""",
        price=29.00,
        currency="USD",
        product_type="digital",
    ),
    ProductListing(
        sku="HYBRID-STACK",
        title="Hybrid Passive Income Stack - Build Income Without Quitting Your Day Job",
        description="""The system designed for people who can't work 40 hours/week on their side business.

Works in the margins - early mornings, lunch breaks, weekends.

WHAT'S INCLUDED:

📚 THE HYBRID PLAYBOOK
• 30/60/90 day launch plan
• Time-boxing strategies
• Energy management for side projects
• Milestone checkpoints

🎯 PRODUCT SELECTION GUIDE
• Best products for limited time
• Effort vs. reward matrix
• Your first product decision tree
• Niche validation framework

⚙️ AUTOMATION TEMPLATES
• Set-and-forget workflows
• Auto-delivery systems
• Social posting automation
• Email sequences

📊 TRACKING DASHBOARD
• Time investment tracking
• ROI calculator
• Goal progress
• Weekly review template

PERFECT FOR:
✓ Full-time employees building side income
✓ Parents with limited hours
✓ Anyone who says "I don't have time"
✓ People who want income, not another job

TIME REQUIRED: 2-5 hours/week
SETUP TIME: 1 weekend""",
        price=99.00,
        currency="USD",
        product_type="digital",
    ),
]


def execute_shopier_deployment() -> Dict[str, Any]:
    """
    Execute real Shopier deployment with the product catalog.
    Returns deployment results.
    """
    executor = ShopierExecutor()
    
    # Check connection first
    shop_info = executor.get_shop_info()
    if "error" in shop_info:
        return {
            "status": "failed",
            "error": "Could not connect to Shopier API",
            "details": shop_info,
        }
    
    # Get existing products to avoid duplicates
    existing = executor.list_products()
    existing_titles = {p.get("title", "").lower() for p in existing}
    
    # Filter out products that already exist
    new_products = [
        p for p in AUTONOMAX_CATALOG
        if p.title.lower() not in existing_titles
    ]
    
    if not new_products:
        return {
            "status": "skipped",
            "message": "All products already exist in Shopier",
            "existing_count": len(existing),
        }
    
    # Push new products
    results = executor.push_catalog(new_products)
    
    return {
        "status": "completed",
        "shop_info": shop_info,
        "deployment_results": results,
        "execution_log": executor.get_execution_log(),
    }
