#!/usr/bin/env python3
"""
Quick Actions for Business Flow Execution
Run: python scripts/quick_actions.py [action]
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

CONTENT_DIR = Path("marketing_outputs/traffic_supply")
TRACKER_PATH = Path("autonomax/execution_tracker.json")

def show_menu():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           AUTONOMAX QUICK ACTIONS MENU                       ║
╠══════════════════════════════════════════════════════════════╣
║  1. view_linkedin    - Show LinkedIn post content            ║
║  2. view_twitter     - Show Twitter thread                   ║
║  3. view_reddit      - Show Reddit posts                     ║
║  4. view_ih          - Show Indie Hackers launch post        ║
║  5. check_status     - Show execution tracker status         ║
║  6. mark_posted [ch] - Mark channel as posted                ║
║  7. add_revenue [amt]- Log new revenue                       ║
║  8. daily_report     - Generate daily report                 ║
║  9. open_shopier     - Open Shopier dashboard                ║
╚══════════════════════════════════════════════════════════════╝
    """)

def view_content(filename):
    filepath = CONTENT_DIR / filename
    if filepath.exists():
        print(f"\n{'='*60}")
        print(f"CONTENT: {filename}")
        print('='*60)
        print(filepath.read_text())
    else:
        print(f"File not found: {filepath}")

def check_status():
    if TRACKER_PATH.exists():
        tracker = json.loads(TRACKER_PATH.read_text())
        print(f"\n{'='*60}")
        print("EXECUTION STATUS")
        print('='*60)
        print(f"Mission: {tracker['mission']}")
        print(f"Target: ${tracker['revenue']['target']} by {tracker['target_date']}")
        print(f"Current Revenue: ${tracker['revenue']['current']}")
        print(f"\nChannel Status:")
        for ch, data in tracker['channels'].items():
            status = "✓ POSTED" if data.get('posted') else "○ PENDING"
            print(f"  {ch}: {status}")

def mark_posted(channel):
    if TRACKER_PATH.exists():
        tracker = json.loads(TRACKER_PATH.read_text())
        if channel in tracker['channels']:
            tracker['channels'][channel]['posted'] = True
            tracker['channels'][channel]['posted_at'] = datetime.now().isoformat()
            TRACKER_PATH.write_text(json.dumps(tracker, indent=2))
            print(f"✓ Marked {channel} as posted")

def add_revenue(amount):
    if TRACKER_PATH.exists():
        tracker = json.loads(TRACKER_PATH.read_text())
        tracker['revenue']['current'] += float(amount)
        tracker['revenue']['orders'].append({
            "amount": float(amount),
            "timestamp": datetime.now().isoformat()
        })
        TRACKER_PATH.write_text(json.dumps(tracker, indent=2))
        print(f"✓ Added ${amount} - Total: ${tracker['revenue']['current']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_menu()
    else:
        action = sys.argv[1]
        if action == "view_linkedin":
            view_content("LINKEDIN_post.txt")
        elif action == "view_twitter":
            view_content("TWITTER_thread.txt")
        elif action == "view_reddit":
            for f in CONTENT_DIR.glob("REDDIT_*.txt"):
                view_content(f.name)
        elif action == "view_ih":
            view_content("INDIEHACKERS_launch.txt")
        elif action == "check_status":
            check_status()
        elif action == "mark_posted" and len(sys.argv) > 2:
            mark_posted(sys.argv[2])
        elif action == "add_revenue" and len(sys.argv) > 2:
            add_revenue(sys.argv[2])
        elif action == "daily_report":
            check_status()
        elif action == "open_shopier":
            subprocess.run(["open", "https://www.shopier.com/seller"])
        else:
            show_menu()
