#!/usr/bin/env python3
"""
AUTONOMAX MISSION COMMANDER v2.0
================================

A unified, intuitive interface for business mission accomplishment.

Design Principles:
- CREATIVITY: AI-assisted content and idea generation
- CONSTRUCTABILITY: Clear steps with validation at each stage
- COMFORTABILITY: Guided experience with helpful prompts

Usage:
    python scripts/mission_commander.py              # Interactive menu
    python scripts/mission_commander.py sprint       # Launch revenue sprint
    python scripts/mission_commander.py post         # Post content wizard
    python scripts/mission_commander.py status       # Full status dashboard
    python scripts/mission_commander.py assist       # Get next best action
"""

import json
import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import textwrap

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRACKER_PATH = PROJECT_ROOT / "autonomax" / "execution_tracker.json"
CONTENT_DIR = PROJECT_ROOT / "marketing_outputs" / "traffic_supply"
NETWORK_DIR = PROJECT_ROOT / "marketing_outputs" / "network_building"
STATE_PATH = PROJECT_ROOT / "autonomax_state.json"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def color(text: str, c: str) -> str:
    """Wrap text in color codes"""
    return f"{c}{text}{Colors.ENDC}"


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header(title: str, subtitle: str = ""):
    """Print a styled header"""
    width = 70
    print()
    print(color("╔" + "═" * (width-2) + "╗", Colors.CYAN))
    print(color("║", Colors.CYAN) + color(f" {title:^{width-4}} ", Colors.BOLD) + color("║", Colors.CYAN))
    if subtitle:
        print(color("║", Colors.CYAN) + color(f" {subtitle:^{width-4}} ", Colors.DIM) + color("║", Colors.CYAN))
    print(color("╚" + "═" * (width-2) + "╝", Colors.CYAN))
    print()


def print_box(content: List[str], title: str = "", color_code: str = Colors.GREEN):
    """Print content in a box"""
    width = 68
    print(color("┌" + "─" * width + "┐", color_code))
    if title:
        print(color("│", color_code) + color(f" {title}", Colors.BOLD) + " " * (width - len(title) - 1) + color("│", color_code))
        print(color("├" + "─" * width + "┤", color_code))
    for line in content:
        # Truncate long lines
        display_line = line[:width-2] if len(line) > width-2 else line
        padding = width - len(display_line) - 1
        print(color("│", color_code) + f" {display_line}" + " " * padding + color("│", color_code))
    print(color("└" + "─" * width + "┘", color_code))


def load_tracker() -> Dict:
    """Load execution tracker"""
    if TRACKER_PATH.exists():
        return json.loads(TRACKER_PATH.read_text())
    return {
        "mission": "First $500 Revenue Sprint",
        "target_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "revenue": {"target": 500, "current": 0, "orders": []},
        "channels": {
            "linkedin": {"status": "READY", "posted": False},
            "twitter": {"status": "READY", "posted": False},
            "reddit": {"status": "READY", "posted": False},
            "indie_hackers": {"status": "READY", "posted": False},
            "facebook": {"status": "READY", "posted": False},
            "quora": {"status": "READY", "posted": False},
            "medium": {"status": "READY", "posted": False},
            "product_hunt": {"status": "SCHEDULED", "posted": False},
        },
        "kpis": {}
    }


def save_tracker(tracker: Dict):
    """Save execution tracker"""
    TRACKER_PATH.parent.mkdir(exist_ok=True)
    TRACKER_PATH.write_text(json.dumps(tracker, indent=2))


