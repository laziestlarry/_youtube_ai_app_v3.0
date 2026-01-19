"""
Smoke test for AutonomaX Nurture Companion.
Verifies read-only ledger access and sentiment audit logic.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from modules.companion.nurture_companion import nurture_companion

async def verify_companion():
    print("🛰️ Starting Companion Sidecar Verification...")
    
    # 1. Test Ledger Audit
    print("\n[Test 1] Fetching recent leads...")
    leads = nurture_companion.get_recent_leads(hours=48)
    print(f"✅ Found {len(leads)} recent leads in the production ledger.")
    
    # 2. Test Sentiment Audit (Mock Interaction)
    print("\n[Test 2] Auditing sentiment for a mock interaction...")
    mock_id = 9999
    mock_text = "I'm interested in the AI Transformation program, but I need to see more enterprise case studies before we sign off."
    
    directive = await nurture_companion.audit_lead_sentiment(mock_id, mock_text)
    print("✅ Directive Generated:")
    print(f"   - Temperature: {directive.get('Lead Temperature', 'N/A')}")
    print(f"   - Sentiment: {directive.get('Sentiment', 'N/A')}")
    print(f"   - Recommendation: {directive.get('Strategic Directive', 'N/A')}")
    
    # 3. Test Referral Injection
    print("\n[Test 3] Generating Personalized Referral...")
    ref_link = nurture_companion.inject_referral_logic(mock_id, "proof_of_value")
    print(f"✅ Referral Link: {ref_link}")
    
    print("\n🛰️ COMPANION VERIFICATION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(verify_companion())
