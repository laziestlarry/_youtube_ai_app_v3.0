#!/usr/bin/env python3
"""
Quick Actions for Business Flow Execution
Run: python scripts/quick_actions.py [action]

Enhanced v2.0 - Now with better UX and more features
"""
import sys
import json
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / "marketing_outputs" / "traffic_supply"
NETWORK_DIR = PROJECT_ROOT / "marketing_outputs" / "network_building"
TRACKER_PATH = PROJECT_ROOT / "autonomax" / "execution_tracker.json"

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RED = '\033[91m'
BOLD = '\033[1m'
END = '\033[0m'

def show_menu():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════════╗
║           AUTONOMAX QUICK ACTIONS MENU v2.0                  ║
╠══════════════════════════════════════════════════════════════╣{END}
║                                                              ║
║  {BOLD}CONTENT{END}                                                      ║
║    view_linkedin    - Show LinkedIn post content             ║
║    view_twitter     - Show Twitter thread                    ║
║    view_reddit      - Show Reddit posts                      ║
║    view_ih          - Show Indie Hackers launch post         ║
║    view_network     - Show network building content          ║
║                                                              ║
║  {BOLD}TRACKING{END}                                                     ║
║    check_status     - Show execution tracker status          ║
║    mark_posted [ch] - Mark channel as posted                 ║
║    add_revenue [amt]- Log new revenue                        ║
║    next             - Get next recommended action            ║
║                                                              ║
║  {BOLD}TOOLS{END}                                                        ║
║    open_shopier     - Open Shopier dashboard                 ║
║    open_linkedin    - Open LinkedIn                          ║
║    open_twitter     - Open Twitter                           ║
║    open_reddit      - Open Reddit                            ║
║    commander        - Launch Mission Commander               ║
║    assist           - Launch Execution Assistant             ║
║                                                              ║
{CYAN}╚══════════════════════════════════════════════════════════════╝{END}
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
        revenue = tracker.get('revenue', {})
        current = revenue.get('current', 0)
        target = revenue.get('target', 500)
        progress = (current / target * 100) if target > 0 else 0
        
        # Progress bar
        bar_filled = int(progress / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        
        print(f"\n{CYAN}{'='*60}{END}")
        print(f"{BOLD}EXECUTION STATUS{END}")
        print(f"{CYAN}{'='*60}{END}")
        print(f"Mission: {tracker.get('mission', 'N/A')}")
        print(f"Target: ${target} by {tracker.get('target_date', 'N/A')}")
        print(f"Current Revenue: {GREEN}${current}{END}")
        print(f"Progress: [{bar}] {progress:.0f}%")
        print(f"\n{BOLD}Channel Status:{END}")
        
        posted_count = 0
        for ch, data in tracker.get('channels', {}).items():
            if data.get('posted'):
                status = f"{GREEN}✓ POSTED{END}"
                posted_count += 1
            else:
                status = f"{YELLOW}○ PENDING{END}"
            print(f"  {ch}: {status}")
        
        total = len(tracker.get('channels', {}))
        print(f"\n  Posted: {posted_count}/{total}")
    else:
        print(f"{RED}Tracker not found. Run mission_commander.py to initialize.{END}")

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
        new_total = tracker['revenue']['current']
        target = tracker['revenue']['target']
        print(f"{GREEN}✓ Added ${amount} - Total: ${new_total}{END}")
        if new_total >= target:
            print(f"\n{GREEN}{BOLD}🎉 CONGRATULATIONS! TARGET REACHED! 🎉{END}")


def get_next_action():
    """Get the next recommended action"""
    if not TRACKER_PATH.exists():
        print("Start with: python scripts/mission_commander.py")
        return
    
    tracker = json.loads(TRACKER_PATH.read_text())
    channels = tracker.get('channels', {})
    
    # Priority order
    priority = ['linkedin', 'twitter', 'reddit', 'indie_hackers', 'facebook', 'quora', 'medium']
    
    for ch in priority:
        if ch in channels and not channels[ch].get('posted'):
            print(f"\n{CYAN}{'='*60}{END}")
            print(f"{BOLD}NEXT ACTION: Post to {ch.upper()}{END}")
            print(f"{CYAN}{'='*60}{END}")
            
            content_files = {
                'linkedin': 'LINKEDIN_post.txt',
                'twitter': 'TWITTER_thread.txt',
                'reddit': 'REDDIT_r_Entrepreneur.txt',
                'indie_hackers': 'INDIEHACKERS_launch.txt',
                'facebook': 'FACEBOOK_groups.txt',
                'quora': 'QUORA_answers.txt',
                'medium': 'MEDIUM_article.txt',
            }
            
            urls = {
                'linkedin': 'https://www.linkedin.com/feed/',
                'twitter': 'https://twitter.com/compose/tweet',
                'reddit': 'https://www.reddit.com/r/Entrepreneur/submit',
                'indie_hackers': 'https://www.indiehackers.com/new-post',
                'facebook': 'https://www.facebook.com/groups/',
                'quora': 'https://www.quora.com/',
                'medium': 'https://medium.com/new-story',
            }
            
            print(f"\n1. View content: python scripts/quick_actions.py view_{ch.replace('_', '')}")
            print(f"2. Open platform: {urls.get(ch, 'N/A')}")
            print(f"3. Post the content")
            print(f"4. Mark done: python scripts/quick_actions.py mark_posted {ch}")
            return
    
    print(f"\n{GREEN}✓ All channels posted! Focus on engagement and monitoring.{END}")


def view_network_content():
    """View network building content"""
    if NETWORK_DIR.exists():
        files = sorted(NETWORK_DIR.glob("*.md"))
        print(f"\n{BOLD}Network Building Content:{END}")
        for f in files:
            print(f"  • {f.name}")
        print(f"\nView with: cat {NETWORK_DIR}/<filename>")
    else:
        print("Network content directory not found")


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
        elif action == "view_ih" or action == "view_indiehackers":
            view_content("INDIEHACKERS_launch.txt")
        elif action == "view_network":
            view_network_content()
        elif action == "check_status" or action == "status":
            check_status()
        elif action == "mark_posted" and len(sys.argv) > 2:
            mark_posted(sys.argv[2])
        elif action == "add_revenue" and len(sys.argv) > 2:
            add_revenue(sys.argv[2])
        elif action == "next":
            get_next_action()
        elif action == "daily_report":
            check_status()
        elif action == "open_shopier":
            webbrowser.open("https://www.shopier.com/seller")
            print(f"{GREEN}✓ Opened Shopier{END}")
        elif action == "open_linkedin":
            webbrowser.open("https://www.linkedin.com/feed/")
            print(f"{GREEN}✓ Opened LinkedIn{END}")
        elif action == "open_twitter":
            webbrowser.open("https://twitter.com/compose/tweet")
            print(f"{GREEN}✓ Opened Twitter{END}")
        elif action == "open_reddit":
            webbrowser.open("https://www.reddit.com/r/Entrepreneur/submit")
            print(f"{GREEN}✓ Opened Reddit{END}")
        elif action == "commander":
            import os
            os.system(f"python {PROJECT_ROOT}/scripts/mission_commander.py")
        elif action == "assist":
            import os
            os.system(f"python {PROJECT_ROOT}/scripts/execution_assistant.py")
        else:
            show_menu()
