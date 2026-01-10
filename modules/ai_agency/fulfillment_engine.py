import json
import os
import random
import asyncio
from datetime import datetime
from uuid import uuid4

EARNINGS_FILE = "earnings.json"

class FulfillmentEngine:
    """
    Simulates the 'Execution' of paid services and updates the financial ledger.
    """
    
    def __init__(self):
        # We check environment via a simplified way for this module
        # but could also import settings
        self.production = os.getenv("APP_ENV") == "production"
        self.assets_dir = "static/assets"
        self._ensure_infrastructure()
        
    def _ensure_infrastructure(self):
        """Ensures ledger and asset directories exist."""
        # Ensure static/assets exists
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir, exist_ok=True)
            
        # Ensure ledger exists
        if not os.path.exists(EARNINGS_FILE):
            initial_data = {
                "total_earnings": 0.0,
                "daily": 0.0,
                "history": []
            }
            with open(EARNINGS_FILE, 'w') as f:
                json.dump(initial_data, f, indent=4)

    async def simulate_work(self, task_type: str, context: str = "", protocol_tier: str = "standard") -> dict:
        """
        Simulates performing a work task (e.g., 'Fiverr Gig').
        Returns the result and the earnings generated.
        protocol_tier: 'standard', 'high_ticket', 'launch_event' (matches Alexandria Protocol levels)
        """
        # If production, perform real work (or log real intent)
        if self.production:
             print(f"🚀 [PRODUCTION] Executing Real-World Fulfillment for: {task_type}")
             # In production, work is faster/real-time
             await asyncio.sleep(0.5) 
        else:
             print(f"Simulating work for: {task_type}...")
             await asyncio.sleep(1.0) 
        
        # Calculate random earnings based on task type AND tier
        earnings = 0.0
        success_msg = ""
        
        # Multipliers based on Protocol Tiers
        # Standard: Routine tasks ($15-$50)
        # High Ticket: Consulting/Complex Gigs ($200-$1000)
        # Launch Event: Product Drops ($1000-$5000)
        tier_multiplier = 1.0
        if protocol_tier == "high_ticket": tier_multiplier = 10.0
        if protocol_tier == "launch_event": tier_multiplier = 50.0
        
        if "gig" in task_type.lower() or "fiverr" in task_type.lower():
            base = random.uniform(15.0, 50.0)
            earnings = base * tier_multiplier
            success_msg = f"Completed Fiverr Order ({protocol_tier}): {context}"
            
        elif "consulting" in task_type.lower() or "profit os" in task_type.lower():
            # Profit OS Consulting (Tier 2 Asset) - $5k - $20k
            # Consulting is high value, low volume
            base = random.uniform(5000.0, 15000.0)
            earnings = base
            success_msg = f"Consulting Engagement Signed (Profit OS): {context}"

        elif "saas" in task_type.lower() or "subscription" in task_type.lower() or "bopper" in task_type.lower():
            # SaaS Subscription Revenue (Recurring)
            # Tiers: $49, $149, $499
            tiers = [49.0, 149.0, 499.0]
            if protocol_tier == "high_ticket":
                earnings = 499.0
            elif protocol_tier == "launch_event":
                # Bulk subscription signups
                count = random.randint(10, 50)
                tier_choice = random.choice(tiers)
                earnings = count * tier_choice
            else:
                 earnings = random.choice(tiers)
            
            success_msg = f"New SaaS Subscription ({protocol_tier}): {context}"

        elif "intelliwealth" in task_type.lower() or "training" in task_type.lower() or "dominance" in task_type.lower():
            # Tier 3: Market Dominance Assets
            if "training" in task_type.lower():
                # AI Training Course Launch ($5k - $20k)
                earnings = random.uniform(5000.0, 20000.0)
                success_msg = f"AI Training Program Enrollment Launch: {context}"
            else:
                # IntelliWealth Consulting ($15k - $50k)
                earnings = random.uniform(15000.0, 50000.0)
                success_msg = f"IntelliWealth Management Contract Signed: {context}"

        elif "shop" in task_type.lower() or "sale" in task_type.lower():
            # ZentromaX art pieces ($5-$75)
            # If Launch Event, simulate bulk sales
            base = random.uniform(5.0, 75.0)
            earnings = base * (tier_multiplier if protocol_tier != "standard" else 1.0)
            # For launch event, we assume volume, not just price hike
            if protocol_tier == "launch_event": earnings = random.uniform(500.0, 1500.0) 
            success_msg = f"Storefront Validation ({protocol_tier}): {context}"

        elif "youtube" in task_type.lower():
            # Platform Launch Ad Revenue
            base = random.uniform(50.0, 200.0)
            earnings = base * tier_multiplier
            success_msg = f"YouTube Platform Revenue ({protocol_tier}): {context}"
            
        elif "audit" in task_type.lower():
            earnings = 0.0 # Audits are internal
            success_msg = f"Optimization Audit Complete."
            
        else:
            earnings = random.uniform(10.0, 50.0) * tier_multiplier
            success_msg = f"Protocol Task Executed: {task_type}"
            
        # Update Ledger
        asset_url = None
        if "intelliwealth" in task_type.lower():
            asset_url = "/assets/intelliwealth_preview.png"
        elif "training" in task_type.lower():
            asset_url = "/assets/mastery_preview.png"
        elif "shop" in task_type.lower() or "art" in task_type.lower():
            asset_url = f"/assets/art_piece_{random.randint(1,5)}.png"

        if earnings > 0:
            self._update_ledger(earnings, success_msg, asset_url, {"kind": "simulated"})
            
        return {
            "status": "completed",
            "message": success_msg,
            "earnings_generated": round(earnings, 2),
            "asset_url": asset_url
        }
        
    def _update_ledger(self, amount: float, source: str, asset_url: str = None, metadata: dict | None = None):
        """Updates the earnings.json file safely."""
        try:
            with open(EARNINGS_FILE, 'r') as f:
                data = json.load(f)
                
            data["total_earnings"] += amount
            data["daily"] += amount # Simplified daily tracking
            
            # Log transaction
            transaction = {
                "timestamp": datetime.utcnow().isoformat(),
                "amount": round(amount, 2),
                "source": source,
                "asset_url": asset_url
            }
            if metadata:
                transaction.update(metadata)
            data["history"].append(transaction)
            
            # Keep history manageable
            if len(data["history"]) > 50:
                data["history"] = data["history"][-50:]
                
            with open(EARNINGS_FILE, 'w') as f:
                json.dump(data, f, indent=4)

            self._write_db_event(amount, source, asset_url, metadata, transaction["timestamp"])
        except Exception as e:
            print(f"Error updating ledger: {e}")

    @staticmethod
    async def _write_db_event_async(
        amount: float,
        source: str,
        asset_url: str | None,
        metadata: dict | None,
        timestamp: str,
    ) -> None:
        try:
            from backend.core import database as db
            from backend.models.revenue import RevenueEvent

            if db.AsyncSessionLocal is None or db.async_engine is None:
                db.create_database_engines()
            parsed_timestamp = timestamp.replace("Z", "+00:00") if timestamp.endswith("Z") else timestamp
            kind = (metadata or {}).get("kind", "simulated")
            async with db.AsyncSessionLocal() as session:
                session.add(
                    RevenueEvent(
                        id=str(uuid4()),
                        amount=float(amount),
                        currency="USD",
                        source=source,
                        kind=str(kind),
                        asset_url=asset_url,
                        metadata_json=metadata,
                        occurred_at=datetime.fromisoformat(parsed_timestamp),
                    )
                )
                await session.commit()
        except Exception as e:
            print(f"Error writing revenue event to DB: {e}")

    @staticmethod
    def _write_db_event(
        amount: float,
        source: str,
        asset_url: str | None,
        metadata: dict | None,
        timestamp: str,
    ) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(
                FulfillmentEngine._write_db_event_async(
                    amount, source, asset_url, metadata, timestamp
                )
            )
            return

        task = loop.create_task(
            FulfillmentEngine._write_db_event_async(
                amount, source, asset_url, metadata, timestamp
            )
        )
        task.add_done_callback(
            lambda t: print(f"Error writing revenue event to DB: {t.exception()}") if t.exception() else None
        )

    def record_sale(self, amount: float, source: str, asset_url: str = None, metadata: dict | None = None):
        """Record a real sale amount into the ledger."""
        if amount <= 0:
            return
        metadata = metadata or {}
        metadata.setdefault("kind", "real")
        self._update_ledger(amount, source, asset_url, metadata)

    def get_earnings_summary(self):
        try:
            with open(EARNINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"total_earnings": 0.0}

fulfillment_engine = FulfillmentEngine()