def get_shopier_status() -> Dict:
    """Get Shopier store status"""
    try:
        from dotenv import load_dotenv
        import requests
        load_dotenv()
        token = os.getenv("SHOPIER_PERSONAL_ACCESS_TOKEN")
        if token:
            resp = requests.get(
                "https://api.shopier.com/v1/products",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if resp.status_code == 200:
                products = resp.json()
                total_value = sum(float(p.get('priceData', {}).get('price', 0) or 0) for p in products)
                return {
                    "status": "LIVE",
                    "products": len(products),
                    "value": total_value,
                    "url": "https://www.shopier.com/autonomax"
                }
    except:
        pass
    return {"status": "OFFLINE", "products": 0, "value": 0, "url": ""}


# =============================================================================
# MAIN MENU SYSTEM
# =============================================================================

def show_main_menu():
    """Display main interactive menu"""
    clear_screen()
    print_header("AUTONOMAX MISSION COMMANDER", "Business Execution System v2.0")
    
    tracker = load_tracker()
    shopier = get_shopier_status()
    
    # Quick status
    posted = sum(1 for ch in tracker.get('channels', {}).values() if ch.get('posted'))
    total_channels = len(tracker.get('channels', {}))
    revenue = tracker.get('revenue', {}).get('current', 0)
    target = tracker.get('revenue', {}).get('target', 500)
    
    status_lines = [
        f"Mission: {tracker.get('mission', 'N/A')}",
        f"Revenue: ${revenue} / ${target} ({revenue/target*100:.0f}%)" if target > 0 else "Revenue: $0",
        f"Channels: {posted}/{total_channels} posted",
        f"Store: {shopier['status']} ({shopier['products']} products)",
    ]
    print_box(status_lines, "CURRENT STATUS", Colors.BLUE)
    
    print()
    menu_options = [
        ("1", "🚀 Launch Sprint", "Start guided revenue sprint"),
        ("2", "📝 Post Content", "Wizard to post on channels"),
        ("3", "📊 Full Dashboard", "Complete status & analytics"),
        ("4", "🎯 Next Best Action", "AI-recommended next step"),
        ("5", "💰 Log Revenue", "Record a sale"),
        ("6", "🌐 Open Store", "Open Shopier in browser"),
        ("7", "📋 View Content", "Browse ready content"),
        ("8", "🔧 System Tools", "Advanced operations"),
        ("0", "Exit", ""),
    ]
    
    print(color("  SELECT AN ACTION:", Colors.BOLD))
    print()
    for key, title, desc in menu_options:
        if desc:
            print(f"    [{color(key, Colors.CYAN)}] {title}")
            print(f"        {color(desc, Colors.DIM)}")
        else:
            print(f"    [{color(key, Colors.CYAN)}] {title}")
    
    print()
    return input(color("  Enter choice: ", Colors.YELLOW)).strip()


def post_content_wizard():
    """Guided wizard for posting content"""
    clear_screen()
    print_header("POST CONTENT WIZARD", "Step-by-step content deployment")
    
    tracker = load_tracker()
    
    # Show pending channels
    pending = [(ch, data) for ch, data in tracker.get('channels', {}).items() if not data.get('posted')]
    
    if not pending:
        print(color("  ✓ All channels have been posted to!", Colors.GREEN))
        input("\n  Press Enter to continue...")
        return
    
    print(color("  PENDING CHANNELS:", Colors.BOLD))
    print()
    for i, (ch, _) in enumerate(pending, 1):
        print(f"    [{i}] {ch.replace('_', ' ').title()}")
    print(f"    [0] Back to menu")
    
    print()
    choice = input(color("  Select channel to post: ", Colors.YELLOW)).strip()
    
    if choice == "0" or not choice:
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(pending):
            channel, _ = pending[idx]
            post_to_channel(channel, tracker)
    except ValueError:
        pass


def post_to_channel(channel: str, tracker: Dict):
    """Guide user through posting to a specific channel"""
    clear_screen()
    print_header(f"POST TO {channel.upper()}", "Follow the steps below")
    
    # Channel-specific content and instructions
    channel_info = {
        "linkedin": {
            "file": "LINKEDIN_post.txt",
            "url": "https://www.linkedin.com/feed/",
            "steps": [
                "1. Copy the content below",
                "2. Go to LinkedIn (will open in browser)",
                "3. Click 'Start a post'",
                "4. Paste and post!",
                "5. Come back and confirm"
            ]
        },
        "twitter": {
            "file": "TWITTER_thread.txt",
            "url": "https://twitter.com/compose/tweet",
            "steps": [
                "1. Copy each tweet from the thread",
                "2. Go to Twitter (will open in browser)",
                "3. Post as a thread (reply to yourself)",
                "4. Come back and confirm"
            ]
        },
        "reddit": {
            "file": "REDDIT_r_Entrepreneur.txt",
            "url": "https://www.reddit.com/r/Entrepreneur/submit",
            "steps": [
                "1. Copy the content below",
                "2. Go to subreddit (will open in browser)",
                "3. Create a new text post",
                "4. DO NOT include direct links!",
                "5. Come back and confirm"
            ]
        },
        "indie_hackers": {
            "file": "INDIEHACKERS_launch.txt",
            "url": "https://www.indiehackers.com/new-post",
            "steps": [
                "1. Copy the content below",
                "2. Go to Indie Hackers (will open in browser)",
                "3. Create a new post",
                "4. Come back and confirm"
            ]
        },
        "facebook": {
            "file": "FACEBOOK_groups.txt",
            "url": "https://www.facebook.com/groups/",
            "steps": [
                "1. Copy the content below",
                "2. Go to your target Facebook groups",
                "3. Create posts in 2-3 groups",
                "4. Come back and confirm"
            ]
        },
        "quora": {
            "file": "QUORA_answers.txt",
            "url": "https://www.quora.com/",
            "steps": [
                "1. Review the answer templates",
                "2. Find relevant questions on Quora",
                "3. Answer 2-3 questions using templates",
                "4. Come back and confirm"
            ]
        },
        "medium": {
            "file": "MEDIUM_article.txt",
            "url": "https://medium.com/new-story",
            "steps": [
                "1. Copy the article content",
                "2. Go to Medium (will open in browser)",
                "3. Create new story and paste",
                "4. Add tags and publish",
                "5. Come back and confirm"
            ]
        },
        "product_hunt": {
            "file": "PRODUCTHUNT_prep.txt",
            "url": "https://www.producthunt.com/posts/new",
            "steps": [
                "1. Review the prep document",
                "2. Product Hunt launches work best on Tuesday",
                "3. Prepare all assets first",
                "4. Schedule for optimal launch day"
            ]
        }
    }
    
    info = channel_info.get(channel, {"file": None, "url": "", "steps": []})
    
    # Show steps
    print_box(info["steps"], "STEPS", Colors.CYAN)
    
    # Show content
    if info["file"]:
        content_path = CONTENT_DIR / info["file"]
        if content_path.exists():
            content = content_path.read_text()
            print()
            print(color("  CONTENT TO POST:", Colors.BOLD))
            print(color("  " + "─" * 66, Colors.DIM))
            # Show first 30 lines
            lines = content.split('\n')[:30]
            for line in lines:
                print(f"  {line[:66]}")
            if len(content.split('\n')) > 30:
                print(color(f"  ... ({len(content.split(chr(10)))-30} more lines)", Colors.DIM))
            print(color("  " + "─" * 66, Colors.DIM))
    
    print()
    actions = [
        "[o] Open URL in browser",
        "[c] Copy content to clipboard",
        "[d] Mark as DONE",
        "[b] Back"
    ]
    print("  " + "  ".join(actions))
    print()
    
    while True:
        action = input(color("  Action: ", Colors.YELLOW)).strip().lower()
        
        if action == 'o':
            webbrowser.open(info["url"])
            print(color("  ✓ Opened in browser", Colors.GREEN))
        elif action == 'c':
            if info["file"]:
                content_path = CONTENT_DIR / info["file"]
                if content_path.exists():
                    content = content_path.read_text()
                    try:
                        subprocess.run(['pbcopy'], input=content.encode(), check=True)
                        print(color("  ✓ Content copied to clipboard!", Colors.GREEN))
                    except:
                        print(color("  Content is displayed above - copy manually", Colors.YELLOW))
        elif action == 'd':
            tracker['channels'][channel]['posted'] = True
            tracker['channels'][channel]['posted_at'] = datetime.now().isoformat()
            save_tracker(tracker)
            print(color(f"  ✓ {channel} marked as posted!", Colors.GREEN))
            input("\n  Press Enter to continue...")
            return
        elif action == 'b':
            return


def show_full_dashboard():
    """Display comprehensive dashboard"""
    clear_screen()
    print_header("MISSION DASHBOARD", "Complete Status Overview")
    
    tracker = load_tracker()
    shopier = get_shopier_status()
    
    # Revenue Section
    revenue = tracker.get('revenue', {})
    current = revenue.get('current', 0)
    target = revenue.get('target', 500)
    progress = (current / target * 100) if target > 0 else 0
    bar_filled = int(progress / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    
    revenue_lines = [
        f"Target: ${target}",
        f"Current: ${current}",
        f"Progress: [{bar}] {progress:.0f}%",
        f"Orders: {len(revenue.get('orders', []))}",
    ]
    print_box(revenue_lines, "💰 REVENUE", Colors.GREEN)
    
    # Store Section
    store_lines = [
        f"Status: {shopier['status']}",
        f"Products: {shopier['products']}",
        f"Catalog Value: {shopier['value']:,.0f} TRY",
        f"URL: {shopier['url']}",
        f"Discount: LAZY20 (20% off)",
    ]
    print_box(store_lines, "🏪 SHOPIER STORE", Colors.BLUE)
    
    # Channels Section
    channels = tracker.get('channels', {})
    posted = sum(1 for ch in channels.values() if ch.get('posted'))
    channel_lines = [f"Posted: {posted}/{len(channels)}"]
    for ch, data in channels.items():
        status = "✓" if data.get('posted') else "○"
        channel_lines.append(f"  {status} {ch}")
    print_box(channel_lines, "📢 CHANNELS", Colors.CYAN)
    
    # Content Assets
    traffic_files = len(list(CONTENT_DIR.glob("*.txt"))) if CONTENT_DIR.exists() else 0
    network_files = len(list(NETWORK_DIR.glob("*.md"))) if NETWORK_DIR.exists() else 0
    asset_lines = [
        f"Traffic Supply: {traffic_files} files",
        f"Network Building: {network_files} files",
        f"Total Ready: {traffic_files + network_files}",
    ]
    print_box(asset_lines, "📁 CONTENT ASSETS", Colors.YELLOW)
    
    input("\n  Press Enter to continue...")


def get_next_best_action():
    """AI-recommended next action based on current state"""
    clear_screen()
    print_header("NEXT BEST ACTION", "AI-Recommended Priority")
    
    tracker = load_tracker()
    shopier = get_shopier_status()
    
    # Analyze state and recommend
    recommendations = []
    
    # Check channels
    channels = tracker.get('channels', {})
    posted = sum(1 for ch in channels.values() if ch.get('posted'))
    
    if posted == 0:
        recommendations.append({
            "priority": 1,
            "action": "Post to LinkedIn",
            "reason": "LinkedIn has highest professional reach. Start there.",
            "command": "python scripts/mission_commander.py post",
            "time": "5 minutes"
        })
    elif not channels.get('twitter', {}).get('posted'):
        recommendations.append({
            "priority": 1,
            "action": "Post Twitter Thread",
            "reason": "Twitter threads get high engagement for build-in-public content.",
            "command": "Select Twitter in post wizard",
            "time": "10 minutes"
        })
    elif not channels.get('reddit', {}).get('posted'):
        recommendations.append({
            "priority": 1,
            "action": "Post to Reddit",
            "reason": "Reddit communities have high-intent users looking for solutions.",
            "command": "Select Reddit in post wizard",
            "time": "5 minutes"
        })
    elif not channels.get('indie_hackers', {}).get('posted'):
        recommendations.append({
            "priority": 1,
            "action": "Post to Indie Hackers",
            "reason": "Perfect audience for productized services and tools.",
            "command": "Select Indie Hackers in post wizard",
            "time": "10 minutes"
        })
    
    # Revenue check
    revenue = tracker.get('revenue', {}).get('current', 0)
    if revenue == 0 and posted >= 2:
        recommendations.append({
            "priority": 2,
            "action": "Engage with Comments",
            "reason": "Respond to all engagement within 2 hours for algorithm boost.",
            "command": "Check your posted platforms for comments",
            "time": "15 minutes"
        })
    
    # Network building
    if posted >= 4:
        recommendations.append({
            "priority": 3,
            "action": "Start Network Building",
            "reason": "Value-first engagement builds long-term audience.",
            "command": "Comment on 5 posts in target communities (no self-promotion)",
            "time": "20 minutes"
        })
    
    if not recommendations:
        recommendations.append({
            "priority": 1,
            "action": "Monitor & Engage",
            "reason": "All channels posted. Focus on engagement and monitoring.",
            "command": "Check all platforms for responses",
            "time": "10 minutes"
        })
    
    # Display recommendations
    for i, rec in enumerate(recommendations[:3], 1):
        lines = [
            f"Action: {rec['action']}",
            f"Why: {rec['reason']}",
            f"How: {rec['command']}",
            f"Time: {rec['time']}",
        ]
        priority_color = Colors.RED if rec['priority'] == 1 else Colors.YELLOW if rec['priority'] == 2 else Colors.BLUE
        print_box(lines, f"PRIORITY #{i}", priority_color)
        print()
    
    input("  Press Enter to continue...")


def log_revenue():
    """Log a new sale"""
    clear_screen()
    print_header("LOG REVENUE", "Record a Sale")
    
    tracker = load_tracker()
    
    print(f"  Current Revenue: ${tracker.get('revenue', {}).get('current', 0)}")
    print()
    
    amount = input(color("  Enter sale amount ($): ", Colors.YELLOW)).strip()
    
    try:
        amount = float(amount)
        tracker['revenue']['current'] += amount
        tracker['revenue']['orders'].append({
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })
        save_tracker(tracker)
        
        new_total = tracker['revenue']['current']
        target = tracker['revenue']['target']
        
        print()
        print(color(f"  ✓ Added ${amount}!", Colors.GREEN))
        print(f"  New Total: ${new_total} / ${target}")
        
        if new_total >= target:
            print()
            print(color("  🎉 CONGRATULATIONS! TARGET REACHED! 🎉", Colors.GREEN + Colors.BOLD))
    except ValueError:
        print(color("  Invalid amount", Colors.RED))
    
    input("\n  Press Enter to continue...")


def view_content_menu():
    """Browse available content"""
    clear_screen()
    print_header("CONTENT LIBRARY", "Ready-to-Post Content")
    
    content_dirs = [
        ("Traffic Supply", CONTENT_DIR),
        ("Network Building", NETWORK_DIR),
    ]
    
    for name, dir_path in content_dirs:
        if dir_path.exists():
            files = sorted(dir_path.glob("*"))
            file_list = [f.name for f in files if f.is_file()][:10]
            if file_list:
                print_box(file_list, name, Colors.CYAN)
                print()
    
    print("  Enter filename to view, or press Enter to go back")
    filename = input(color("  Filename: ", Colors.YELLOW)).strip()
    
    if filename:
        for _, dir_path in content_dirs:
            filepath = dir_path / filename
            if filepath.exists():
                clear_screen()
                print_header(f"CONTENT: {filename}", "")
                print(filepath.read_text())
                input("\n  Press Enter to continue...")
                return
        print(color("  File not found", Colors.RED))
        input("\n  Press Enter to continue...")


def system_tools_menu():
    """Advanced system tools"""
    clear_screen()
    print_header("SYSTEM TOOLS", "Advanced Operations")
    
    tools = [
        ("1", "Run Monitor Dashboard", "python scripts/monitor_dashboard.py"),
        ("2", "Run Handover Command", "python scripts/handover_command.py"),
        ("3", "Run Command Center", "python scripts/run_command_center.py"),
        ("4", "Check Shopier Products", "python scripts/check_shopier.py"),
        ("5", "Open Shopier Seller Dashboard", "open https://www.shopier.com/seller"),
        ("0", "Back", ""),
    ]
    
    for key, name, cmd in tools:
        print(f"    [{key}] {name}")
        if cmd and key != "0":
            print(color(f"        {cmd}", Colors.DIM))
    
    print()
    choice = input(color("  Select tool: ", Colors.YELLOW)).strip()
    
    for key, name, cmd in tools:
        if choice == key and cmd:
            if cmd.startswith("open "):
                webbrowser.open(cmd[5:])
            else:
                print()
                print(color(f"  Running: {cmd}", Colors.CYAN))
                print()
                os.system(cmd)
                input("\n  Press Enter to continue...")
            return


def launch_sprint():
    """Launch guided revenue sprint"""
    clear_screen()
    print_header("LAUNCH REVENUE SPRINT", "Guided Mission Execution")
    
    tracker = load_tracker()
    
    sprint_plan = [
        ("1", "Post LinkedIn", "linkedin", "5 min"),
        ("2", "Post Twitter Thread", "twitter", "10 min"),
        ("3", "Post Reddit Value Content", "reddit", "5 min"),
        ("4", "Post Indie Hackers Launch", "indie_hackers", "10 min"),
        ("5", "Engage with Comments", None, "15 min"),
        ("6", "Post to Facebook Groups", "facebook", "10 min"),
        ("7", "Answer Quora Questions", "quora", "15 min"),
    ]
    
    print(color("  SPRINT SEQUENCE:", Colors.BOLD))
    print()
    
    for step, name, channel, time in sprint_plan:
        if channel:
            posted = tracker.get('channels', {}).get(channel, {}).get('posted', False)
            status = color("✓ DONE", Colors.GREEN) if posted else color("○ PENDING", Colors.YELLOW)
        else:
            status = color("◐ MANUAL", Colors.BLUE)
        print(f"    [{step}] {name} ({time}) - {status}")
    
    print()
    print("  [s] Start from first pending step")
    print("  [#] Jump to specific step")
    print("  [b] Back to menu")
    print()
    
    choice = input(color("  Choice: ", Colors.YELLOW)).strip().lower()
    
    if choice == 's':
        for step, name, channel, time in sprint_plan:
            if channel and not tracker.get('channels', {}).get(channel, {}).get('posted', False):
                post_to_channel(channel, tracker)
                tracker = load_tracker()  # Reload after each post
                continue_choice = input(color("\n  Continue to next? [y/n]: ", Colors.YELLOW)).strip().lower()
                if continue_choice != 'y':
                    break
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(sprint_plan):
            _, _, channel, _ = sprint_plan[idx]
            if channel:
                post_to_channel(channel, tracker)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point"""
    # Handle command line arguments
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "sprint":
            launch_sprint()
        elif cmd == "post":
            post_content_wizard()
        elif cmd == "status":
            show_full_dashboard()
        elif cmd == "assist" or cmd == "next":
            get_next_best_action()
        elif cmd == "revenue":
            log_revenue()
        elif cmd == "content":
            view_content_menu()
        else:
            print(f"Unknown command: {cmd}")
            print("Available: sprint, post, status, assist, revenue, content")
        return
    
    # Interactive menu loop
    while True:
        choice = show_main_menu()
        
        if choice == "1":
            launch_sprint()
        elif choice == "2":
            post_content_wizard()
        elif choice == "3":
            show_full_dashboard()
        elif choice == "4":
            get_next_best_action()
        elif choice == "5":
            log_revenue()
        elif choice == "6":
            webbrowser.open("https://www.shopier.com/autonomax")
        elif choice == "7":
            view_content_menu()
        elif choice == "8":
            system_tools_menu()
        elif choice == "0":
            clear_screen()
            print(color("\n  Mission Commander signing off. Good luck! 🚀\n", Colors.CYAN))
            break


if __name__ == "__main__":
    main()
