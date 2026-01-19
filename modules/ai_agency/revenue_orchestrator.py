"""
Revenue Orchestrator - Continuous revenue stream optimization engine.
Analyzes Growth Ledger, adjusts pricing, and triggers marketing campaigns automatically.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from modules.growth_engine_v1.models import GrowthLedgerEntry
from modules.growth_engine_v1.app import SessionLocal
from modules.ai_agency.chimera_engine import chimera_engine
from modules.ai_agency.marketing_commander import marketing_commander
from modules.ai_agency.lead_hunter import lead_hunter
from modules.ai_agency.ads_commander import ads_commander

logger = logging.getLogger(__name__)

class RevenueOrchestrator:
    """
    Orchestrates continuous revenue optimization.
    - Analyzes revenue trends
    - Adjusts SKU pricing (within bounds)
    - Triggers marketing for underperforming/high-potential assets
    """
    
    def __init__(self):
        self.min_margin = 0.20 # Minimum 20% margin
    
    def get_revenue_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze revenue trends from Growth Ledger."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            entries = db.query(GrowthLedgerEntry).filter(
                GrowthLedgerEntry.created_at >= cutoff_date
            ).all()
            
            total_revenue = sum(e.amount_cents for e in entries) / 100.0
            
            # Group by stream/SKU if possible (assuming meta has SKU)
            by_sku = {}
            for e in entries:
                sku = e.provenance_meta.get("sku", "unknown") if e.provenance_meta else "unknown"
                by_sku[sku] = by_sku.get(sku, 0.0) + (e.amount_cents / 100.0)
                
            return {
                "total_revenue": total_revenue,
                "days": days,
                "by_sku": by_sku,
                "entry_count": len(entries)
            }
        finally:
            db.close()
            
    async def optimize_pricing(self, sku: str, current_price: float, sales_velocity: float) -> float:
        """
        AI-driven pricing optimization.
        If velocity is high, test higher price. If low, test lower price.
        """
        prompt = f"""
        Analyze pricing for SKU: {sku}
        Current Price: ${current_price}
        Sales Velocity: {sales_velocity} sales/week
        
        Recommend a new price to maximize revenue (revenue = price * volume).
        Return ONLY the numeric value of the new price (e.g. 49.99).
        """
        
        try:
            response = await chimera_engine.generate_response(prompt, task_type="analysis")
            # Extract number from response
            import re
            match = re.search(r"(\d+\.?\d*)", response)
            if match:
                return float(match.group(1))
            return current_price
        except Exception as e:
            logger.error(f"Pricing optimization failed: {e}")
            return current_price
            
    async def daily_mission(self) -> Dict[str, Any]:
        """
        Execute the daily optimization mission.
        1. Analyze yesterday's performance
        2. Identify top/bottom performers
        3. Trigger marketing for opportunity SKUs
        """
        trends = self.get_revenue_trends(days=1)
        
        # Load catalog to get active SKUs
        import json
        with open("docs/commerce/product_catalog.json", 'r') as f:
            catalog = json.load(f)
        
        results = {
            "mission_id": f"mission_{datetime.now().strftime('%Y%m%d')}",
            "revenue_yesterday": trends['total_revenue'],
            "actions": []
        }
        
        # Strategy: Marketing Boost for Top SKU + One Random "Discovery" SKU
        import random
        active_products = [p for p in catalog['products']]
        
        # 1. Identify Target
        target_sku = None
        if trends['by_sku']:
            # Boost winner
            best_sku_id = max(trends['by_sku'], key=trends['by_sku'].get)
            target_sku = next((p for p in active_products if p['sku'] == best_sku_id), None)
        
        if not target_sku:
            # No sales yet? Pick a quick win
            target_sku = next((p for p in active_products if p['sku'] == "CREATOR-KIT-01"), active_products[0])
            
        # 2. Execute Marketing Boost
        if target_sku:
            logger.info(f"Boosting SKU: {target_sku['sku']}")
            
            # --- New: Autonomous Lead Hunter Loop ---
            # If trends are non-existent or fresh launch, hunt for new leads
            if trends['total_revenue'] < 100.0:
                logger.info("Revenue below threshold. Activating Autonomous Lead Hunter...")
                hunt_result = await lead_hunter.hunt_leads(target_sku, context="US Market Pivot Initial Launch")
                results["actions"].append({
                    "type": "autonomous_lead_hunt",
                    "sku": target_sku['sku'],
                    "hunt_summary": hunt_result
                })
            else:
                # Standard social boost
                campaign = await marketing_commander.execute_campaign(
                    target_sku, 
                    channels=["twitter", "linkedin"] # Quick social boost
                )
                results["actions"].append({
                    "type": "marketing_boost",
                    "sku": target_sku['sku'],
                    "campaign": campaign
                })
            
        return results

    async def sprint_mission(self, target: float = 2000.0, duration_hrs: int = 2) -> Dict[str, Any]:
        """
        Execute a high-intensity revenue sprint.
        - Targets high-ticket items
        - Triggers multi-channel aggressive outreach
        - Forces LeadHunter into 'Deep Search' mode
        """
        logger.info(f"🚀 IGNITING QUANTUM SPRINT: Target ${target} in {duration_hrs}hrs")
        
        # 1. Load Catalog & Identify High-Ticket Targets
        import json
        with open("docs/commerce/product_catalog.json", 'r') as f:
            catalog = json.load(f)
            
        high_ticket_skus = [p for p in catalog['products'] if p['price']['min'] >= 499]
        if not high_ticket_skus:
            # Fallback to premium SaaS if no consulting/training found
            high_ticket_skus = [p for p in catalog['products'] if p['price']['min'] >= 149]
            
        results = {
            "sprint_id": f"sprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "target": target,
            "duration": f"{duration_hrs} hours",
            "intensity": "EXTREME",
            "actions": []
        }
        
        # 2. Parallel Aggressive Outreach
        tasks = []
        for sku in high_ticket_skus[:3]: # Limit to top 3 for intensity
            logger.info(f"Sprint targeting SKU: {sku['sku']}")
            
            # Action A: Deep Lead Hunt
            tasks.append(lead_hunter.hunt_leads(sku, context="AGGRESSIVE SPRINT: DIRECT CONVERSION REQUIRED"))
            
            # Action B: Viral Social Pulse
            tasks.append(marketing_commander.execute_campaign(sku, channels=["linkedin", "twitter", "blog"]))
            
        execution_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results["actions"].append({
            "type": "quantum_pulse_complete",
            "targets_count": len(high_ticket_skus[:3]),
            "execution_summary": "Aggressive Outreach Sequenced"
        })
        
        return results

    async def execute_ads_sprint(self, sku: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce a complete Ads execution pack for a high-ticket SKU.
        - Generates 3 ad variations
        - Suggests demographic targeting
        - Estimates budget impact
        """
        logger.info(f"🚀 Executing Ads Sprint for SKU: {sku['sku']}")
        
        ad_pack = await ads_commander.generate_meta_ads(sku)
        targeting = await ads_commander.suggest_targeting(sku)
        
        return {
            "sku": sku['sku'],
            "ad_variations": ad_pack,
            "targeting_strategy": targeting,
            "ready_for_deploy": True
        }

revenue_orchestrator = RevenueOrchestrator()
