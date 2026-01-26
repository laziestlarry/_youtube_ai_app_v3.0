#!/usr/bin/env python3
"""
AutonomaX Monitoring Dashboard
==============================

Real-time operational view of all systems, KPIs, and required actions.

Usage:
    python scripts/monitor_dashboard.py           # Full dashboard
    python scripts/monitor_dashboard.py --quick   # Quick status
    python scripts/monitor_dashboard.py --actions # Actions only
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title: str):
    print(f"\n{title}")
    print("-" * 50)

def get_shopier_status() -> dict:
    """Get Shopier store status"""
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv("SHOPIER_PERSONAL_ACCESS_TOKEN")
        if not token:
            return {"status": "NO_TOKEN", "products": 0}
        
        resp = requests.get(
            "https://api.shopier.com/v1/products",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if resp.status_code == 200:
            products = resp.json()
            active = [p for p in products if p.get("stockStatus") == "inStock"]
            total_value = sum(float(p.get("price", 0)) for p in active)
            return {
                "status": "CONNECTED",
                "products": len(active),
                "catalog_value": total_value,
            }
        elif resp.status_code == 401:
            return {"status": "TOKEN_EXPIRED", "products": 0}
        else:
            return {"status": f"ERROR_{resp.status_code}", "products": 0}
    except Exception as e:
        return {"status": f"ERROR: {str(e)[:30]}", "products": 0}

def get_genesis_status() -> dict:
    """Get Genesis system status"""
    try:
        from autonomax.genesis import get_genesis
        genesis = get_genesis()
        return genesis.get_state()
    except Exception as e:
        return {"error": str(e)}

def get_command_center_status() -> dict:
    """Get Command Center status"""
    try:
        from autonomax.command_center import get_command_center
        cc = get_command_center()
        return cc.get_executive_dashboard()
    except Exception as e:
        return {"error": str(e)}

def check_content_files() -> dict:
    """Check available content files"""
    content_dir = ROOT / "marketing_outputs" / "social_posts"
    if not content_dir.exists():
        return {"files": 0, "latest": None}
    
    files = list(content_dir.glob("*.txt"))
    latest = max(files, key=lambda f: f.stat().st_mtime) if files else None
    
    return {
        "files": len(files),
        "latest": latest.name if latest else None,
        "ready_to_post": len(files) > 0,
    }

def get_manual_actions() -> list:
    """Get list of manual actions required"""
    actions = []
    
    # Check Shopier discount code
    actions.append({
        "priority": 1,
        "category": "SHOPIER",
        "action": "Create LAZY20 discount code (20% off, 48h)",
        "url": "https://www.shopier.com/seller/discounts",
        "time": "2 min",
        "status": "PENDING",
    })
    
    # Check social posting
    actions.append({
        "priority": 2,
        "category": "SOCIAL",
        "action": "Post flash sale to LinkedIn",
        "url": "https://www.linkedin.com/in/lazy-larry-344631373/",
        "content_file": "marketing_outputs/social_posts/SPRINT_LAUNCH_*.txt",
        "time": "3 min",
        "status": "PENDING",
    })
    
    actions.append({
        "priority": 3,
        "category": "SOCIAL",
        "action": "Post flash sale to Twitter",
        "url": "https://x.com/lazylarries",
        "time": "2 min",
        "status": "PENDING",
    })
    
    actions.append({
        "priority": 4,
        "category": "SOCIAL",
        "action": "Post flash sale to Facebook",
        "url": "https://www.facebook.com/profile.php?id=61578065763242",
        "time": "2 min",
        "status": "PENDING",
    })
    
    actions.append({
        "priority": 5,
        "category": "COMMUNITY",
        "action": "Join Indie Hackers and post introduction",
        "url": "https://www.indiehackers.com/",
        "content_file": "marketing_outputs/social_posts/COMMUNITY_INTRO_*.txt",
        "time": "5 min",
        "status": "PENDING",
    })
    
    actions.append({
        "priority": 6,
        "category": "COMMUNITY",
        "action": "Post to r/Entrepreneur or r/passive_income",
        "url": "https://www.reddit.com/r/Entrepreneur/",
        "time": "5 min",
        "status": "PENDING",
    })
    
    return actions

def get_automated_schedules() -> list:
    """Get automated schedule summary"""
    return [
        {
            "schedule": "Every 15 min",
            "task": "Work queue execution",
            "script": "run_work_schedule.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Every 4 hours",
            "task": "Revenue sync",
            "script": "run_revenue_sync.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Every hour",
            "task": "Ledger monitoring",
            "script": "monitor_ledger.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Daily 9:00 AM",
            "task": "Chimera daily ops",
            "script": "chimera_ops.py daily",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Daily 10:00 AM",
            "task": "Storefront health check",
            "script": "post_deploy_health_report.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Daily 10:30 AM",
            "task": "Shopier checkout verify",
            "script": "verify_shopier_checkout.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Weekly Monday 8:30 AM",
            "task": "Alexandria Genesis refresh",
            "script": "alexandria_genesis.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Weekly Monday 10:00 AM",
            "task": "Chimera weekly ops",
            "script": "chimera_ops.py weekly",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Weekly Monday 11:00 AM",
            "task": "Marketing asset generation",
            "script": "generate_listing_assets.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Weekly Friday 12:00 PM",
            "task": "Payout orchestration",
            "script": "orchestrate_bank_payout.py",
            "status": "CONFIGURED",
        },
        {
            "schedule": "Monthly 1st 11:00 AM",
            "task": "Chimera monthly review",
            "script": "chimera_ops.py monthly",
            "status": "CONFIGURED",
        },
    ]

def print_dashboard():
    """Print full monitoring dashboard"""
    print_header("AUTONOMAX MONITORING DASHBOARD")
    print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # 1. SYSTEM STATUS
    print_section("1. SYSTEM STATUS")
    
    shopier = get_shopier_status()
    genesis = get_genesis_status()
    content = check_content_files()
    
    print(f"""
  Shopier Store:
    Status: {shopier.get('status', 'UNKNOWN')}
    Products Live: {shopier.get('products', 0)}
    Catalog Value: {shopier.get('catalog_value', 0):,.0f} TRY

  Genesis System:
    Initialized: {genesis.get('initialized', False)}
    Files Indexed: {genesis.get('assets', {}).get('files_indexed', 0):,}
    Knowledge Nodes: {genesis.get('assets', {}).get('knowledge_nodes', 0):,}
    Revenue Streams: {genesis.get('revenue', {}).get('streams', 0)}
    Target MRR: ${genesis.get('revenue', {}).get('target_mrr', 0):,}

  Content Ready:
    Files Available: {content.get('files', 0)}
    Latest: {content.get('latest', 'None')}
    Ready to Post: {'YES' if content.get('ready_to_post') else 'NO'}
