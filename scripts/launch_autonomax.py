#!/usr/bin/env python3
"""
AutonomaX Launch Script
=======================

This script launches the autonomous business execution system.
It's the "set and forget" trigger that activates all engines.

Usage:
    python scripts/launch_autonomax.py [--mode full-auto|semi-auto|manual]
    
    # Quick win actions
    python scripts/launch_autonomax.py --action flash_sale
    python scripts/launch_autonomax.py --action dm_outreach
    python scripts/launch_autonomax.py --action content_burst
    
    # Launch a mission
    python scripts/launch_autonomax.py --mission "First $500 Sprint"
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autonomax import (
    AutonomaXOrchestrator,
    get_orchestrator,
    launch_business_mission,
)


def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def print_banner():
    """Print the AutonomaX banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ██╗ ██████╗ ███╗   ███╗ █████╗ ██╗  ██╗  ║
    ║    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗  ██║██╔═══██╗████╗ ████║██╔══██╗╚██╗██╔╝  ║
    ║    ███████║██║   ██║   ██║   ██║   ██║██╔██╗ ██║██║   ██║██╔████╔██║███████║ ╚███╔╝   ║
    ║    ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══██║ ██╔██╗   ║
    ║    ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██║  ██║██╔╝ ██╗  ║
    ║    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ║
    ║                                                                   ║
    ║              Autonomous Business Execution System                 ║
    ║                     PROFIT OS COMMANDER                           ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_dashboard(orchestrator: AutonomaXOrchestrator):
    """Print the current dashboard state"""
    dashboard = orchestrator.get_dashboard()
    
    print("\n" + "="*70)
    print("                    AUTONOMAX COMMAND CENTER")
    print("="*70)
    
    # Orchestrator Status
    orch = dashboard["orchestrator"]
    print(f"\n[ORCHESTRATOR]")
    print(f"  Mode: {orch['mode'].upper()}")
    print(f"  Running: {'YES' if orch['running'] else 'NO'}")
    print(f"  Cycles Completed: {orch['cycles_completed']}")
    print(f"  Bus Queue: {orch['bus_queue_length']} messages")
    
    # Financials
    cmd = dashboard["commander"]
    print(f"\n[FINANCIALS]")
    print(f"  Budget Remaining: ${cmd['financials']['budget_remaining']:,.2f}")
    print(f"  Revenue Target: ${cmd['financials']['revenue_target']:,.2f}")
    print(f"  Current Revenue: ${cmd['financials']['current_revenue']:,.2f}")
    print(f"  Progress: {cmd['financials']['progress']}")
    
    # Revenue Engine
    rev = dashboard["revenue"]
    print(f"\n[REVENUE ENGINE]")
    print(f"  Total Revenue: ${rev['total_revenue']:,.2f}")
    print(f"  Today Revenue: ${rev['today_revenue']:,.2f}")
    print(f"  Products Active: {rev['active_products']}")
    
    # Growth Engine
    growth = dashboard["growth"]
    print(f"\n[GROWTH ENGINE]")
    print(f"  Active Campaigns: {growth['active_campaigns']}")
    print(f"  Total Reach: {growth['total_reach']:,}")
    print(f"  Email List: {growth['email_list']:,}")
    
    # Delivery Engine
    delivery = dashboard["delivery"]
    print(f"\n[DELIVERY ENGINE]")
    print(f"  Total Deliveries: {delivery['total_deliveries']}")
    print(f"  Success Rate: {delivery['success_rate']}")
    print(f"  Scheduled Emails: {delivery['scheduled_emails']}")
    
    # Totals
    totals = dashboard["totals"]
    print(f"\n[TOTALS]")
    print(f"  Jobs Processed: {totals['total_jobs_processed']}")
    print(f"  Overall Success Rate: {totals['overall_success_rate']:.1f}%")
    
    print("\n" + "="*70)


def launch_default_mission(orchestrator: AutonomaXOrchestrator):
    """Launch the default revenue acceleration mission"""
    print("\n[LAUNCHING MISSION] First $500 Sprint")
    print("-" * 50)
    
    result = orchestrator.launch_mission(
        title="First $500 Sprint",
        objective="Generate first $500 in revenue within 48 hours through digital products and services",
        income_streams=[
            "digital_products",
            "services",
            "content",
        ],
        time_horizon="NOW",
    )
    
    print(f"\nMission ID: {result['mission_id']}")
    print(f"Status: {result['status']}")
    print(f"\nTier 1 Actions (Execute Now):")
    for i, action in enumerate(result['tier1_actions'], 1):
        print(f"  {i}. {action}")
    
    print(f"\nKPIs:")
    for kpi, target in result['kpis'].items():
        print(f"  - {kpi}: {target}")
    
    return result


def execute_quick_win(orchestrator: AutonomaXOrchestrator, action: str):
    """Execute a quick win action"""
    print(f"\n[EXECUTING QUICK WIN] {action}")
    print("-" * 50)
    
    result = orchestrator.execute_quick_win(action)
    
    print(f"Action: {result['action']}")
    print(f"Status: {result['status']}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="AutonomaX Autonomous Business Execution System"
    )
    parser.add_argument(
        "--mode",
        choices=["manual", "semi-auto", "full-auto"],
        default="manual",
        help="Execution mode (default: manual)",
    )
    parser.add_argument(
        "--action",
        choices=["flash_sale", "dm_outreach", "content_burst", "review_push"],
        help="Execute a quick win action",
    )
    parser.add_argument(
        "--mission",
        type=str,
        help="Launch a named mission",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Show dashboard and exit",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    print_banner()
    
    # Get orchestrator
    orchestrator = get_orchestrator()
    orchestrator.set_mode(args.mode)
    
    # Dashboard only
    if args.dashboard:
        print_dashboard(orchestrator)
        return
    
    # Quick win action
    if args.action:
        result = execute_quick_win(orchestrator, args.action)
        print_dashboard(orchestrator)
        return
    
    # Named mission
    if args.mission:
        result = orchestrator.launch_mission(
            title=args.mission,
            objective=f"Execute mission: {args.mission}",
            income_streams=["digital_products", "services"],
            time_horizon="NOW",
        )
        print_dashboard(orchestrator)
        return
    
    # Default: Launch the standard revenue sprint
    result = launch_default_mission(orchestrator)
    print_dashboard(orchestrator)
    
    # Save state
    state_file = project_root / "autonomax_state.json"
    orchestrator.save_state(str(state_file))
    print(f"\nState saved to: {state_file}")
    
    print("\n" + "="*70)
    print("                    MISSION ACTIVATED")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Check your Shopify dashboard for new orders")
    print("  2. Monitor email for customer inquiries")
    print("  3. Run 'python scripts/launch_autonomax.py --dashboard' for updates")
    print("  4. Execute quick wins: --action flash_sale")
    print("\n")


if __name__ == "__main__":
    main()
