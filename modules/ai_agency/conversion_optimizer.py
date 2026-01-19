"""
Conversion Optimizer - Injects psychological triggers and ROI-focused language into AI prompts.
Tailored for the US high-ticket market.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ConversionOptimizer:
    """
    Optimizes AI prompts for conversion using:
    - Anchoring (Value vs. Price)
    - Authority (AutonomaX Protocol)
    - Scarcity (Slot-based availability)
    - ROI-Centricity (Focus on outcomes)
    """

    def wrap_marketing_prompt(self, base_prompt: str, sku: Dict[str, Any]) -> str:
        """Inject conversion triggers into a marketing content prompt."""
        is_high_ticket = sku.get("price", {}).get("min", 0) >= 499
        
        triggers = ""
        if is_high_ticket:
            triggers = """
            PSYCHOLOGICAL TRIGGERS (HIGH-TICKET):
            1. Focus on ROI: Explain how this investment pays for itself in < 30 days.
            2. High Authority: Reference the 'AutonomaX Alexandria Protocol' as the source.
            3. Scarcity: Mention that only 5 executive slots are available for this quarter's cohort.
            4. B2B Tone: Use language appropriate for a CTO/CMO/Founder.
            """
        else:
            triggers = """
            PSYCHOLOGICAL TRIGGERS (RETAIL):
            1. Instant Gratification: Emphasize 'Immediate Download' and 'Day 1 Impact'.
            2. Social Proof: Use 'Join the 1,000+ creators' framing.
            3. Lower Friction: Focus on how easy it is to start.
            """

        return f"""
        {base_prompt}
        
        ---
        CONVERSION OPTIMIZATION LAYER:
        {triggers}
        
        CRITICAL: Do not just list these triggers. Weave them naturally into the narrative for maximum impact.
        Language: Professional American English.
        """

    def wrap_outreach_prompt(self, base_prompt: str, persona: Dict[str, Any]) -> str:
        """Fix prompts for lead outreach (DMs/Emails)."""
        return f"""
        {base_prompt}
        
        OUTREACH OPTIMIZATION:
        1. Personalized Hook: Reference the specific pain point: '{persona.get('pain_points', ['Scaling issues'])[0]}'.
        2. Soft CTA: Instead of 'Buy Now', use 'Are you open to a quick audit?' or 'Should I send the blueprint over?'.
        3. No Spam Language: Avoid 'Free', 'Guarantee', or excessive emojis. Keep it elite.
        """

conversion_optimizer = ConversionOptimizer()