""")
    
    # 2. CURRENT SPRINT
    print_section("2. CURRENT SPRINT: $500 Revenue (48h)")
    print(f"""
  Target: $500 USD (~17,500 TRY)
  Orders Needed: ~5 orders
  Discount Code: LAZY20 (20% off)
  
  Progress: $0 / $500 (0%)
  [░░░░░░░░░░░░░░░░░░░░] 0%
  
  Time Remaining: ~48 hours
""")
    
    # 3. YOUR ACTION ITEMS (MANUAL)
    print_section("3. YOUR ACTION ITEMS (Do Now)")
    actions = get_manual_actions()
    total_time = sum(int(a['time'].split()[0]) for a in actions)
    
    print(f"\n  Total estimated time: {total_time} minutes\n")
    
    for i, action in enumerate(actions, 1):
        print(f"  [{i}] {action['category']}: {action['action']}")
        print(f"      URL: {action['url']}")
        if 'content_file' in action:
            print(f"      Content: {action['content_file']}")
        print(f"      Time: {action['time']}")
        print()
    
    # 4. AUTOMATED SCHEDULES
    print_section("4. AUTOMATED SCHEDULES (System Handles)")
    print(f"\n  To activate: crontab scripts/chimera_schedule.cron\n")
    
    schedules = get_automated_schedules()
    for sched in schedules[:6]:
        print(f"  {sched['schedule']:25} | {sched['task']}")
    
    print(f"\n  ... and {len(schedules) - 6} more scheduled tasks")
    
    # 5. QUICK COMMANDS
    print_section("5. QUICK COMMANDS")
    print(f"""
  # Check system status
  python scripts/monitor_dashboard.py --quick

  # Run income sprint activation
  python scripts/income_sprint_activate.py

  # Get executive dashboard
  python -c "from autonomax import get_command_center; print(get_command_center().get_executive_dashboard())"

  # Check Shopier products
  python -c "import requests,os; from dotenv import load_dotenv; load_dotenv(); r=requests.get('https://api.shopier.com/v1/products', headers={{'Authorization': f'Bearer {{os.getenv(\"SHOPIER_PERSONAL_ACCESS_TOKEN\")}}'}}); print(f'Products: {{len(r.json())}}')"

  # Run full Genesis
  python scripts/run_alexandria_chimera_genesis.py --full
