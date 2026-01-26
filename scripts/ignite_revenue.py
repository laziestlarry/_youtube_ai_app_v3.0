#!/usr/bin/env python3
"""Revenue Engine Ignition - Compact launcher for autonomous sales."""
import json, os, sys, urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = os.getenv("BACKEND_ORIGIN", "https://youtube-ai-backend-71658389068.us-central1.run.app")

def check(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return {"ok": True, "data": r.read().decode()[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    print("="*60)
    print("REVENUE ENGINE IGNITION")
    print(f"Time: {datetime.now().isoformat()}")
    print("="*60)
    
    # Phase 1: Health Check
    print("\n[1/4] SYSTEM CHECK")
    h = check(f"{BACKEND}/health")
    print(f"  Backend: {'OK' if h['ok'] else 'FAIL'}")
    
    # Phase 2: Sync Orders
    print("\n[2/4] ORDER SYNC")
    try:
        req = urllib.request.Request(f"{BACKEND}/api/growth/sync/orders?limit=50", method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"  Sync: OK - {r.read().decode()[:100]}")
    except Exception as e:
        print(f"  Sync: {e}")
    
    # Phase 3: Revenue Check
    print("\n[3/4] REVENUE STATUS")
    ep = ROOT / "earnings.json"
    if ep.exists():
        d = json.loads(ep.read_text())
        real = [h for h in d.get("history",[]) if h.get("kind")=="real"]
        print(f"  Real Sales: {len(real)}")
        print(f"  Real Revenue: ${sum(float(h.get('amount',0)) for h in real):.2f}")
    
    # Phase 4: Quick Links
    print("\n[4/4] SALES LINKS")
    sp = ROOT / "docs/commerce/shopier_product_map.json"
    if sp.exists():
        m = json.loads(sp.read_text())
        for sku, info in list(m.items())[:5]:
            print(f"  {sku}: {info.get('url','')}")
    
    print("\n" + "="*60)
    print("IMMEDIATE ACTIONS:")
    print("  1. Share links on LinkedIn/Twitter")
    print("  2. Post YouTube community update")  
    print("  3. Check Fiverr gig visibility")
    print("  4. Monitor: " + f"{BACKEND}/api/outcomes/summary")
    print("="*60)

if __name__ == "__main__":
    main()
