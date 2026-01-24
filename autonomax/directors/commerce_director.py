"""
Commerce Director - Owns revenue generation, pricing, channels, conversions
Reports to Commander with revenue and sales KPIs
"""

import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .base_director import BaseDirector, DirectorTask


class CommerceDirector(BaseDirector):
    """
    Director of Commerce & Revenue
    
    Responsibilities:
    - Product pricing and bundling
    - Sales channel management (Shopier, Etsy, Gumroad, etc.)
    - Conversion optimization
    - Revenue tracking and forecasting
    - Promotional campaigns
    
    KPIs:
    - Monthly Recurring Revenue (MRR)
    - Average Order Value (AOV)
    - Conversion Rate
    - Products Live
    - Sales per Channel
    """
    
    SALES_CHANNELS = {
        "shopier": {
            "name": "Shopier",
            "type": "primary",
            "url": "https://www.shopier.com/",
            "api_available": True,
            "currency": "TRY",
        },
        "etsy": {
            "name": "Etsy",
            "type": "expansion",
            "url": "https://www.etsy.com/",
            "api_available": True,
            "currency": "USD",
        },
        "gumroad": {
            "name": "Gumroad",
            "type": "expansion",
            "url": "https://gumroad.com/",
            "api_available": True,
            "currency": "USD",
        },
        "fiverr": {
            "name": "Fiverr",
            "type": "services",
            "url": "https://www.fiverr.com/",
            "api_available": False,
            "currency": "USD",
        },
    }
    
    PRODUCT_CATALOG = {
        "ZEN-ART-BASE": {"name": "Zen Art Base Collection", "price_usd": 29, "type": "digital"},
        "CREATOR-KIT": {"name": "Creator Starter Kit", "price_usd": 49, "type": "digital"},
        "MASTERY-PACK": {"name": "AutonomaX Mastery Pack", "price_usd": 497, "type": "bundle"},
        "YT-AUTO-DIY": {"name": "YouTube Automation DIY", "price_usd": 299, "type": "course"},
        "NOTION-DASHBOARD": {"name": "Notion Revenue Dashboard", "price_usd": 29, "type": "template"},
        "HYBRID-STACK": {"name": "Hybrid Passive Income Stack", "price_usd": 99, "type": "playbook"},
        "SOP-VAULT": {"name": "Automation SOP Vault", "price_usd": 149, "type": "digital"},
        "FIVERR-KIT": {"name": "Fiverr AI Services Kit", "price_usd": 79, "type": "digital"},
        "CONSULTING-HOUR": {"name": "1:1 Consulting (1 hour)", "price_usd": 199, "type": "service"},
        "CONSULTING-RETAINER": {"name": "Monthly Consulting Retainer", "price_usd": 1499, "type": "service"},
    }
    
    def __init__(self):
        super().__init__(
            name="Director of Commerce & Revenue",
            domain="commerce"
        )
        self.sales_data: List[Dict] = []
        self.active_campaigns: List[Dict] = []
        self.channel_performance: Dict[str, Dict] = {}
    
    def _initialize_kpis(self):
        """Initialize commerce-specific KPIs"""
        # Revenue KPIs
        self.kpis.add_metric("monthly_revenue", target=5000, unit="USD", period="monthly")
        self.kpis.add_metric("weekly_revenue", target=1250, unit="USD", period="weekly")
        self.kpis.add_metric("daily_revenue", target=180, unit="USD", period="daily")
        
        # Sales KPIs
        self.kpis.add_metric("orders_per_week", target=20, unit="orders", period="weekly")
        self.kpis.add_metric("aov", target=75, unit="USD", period="monthly")
        self.kpis.add_metric("conversion_rate", target=3.0, unit="%", period="monthly")
        
        # Product KPIs
        self.kpis.add_metric("products_live", target=15, unit="products", period="monthly")
        self.kpis.add_metric("channels_active", target=3, unit="channels", period="monthly")
        
        # Growth KPIs
        self.kpis.add_metric("new_customers", target=50, unit="customers", period="monthly")
        self.kpis.add_metric("repeat_purchase_rate", target=15, unit="%", period="monthly")
    
    def execute_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Execute commerce-specific tasks"""
        task_type = task.title.lower()
        
        if "price" in task_type or "pricing" in task_type:
            return self._optimize_pricing(task)
        
        elif "campaign" in task_type or "sale" in task_type or "promo" in task_type:
            return self._launch_campaign(task)
        
        elif "channel" in task_type or "expand" in task_type:
            return self._expand_channel(task)
        
        elif "bundle" in task_type:
            return self._create_bundle(task)
        
        elif "revenue" in task_type or "report" in task_type:
            return self._generate_revenue_report(task)
        
        else:
            return self._generic_commerce_task(task)
    
    def _optimize_pricing(self, task: DirectorTask) -> Dict[str, Any]:
        """Optimize product pricing based on data"""
        recommendations = []
        
        for sku, product in self.PRODUCT_CATALOG.items():
            current_price = product["price_usd"]
            
            # Pricing optimization logic
            if product["type"] == "bundle":
                # Bundles should be 3-5x entry products
                recommendations.append({
                    "sku": sku,
                    "current_price": current_price,
                    "strategy": "anchor_high",
                    "recommendation": "Maintain premium pricing, emphasize value stack",
                })
            elif product["type"] == "digital" and current_price < 50:
                # Entry products - optimize for conversion
                recommendations.append({
                    "sku": sku,
                    "current_price": current_price,
                    "strategy": "conversion_focus",
                    "recommendation": "Test $X9 pricing (e.g., $29, $39)",
                })
            elif product["type"] == "service":
                # Services - premium positioning
                recommendations.append({
                    "sku": sku,
                    "current_price": current_price,
                    "strategy": "value_based",
                    "recommendation": "Price based on outcome value, not time",
                })
        
        return {
            "action": "pricing_optimization",
            "products_analyzed": len(self.PRODUCT_CATALOG),
            "recommendations": recommendations,
        }
    
    def _launch_campaign(self, task: DirectorTask) -> Dict[str, Any]:
        """Launch a promotional campaign"""
        campaign_type = "flash_sale" if "flash" in task.description.lower() else "standard"
        
        campaign = {
            "id": f"CAMP_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "name": task.title,
            "type": campaign_type,
            "discount_percent": 20 if campaign_type == "flash_sale" else 10,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=2 if campaign_type == "flash_sale" else 7)).isoformat(),
            "products": list(self.PRODUCT_CATALOG.keys())[:5],
            "channels": ["shopier"],
            "status": "active",
        }
        
        self.active_campaigns.append(campaign)
        
        # Generate campaign content
        content = self._generate_campaign_content(campaign)
        
        return {
            "action": "campaign_launched",
            "campaign": campaign,
            "content": content,
            "expected_revenue_boost": f"{campaign['discount_percent'] * 2}%",
        }
    
    def _generate_campaign_content(self, campaign: Dict) -> Dict[str, str]:
        """Generate marketing content for campaign"""
        if campaign["type"] == "flash_sale":
            return {
                "headline": f"⚡ {campaign['discount_percent']}% OFF - 48 Hours Only!",
                "email_subject": f"🔥 Flash Sale: {campaign['discount_percent']}% off everything (ends tomorrow)",
                "social_post": f"⚡ FLASH SALE ⚡\n\n{campaign['discount_percent']}% off all digital products.\n\n48 hours only.\n\nNo code needed - prices already slashed.\n\n🔗 Link in bio",
                "urgency_message": "Sale ends in 48 hours. No extensions.",
            }
        else:
            return {
                "headline": f"Special Offer: {campaign['discount_percent']}% Off",
                "email_subject": f"Your exclusive {campaign['discount_percent']}% discount inside",
                "social_post": f"📦 Special offer this week\n\n{campaign['discount_percent']}% off selected products.\n\nPerfect time to start your automation journey.",
            }
    
    def _expand_channel(self, task: DirectorTask) -> Dict[str, Any]:
        """Expand to a new sales channel"""
        channel_name = task.description.lower()
        
        # Find matching channel
        channel = None
        for key, ch in self.SALES_CHANNELS.items():
            if key in channel_name or ch["name"].lower() in channel_name:
                channel = ch
                channel["key"] = key
                break
        
        if not channel:
            return {"action": "channel_not_found", "query": channel_name}
        
        # Generate expansion plan
        expansion_plan = {
            "channel": channel["name"],
            "type": channel["type"],
            "steps": [
                f"Create seller account on {channel['name']}",
                "Adapt product listings for platform requirements",
                "Set up payment/payout configuration",
                "Upload first 5 products",
                "Configure auto-delivery (if supported)",
                "Set up analytics tracking",
            ],
            "products_to_list": [
                sku for sku, p in self.PRODUCT_CATALOG.items()
                if p["type"] in ["digital", "template", "playbook"]
            ][:5],
            "estimated_time": "2-4 hours",
            "api_integration": channel["api_available"],
        }
        
        self.kpis.increment_metric("channels_active", 1)
        
        return {
            "action": "channel_expansion_planned",
            "plan": expansion_plan,
        }
    
    def _create_bundle(self, task: DirectorTask) -> Dict[str, Any]:
        """Create a product bundle"""
        # Default bundle configuration
        bundle = {
            "name": task.title,
            "sku": f"BUNDLE-{datetime.utcnow().strftime('%Y%m%d')}",
            "components": ["ZEN-ART-BASE", "CREATOR-KIT", "NOTION-DASHBOARD"],
            "individual_value": sum(
                self.PRODUCT_CATALOG[sku]["price_usd"]
                for sku in ["ZEN-ART-BASE", "CREATOR-KIT", "NOTION-DASHBOARD"]
            ),
            "bundle_price": 79,  # Discounted
            "savings_percent": 0,
        }
        bundle["savings_percent"] = round(
            (1 - bundle["bundle_price"] / bundle["individual_value"]) * 100
        )
        
        return {
            "action": "bundle_created",
            "bundle": bundle,
            "positioning": f"Save {bundle['savings_percent']}% with this bundle",
        }
    
    def _generate_revenue_report(self, task: DirectorTask) -> Dict[str, Any]:
        """Generate revenue report"""
        # This would pull from actual sales data
        report = {
            "period": "current_month",
            "total_revenue": self.kpis.metrics.get("monthly_revenue", {}).current if "monthly_revenue" in self.kpis.metrics else 0,
            "orders": self.kpis.metrics.get("orders_per_week", {}).current if "orders_per_week" in self.kpis.metrics else 0,
            "aov": self.kpis.metrics.get("aov", {}).current if "aov" in self.kpis.metrics else 0,
            "top_products": [],
            "channel_breakdown": self.channel_performance,
            "kpi_status": self.kpis.get_summary(),
        }
        
        return {
            "action": "revenue_report_generated",
            "report": report,
        }
    
    def _generic_commerce_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Handle generic commerce tasks"""
        return {
            "action": "task_acknowledged",
            "task": task.title,
            "status": "queued_for_review",
        }
    
    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """Get prioritized actions to improve commerce KPIs"""
        actions = []
        at_risk = self.kpis.get_at_risk()
        
        if "daily_revenue" in at_risk or "weekly_revenue" in at_risk:
            actions.append({
                "action": "flash_sale",
                "target": "Launch 48-hour flash sale on top 3 products",
                "priority": 1,
                "kpi_impact": ["daily_revenue", "weekly_revenue", "orders_per_week"],
                "expected_lift": "+30% revenue for 48h",
            })
        
        if "conversion_rate" in at_risk:
            actions.append({
                "action": "optimize_listings",
                "target": "A/B test product titles and descriptions",
                "priority": 2,
                "kpi_impact": ["conversion_rate", "orders_per_week"],
            })
        
        if "products_live" in at_risk:
            actions.append({
                "action": "expand_catalog",
                "target": "Add 5 new products from template library",
                "priority": 2,
                "kpi_impact": ["products_live", "monthly_revenue"],
            })
        
        if "channels_active" in at_risk:
            actions.append({
                "action": "channel_expansion",
                "target": "Launch on Etsy or Gumroad",
                "priority": 3,
                "kpi_impact": ["channels_active", "monthly_revenue"],
            })
        
        if "aov" in at_risk:
            actions.append({
                "action": "upsell_implementation",
                "target": "Add order bump and upsell flow",
                "priority": 2,
                "kpi_impact": ["aov", "monthly_revenue"],
            })
        
        # Always have baseline revenue actions
        if not actions:
            actions = [
                {"action": "review_pricing", "target": "Audit pricing vs competition", "priority": 3},
                {"action": "email_campaign", "target": "Send promotional email to list", "priority": 2},
                {"action": "social_proof", "target": "Request 5 customer reviews", "priority": 3},
            ]
        
        return sorted(actions, key=lambda x: x.get("priority", 5))
    
    def record_sale(self, order_id: str, amount: float, channel: str, products: List[str]):
        """Record a sale and update KPIs"""
        sale = {
            "order_id": order_id,
            "amount": amount,
            "channel": channel,
            "products": products,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.sales_data.append(sale)
        
        # Update KPIs
        self.kpis.increment_metric("daily_revenue", amount)
        self.kpis.increment_metric("weekly_revenue", amount)
        self.kpis.increment_metric("monthly_revenue", amount)
        self.kpis.increment_metric("orders_per_week", 1)
        self.kpis.increment_metric("new_customers", 1)
        
        # Update channel performance
        if channel not in self.channel_performance:
            self.channel_performance[channel] = {"revenue": 0, "orders": 0}
        self.channel_performance[channel]["revenue"] += amount
        self.channel_performance[channel]["orders"] += 1
        
        self.log_execution("sale_recorded", sale)
        return sale
    
    def get_revenue_forecast(self, days: int = 30) -> Dict[str, Any]:
        """Forecast revenue based on current trajectory"""
        current_daily = self.kpis.metrics.get("daily_revenue")
        if current_daily:
            avg_daily = current_daily.current / max(1, datetime.utcnow().day)
        else:
            avg_daily = 0
        
        return {
            "forecast_period_days": days,
            "avg_daily_revenue": avg_daily,
            "projected_revenue": avg_daily * days,
            "target": self.kpis.metrics.get("monthly_revenue", {}).target if "monthly_revenue" in self.kpis.metrics else 5000,
            "on_track": avg_daily * 30 >= (self.kpis.metrics.get("monthly_revenue", {}).target if "monthly_revenue" in self.kpis.metrics else 5000),
        }