""")
    
    # 6. NEXT PHASE PREVIEW
    print_section("6. NEXT PHASES (After $500)")
    print(f"""
  Phase 2: Community Momentum (Days 3-7)
    - Target: $1,000
    - Focus: Social proof and community engagement
    - Actions: 5 communities/day, 2 value posts/day

  Phase 3: Service Activation (Days 8-21)  
    - Target: $3,000
    - Focus: Fiverr gig launch
    - Actions: 3 gigs, outreach campaign

  Phase 4: Recurring Revenue (Days 22-60)
    - Target: $5,000
    - Focus: Subscription model
    - Actions: Membership tier, retention automation

  Phase 5: Scale & Consulting (Days 61-90)
    - Target: $15,000
    - Focus: Enterprise engagements
    - Actions: LinkedIn consulting launch, case studies
""")

def print_quick_status():
    """Print quick status summary"""
    print_header("QUICK STATUS")
    
    shopier = get_shopier_status()
    genesis = get_genesis_status()
    
    status_icon = "✓" if shopier.get('status') == 'CONNECTED' else "✗"
    genesis_icon = "✓" if genesis.get('initialized') else "✗"
    
    print(f"""
  [{status_icon}] Shopier: {shopier.get('status')} ({shopier.get('products', 0)} products)
  [{genesis_icon}] Genesis: {'Initialized' if genesis.get('initialized') else 'Not initialized'}
  
  Sprint Target: $500 / 48h
  Current: $0 (0%)
  
  NEXT ACTION: Create LAZY20 discount in Shopier
               https://www.shopier.com/seller/discounts
""")

def print_actions_only():
    """Print only manual actions"""
    print_header("MANUAL ACTIONS REQUIRED")
    
    actions = get_manual_actions()
    total_time = sum(int(a['time'].split()[0]) for a in actions)
    
    print(f"\n  Total time needed: {total_time} minutes")
    print(f"  Actions: {len(actions)}\n")
    
    for i, action in enumerate(actions, 1):
        print(f"  {i}. [{action['category']}] {action['action']}")
        print(f"     {action['url']}")
        print()

def main():
    parser = argparse.ArgumentParser(description="AutonomaX Monitoring Dashboard")
    parser.add_argument("--quick", action="store_true", help="Quick status only")
    parser.add_argument("--actions", action="store_true", help="Manual actions only")
    args = parser.parse_args()
    
    if args.quick:
        print_quick_status()
    elif args.actions:
        print_actions_only()
    else:
        print_dashboard()

if __name__ == "__main__":
    main()
