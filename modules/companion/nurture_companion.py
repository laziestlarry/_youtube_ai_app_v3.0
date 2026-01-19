"""
Nurture Companion - Production Sidecar for AutonomaX.
Provides read-only oversight, sentiment auditing, and manual referral injection
without disturbing the primary production shell.
"""
import logging
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Ensure we can import from the project root
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from modules.growth_engine_v1.app import SessionLocal
from modules.growth_engine_v1.models import GrowthLedgerEntry
from modules.ai_agency.chimera_engine import chimera_engine

logger = logging.getLogger(__name__)

class NurtureCompanion:
    def __init__(self):
        self.directives_file = "logs/nurture_directives.json"
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.directives_file):
            with open(self.directives_file, "w") as f:
                json.dump([], f)

    def get_recent_leads(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Fetch leads from the Growth Ledger without interfering with active missions."""
        db = SessionLocal()
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            # We look for entries or specifically metadata that indicates outreach
            entries = db.query(GrowthLedgerEntry).filter(
                GrowthLedgerEntry.created_at >= cutoff
            ).all()
            
            leads = []
            for entry in entries:
                leads.append({
                    "id": entry.id,
                    "amount": entry.amount_cents / 100.0,
                    "status": entry.status,
                    "meta": entry.provenance_meta,
                    "timestamp": entry.created_at.isoformat()
                })
            return leads
        finally:
            db.close()

    async def audit_lead_sentiment(self, lead_id: int, interaction_text: str) -> Dict[str, Any]:
        """Analyze lead interaction and generate a 'Temperature' and 'Directive'."""
        prompt = f"""
        Analyze this interaction from a high-ticket B2B lead (ID: {lead_id}):
        "{interaction_text}"
        
        Determine:
        1. Sentiment (Positive/Neutral/Negative)
        2. Lead Temperature (Cold/Warm/Hot)
        3. Strategic Directive (e.g., "Send Authority Whitepaper", "Inject 5-slot Scarcity", "Manual Outreach Needed")
        
        Return in JSON format.
        """
        try:
            response = await chimera_engine.generate_response(prompt, task_type="analysis")
            # Simple extraction
            import re
            match = re.search(r"({.*})", response, re.DOTALL)
            if match:
                directive = json.loads(match.group(1))
            else:
                directive = {"raw": response}
            
            self._save_directive(lead_id, directive)
            return directive
        except Exception as e:
            logger.error(f"Sentiment audit failed: {e}")
            return {"error": str(e)}

    def _save_directive(self, lead_id: int, directive: Dict[str, Any]):
        """Persist directives for the Companion Dashboard."""
        with open(self.directives_file, "r") as f:
            data = json.load(f)
        
        data.append({
            "lead_id": lead_id,
            "directive": directive,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(self.directives_file, "w") as f:
            json.dump(data, f, indent=2)

    def inject_referral_logic(self, lead_id: int, referral_type: str = "high_authority") -> str:
        """Generate a personalized referral link for 'Surprise & Delight' intervention."""
        # This would link to specialized vsl paths or whitepapers
        base_urls = {
            "high_authority": "https://autonomax.ai/protocol/alexandria",
            "scarcity": "https://autonomax.ai/checkout/limited-v1",
            "proof_of_value": "https://autonomax.ai/results/enterprise-casestudy"
        }
        url = base_urls.get(referral_type, base_urls["high_authority"])
        return f"{url}?ref=companion_{lead_id}"

nurture_companion = NurtureCompanion()
