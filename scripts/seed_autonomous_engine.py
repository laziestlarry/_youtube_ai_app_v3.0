import requests
import json

BASE_URL = "http://localhost:8001"

def seed_engine():
    print("🚀 Seeding ProPulse-AutonomaX Autonomous Engine...")
    
    # 1. Seed Mission
    mission_payload = {
        "vision": "To architect a self-sustaining, AI-powered business ecosystem that autonomously generates income and accelerates professional mastery.",
        "values": {
            "core": ["Ethical Automation", "Strategic Dominance", "Pain-Killer Solutions"],
            "operational": ["Zero-Human Intervention", "Revenue First", "Circular Value"]
        },
        "north_star_metric": "daily_net_revenue"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/strategy/mission", json=mission_payload)
        print(f"✅ Mission Seeded: {r.status_code}")
    except Exception as e:
        print(f"❌ Mission Seed Error: {e}")

    # 2. Seed Workflows
    workflows = [
        {
            "name": "Revenue Mastery Loop",
            "trigger": "payment_completed",
            "steps": [
                {"step": 1, "action": "Credit Ledger", "params": {"status": "CLEARED"}},
                {"step": 2, "action": "AI Content Generation", "params": {"type": "success_story"}},
                {"step": 3, "action": "Distribute Artifact", "params": {"channel": "linkedin/twitter"}}
            ],
            "autonomous": True
        },
        {
            "name": "Growth Watchdog",
            "trigger": "daily_net_revenue_dip",
            "steps": [
                {"step": 1, "action": "Alert A-RE Auditor"},
                {"step": 2, "action": "Analyze Ad Spend"},
                {"step": 3, "action": "Pivot Strategy", "params": {"target": "high_ticket"}}
            ],
            "autonomous": True
        }
    ]

    for wf in workflows:
        try:
            r = requests.post(f"{BASE_URL}/workflows", json=wf)
            print(f"✅ Workflow '{wf['name']}' Seeded: {r.status_code}")
            if r.status_code != 200:
                print(f"❌ Error Detail: {r.text}")
        except Exception as e:
            print(f"❌ Workflow Seed Error: {e}")

    print("🏁 Seeding Complete.")

if __name__ == "__main__":
    seed_engine()
