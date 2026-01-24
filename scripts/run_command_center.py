#!/usr/bin/env python3
"""
Run Command Center - Launch and operate the Propulse-AutonomaX command structure

Usage:
    python scripts/run_command_center.py --dashboard
    python scripts/run_command_center.py --sprint 500
    python scripts/run_command_center.py --brand community
    python scripts/run_command_center.py --cycle
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomax.command_center import get_command_center, MissionPriority


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗  ██████╗ ██████╗ ██╗   ██╗██╗     ███████╗███████╗        ║
║   ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██║   ██║██║     ██╔════╝██╔════╝        ║
║   ██████╔╝██████╔╝██║   ██║██████╔╝██║   ██║██║     ███████╗█████╗          ║
║   ██╔═══╝ ██╔══██╗██║   ██║██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝          ║
║   ██║     ██║  ██║╚██████╔╝██║     ╚██████╔╝███████╗███████║███████╗        ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝        ║
║                                                                              ║
║              AUTONOMAX COMMAND CENTER - KPI-DRIVEN EXECUTION                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def print_dashboard(dashboard: dict):
    """Pretty print the executive dashboard"""
    print("\n" + "="*80)
    print(f"  EXECUTIVE DASHBOARD - {dashboard['organization']['name']}")
    print(f"  Generated: {dashboard['generated_at']}")
    print("="*80)
    
    # Health Score
    health = dashboard['organization']['health_score']
    health_bar = "█" * int(health / 10) + "░" * (10 - int(health / 10))
    print(f"\n  HEALTH SCORE: [{health_bar}] {health:.1f}%")
    
    if dashboard['organization']['at_risk_areas']:
        print(f"  ⚠️  AT RISK: {', '.join(dashboard['organization']['at_risk_areas'])}")
    
    # KPIs
    print("\n  KEY PERFORMANCE INDICATORS")
    print("  " + "-"*76)
    
    kpis = dashboard['kpis']
    print(f"  Revenue:       ${kpis['revenue']['actual']:,.2f} / ${kpis['revenue']['target']:,.2f} ({kpis['revenue']['progress']})")
    print(f"  Email List:    {kpis['email_list']['actual']:,} / {kpis['email_list']['target']:,}")
    print(f"  Social:        {kpis['social_followers']['actual']:,} / {kpis['social_followers']['target']:,}")
    print(f"  Delivery:      {kpis['operations']['delivery_success']}")
    print(f"  Automation:    {kpis['operations']['automation_coverage']}")
    
    # Directors
    print("\n  DIRECTOR STATUS")
    print("  " + "-"*76)
    
    for director_id, info in dashboard['directors'].items():
        status = "🟢" if not info['at_risk_kpis'] else "🟡"
        print(f"  {status} {info['name']}")
        print(f"     Tasks: {info['tasks_pending']} pending, {info['tasks_in_progress']} in progress")
        if info['at_risk_kpis']:
            print(f"     ⚠️  At Risk KPIs: {', '.join(info['at_risk_kpis'])}")
    
    # Active Missions
    if dashboard['active_missions']:
        print("\n  ACTIVE MISSIONS")
        print("  " + "-"*76)
        for mission in dashboard['active_missions']:
            print(f"  📋 {mission['title']}")
            print(f"     Progress: {mission['progress']} | Deadline: {mission['deadline'][:10]} | Priority: {mission['priority']}")
    
    # Priority Actions
    if dashboard['priority_actions']:
        print("\n  PRIORITY ACTIONS (Top 5)")
        print("  " + "-"*76)
        for i, action in enumerate(dashboard['priority_actions'][:5], 1):
            print(f"  {i}. [{action['director'].upper()}] {action.get('action', 'Execute task')}")
            print(f"     Target: {action.get('target', 'N/A')}")
    
    print("\n" + "="*80)


def print_sprint_result(result: dict):
    """Pretty print sprint launch result"""
    print("\n" + "="*60)
    print("  🚀 REVENUE SPRINT LAUNCHED")
    print("="*60)
    print(f"\n  Mission ID: {result['mission']}")
    print(f"  Target: {result['target']}")
    print(f"  Deadline: {result['deadline'][:10]}")
    print(f"  Status: {result['status'].upper()}")
    
    print("\n  IMMEDIATE ACTIONS:")
    for i, action in enumerate(result['immediate_actions'], 1):
        print(f"  {i}. {action.get('action', 'Execute')}")
        print(f"     → {action.get('target', '')}")
        if action.get('expected_lift'):
            print(f"     Expected: {action['expected_lift']}")
    
    print("\n" + "="*60)


def print_cycle_result(result: dict):
    """Pretty print cycle execution result"""
    print("\n" + "="*60)
    print("  ⚙️  EXECUTION CYCLE COMPLETED")
    print("="*60)
    print(f"\n  Timestamp: {result['timestamp']}")
    print(f"  Health Score: {result['health_score']:.1f}%")
    
    if result['at_risk_areas']:
        print(f"  ⚠️  At Risk: {', '.join(result['at_risk_areas'])}")
    
    print(f"\n  Actions Taken: {len(result['actions_taken'])}")
    for action in result['actions_taken'][:5]:
        status_icon = "✅" if action['status'] == 'completed' else "⚠️"
        print(f"    {status_icon} [{action['director']}] {action['task_id']}")
    
    if result['escalations']:
        print("\n  ⚠️  ESCALATIONS:")
        for escalation in result['escalations']:
            print(f"    • {escalation['type']}: {escalation['recommendation']}")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(description="Propulse-AutonomaX Command Center")
    parser.add_argument("--dashboard", action="store_true", help="Show executive dashboard")
    parser.add_argument("--sprint", type=int, help="Launch revenue sprint with target amount")
    parser.add_argument("--brand", type=str, help="Launch brand push (community/social)")
    parser.add_argument("--growth", type=str, help="Launch growth campaign (email/traffic)")
    parser.add_argument("--cycle", action="store_true", help="Execute one operational cycle")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if not args.json:
        print_banner()
    
    # Initialize command center
    cc = get_command_center()
    
    if args.dashboard:
        dashboard = cc.get_executive_dashboard()
        if args.json:
            print(json.dumps(dashboard, indent=2, default=str))
        else:
            print_dashboard(dashboard)
    
    elif args.sprint:
        result = cc.launch_revenue_sprint(target=args.sprint, days=7)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print_sprint_result(result)
    
    elif args.brand:
        result = cc.launch_brand_push(focus=args.brand)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\n🎨 Brand Push Launched: {result['mission']}")
            print(f"Focus: {result['focus']}")
            print(f"Deadline: {result['deadline'][:10]}")
            print("\nContent Calendar (7 days):")
            for day in result['content_calendar']:
                print(f"  {day['day_name']}: {day['content_type']} → {', '.join(day['platforms'])}")
    
    elif args.growth:
        result = cc.launch_growth_campaign(channel=args.growth)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\n📈 Growth Campaign Launched: {result['mission']}")
            print(f"Channel: {result['channel']}")
            print("\nKPI Targets:")
            for kpi, target in result['kpi_targets'].items():
                print(f"  • {kpi}: {target}")
    
    elif args.cycle:
        result = cc.execute_cycle()
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print_cycle_result(result)
    
    else:
        # Default: show dashboard
        dashboard = cc.get_executive_dashboard()
        if args.json:
            print(json.dumps(dashboard, indent=2, default=str))
        else:
            print_dashboard(dashboard)
            print("\n  AVAILABLE COMMANDS:")
            print("  --dashboard     Show executive dashboard")
            print("  --sprint N      Launch $N revenue sprint")
            print("  --brand TYPE    Launch brand push (community/social)")
            print("  --growth TYPE   Launch growth campaign (email/traffic)")
            print("  --cycle         Execute one operational cycle")
            print("  --json          Output as JSON\n")


if __name__ == "__main__":
    main()
