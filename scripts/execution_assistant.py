#!/usr/bin/env python3
"""
AUTONOMAX EXECUTION ASSISTANT
=============================

AI-powered assistant for business mission execution.
Provides contextual help, generates content variations, and tracks progress.

Features:
- Contextual next-action recommendations
- Content adaptation for different platforms
- Progress tracking with milestone celebrations
- Intelligent reminders and follow-ups
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import textwrap

PROJECT_ROOT = Path(__file__).parent.parent
TRACKER_PATH = PROJECT_ROOT / "autonomax" / "execution_tracker.json"
CONTENT_DIR = PROJECT_ROOT / "marketing_outputs" / "traffic_supply"
NETWORK_DIR = PROJECT_ROOT / "marketing_outputs" / "network_building"


class ExecutionAssistant:
    """AI-powered execution assistant"""
    
    def __init__(self):
        self.tracker = self._load_tracker()
        self.session_start = datetime.now()
        self.actions_taken = []
    
    def _load_tracker(self) -> Dict:
        if TRACKER_PATH.exists():
            return json.loads(TRACKER_PATH.read_text())
        return {}
    
    def _save_tracker(self):
        TRACKER_PATH.write_text(json.dumps(self.tracker, indent=2))
    
    def get_context(self) -> Dict:
        """Get current execution context"""
        channels = self.tracker.get('channels', {})
        revenue = self.tracker.get('revenue', {})
        
        posted_channels = [ch for ch, data in channels.items() if data.get('posted')]
        pending_channels = [ch for ch, data in channels.items() if not data.get('posted')]
        
        return {
            "posted_count": len(posted_channels),
            "pending_count": len(pending_channels),
            "posted_channels": posted_channels,
            "pending_channels": pending_channels,
            "revenue_current": revenue.get('current', 0),
            "revenue_target": revenue.get('target', 500),
            "orders": len(revenue.get('orders', [])),
            "target_date": self.tracker.get('target_date', ''),
            "mission": self.tracker.get('mission', 'Revenue Sprint'),
        }
    
    def get_priority_action(self) -> Dict:
        """Determine the single most important next action"""
        ctx = self.get_context()
        
        # Decision tree for priority
        if ctx['posted_count'] == 0:
            return {
                "action": "POST_LINKEDIN",
                "title": "Post to LinkedIn",
                "reason": "LinkedIn is your highest-value professional network. Start here for credibility.",
                "urgency": "HIGH",
                "time_estimate": "5 minutes",
                "instructions": self._get_linkedin_instructions(),
            }
        
        if 'twitter' in ctx['pending_channels']:
            return {
                "action": "POST_TWITTER",
                "title": "Post Twitter Thread",
                "reason": "Twitter threads get high engagement. Your build-in-public story resonates here.",
                "urgency": "HIGH",
                "time_estimate": "10 minutes",
                "instructions": self._get_twitter_instructions(),
            }
        
        if 'reddit' in ctx['pending_channels']:
            return {
                "action": "POST_REDDIT",
                "title": "Post Reddit Value Content",
                "reason": "Reddit has highly engaged communities. Share value, not pitches.",
                "urgency": "MEDIUM",
                "time_estimate": "5 minutes",
                "instructions": self._get_reddit_instructions(),
            }
        
        if 'indie_hackers' in ctx['pending_channels']:
            return {
                "action": "POST_IH",
                "title": "Post on Indie Hackers",
                "reason": "Perfect audience of builders who appreciate your journey.",
                "urgency": "MEDIUM",
                "time_estimate": "10 minutes",
                "instructions": self._get_ih_instructions(),
            }
        
        if ctx['posted_count'] >= 4 and ctx['revenue_current'] == 0:
            return {
                "action": "ENGAGE",
                "title": "Engage with Responses",
                "reason": "Engagement drives algorithm visibility. Respond to every comment.",
                "urgency": "HIGH",
                "time_estimate": "15 minutes",
                "instructions": [
                    "1. Check each platform you posted to",
                    "2. Respond to EVERY comment within 2 hours",
                    "3. Ask follow-up questions to keep conversation going",
                    "4. Thank people genuinely",
                    "5. DO NOT pitch in comments - provide value only",
                ],
            }
        
        if ctx['revenue_current'] >= ctx['revenue_target']:
            return {
                "action": "CELEBRATE",
                "title": "🎉 Target Reached!",
                "reason": "You hit your revenue target! Time to set a new goal.",
                "urgency": "LOW",
                "instructions": [
                    "1. Celebrate this win!",
                    "2. Document what worked",
                    "3. Set next target (2x current)",
                    "4. Continue engagement momentum",
                ],
            }
        
        return {
            "action": "MONITOR",
            "title": "Monitor & Optimize",
            "reason": "Content is live. Now monitor, engage, and optimize.",
            "urgency": "LOW",
            "time_estimate": "10 minutes",
            "instructions": [
                "1. Check analytics on each platform",
                "2. Identify top-performing content",
                "3. Double down on what works",
                "4. Respond to any new engagement",
            ],
        }
    
    def _get_linkedin_instructions(self) -> List[str]:
        return [
            "1. Open: https://www.linkedin.com/feed/",
            "2. Click 'Start a post'",
            "3. Paste content from: marketing_outputs/traffic_supply/LINKEDIN_post.txt",
            "4. Add 3-5 relevant hashtags",
            "5. Post and engage with comments for first hour",
        ]
    
    def _get_twitter_instructions(self) -> List[str]:
        return [
            "1. Open: https://twitter.com/compose/tweet",
            "2. Copy FIRST tweet from TWITTER_thread.txt",
            "3. Post, then reply to yourself with next tweet",
            "4. Continue until thread is complete",
            "5. Pin the thread to your profile",
        ]
    
    def _get_reddit_instructions(self) -> List[str]:
        return [
            "1. Choose subreddit: r/Entrepreneur or r/SideProject",
            "2. Read the rules first!",
            "3. Post value content (NO direct links)",
            "4. Use content from REDDIT_r_Entrepreneur.txt",
            "5. Respond to comments genuinely",
        ]
    
    def _get_ih_instructions(self) -> List[str]:
        return [
            "1. Open: https://www.indiehackers.com/new-post",
            "2. Use content from INDIEHACKERS_launch.txt",
            "3. Choose relevant group (Product, Side Project, etc.)",
            "4. Engage with commenters",
            "5. Check back in 24 hours",
        ]
    
    def generate_progress_report(self) -> str:
        """Generate a progress report"""
        ctx = self.get_context()
        
        # Calculate progress percentage
        channel_progress = ctx['posted_count'] / max(1, ctx['posted_count'] + ctx['pending_count']) * 50
        revenue_progress = min(50, ctx['revenue_current'] / max(1, ctx['revenue_target']) * 50)
        total_progress = channel_progress + revenue_progress
        
        # Progress bar
        bar_filled = int(total_progress / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    EXECUTION PROGRESS REPORT                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Mission: {ctx['mission'][:50]:<50} ║
║  Target Date: {ctx['target_date']:<52} ║
║                                                                      ║
║  Overall Progress: [{bar}] {total_progress:.0f}%                 ║
║                                                                      ║
║  CHANNELS                                                            ║
║  ├─ Posted: {ctx['posted_count']}/{ctx['posted_count'] + ctx['pending_count']:<54} ║
║  └─ Remaining: {', '.join(ctx['pending_channels'][:4]) if ctx['pending_channels'] else 'None':<47} ║
║                                                                      ║
║  REVENUE                                                             ║
║  ├─ Current: ${ctx['revenue_current']:<55} ║
║  ├─ Target: ${ctx['revenue_target']:<56} ║
║  └─ Orders: {ctx['orders']:<56} ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        return report
    
    def get_motivational_message(self) -> str:
        """Get a contextual motivational message"""
        ctx = self.get_context()
        
        if ctx['posted_count'] == 0:
            return "🚀 The journey begins! Your first post is the hardest. After that, momentum takes over."
        elif ctx['posted_count'] == 1:
            return "💪 One down! You're building momentum. Each post compounds your reach."
        elif ctx['posted_count'] < 4:
            return "🔥 You're on fire! Keep going - consistency beats perfection."
        elif ctx['revenue_current'] == 0:
            return "📊 Content is out there working for you. Focus on engagement now."
        elif ctx['revenue_current'] > 0:
            return f"💰 ${ctx['revenue_current']} and counting! Your system is working."
        else:
            return "⭐ Keep pushing. Every action compounds over time."
    
    def mark_channel_posted(self, channel: str):
        """Mark a channel as posted"""
        if channel in self.tracker.get('channels', {}):
            self.tracker['channels'][channel]['posted'] = True
            self.tracker['channels'][channel]['posted_at'] = datetime.now().isoformat()
            self._save_tracker()
            self.actions_taken.append(f"Posted to {channel}")
            return True
        return False
    
    def add_revenue(self, amount: float):
        """Record revenue"""
        if 'revenue' not in self.tracker:
            self.tracker['revenue'] = {'target': 500, 'current': 0, 'orders': []}
        
        self.tracker['revenue']['current'] += amount
        self.tracker['revenue']['orders'].append({
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        })
        self._save_tracker()
        self.actions_taken.append(f"Added ${amount} revenue")
    
    def run_interactive(self):
        """Run interactive assistant mode"""
        print("\n" + "=" * 70)
        print("AUTONOMAX EXECUTION ASSISTANT")
        print("=" * 70)
        
        print(self.generate_progress_report())
        print(self.get_motivational_message())
        
        print("\n" + "-" * 70)
        print("PRIORITY ACTION:")
        print("-" * 70)
        
        action = self.get_priority_action()
        print(f"\n🎯 {action['title']}")
        print(f"   Reason: {action['reason']}")
        if 'time_estimate' in action:
            print(f"   Time: {action['time_estimate']}")
        print(f"   Urgency: {action.get('urgency', 'MEDIUM')}")
        
        print("\n   Steps:")
        for step in action.get('instructions', []):
            print(f"   {step}")
        
        print("\n" + "-" * 70)
        print("COMMANDS:")
        print("  [d] Mark current action as done")
        print("  [r] Record revenue")
        print("  [s] Show full status")
        print("  [q] Quit")
        print("-" * 70)
        
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'd':
                # Determine which channel to mark
                ctx = self.get_context()
                if ctx['pending_channels']:
                    channel = ctx['pending_channels'][0]
                    self.mark_channel_posted(channel)
                    print(f"✓ Marked {channel} as posted!")
                    # Get next action
                    action = self.get_priority_action()
                    print(f"\n🎯 Next: {action['title']}")
                else:
                    print("All channels already posted!")
            
            elif cmd == 'r':
                try:
                    amount = float(input("Amount ($): "))
                    self.add_revenue(amount)
                    print(f"✓ Added ${amount}. Total: ${self.tracker['revenue']['current']}")
                except ValueError:
                    print("Invalid amount")
            
            elif cmd == 's':
                print(self.generate_progress_report())
            
            elif cmd == 'q':
                print("\n✨ Great progress! Keep executing!")
                break
            
            else:
                print("Unknown command. Use: d, r, s, q")


def main():
    assistant = ExecutionAssistant()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "status":
            print(assistant.generate_progress_report())
        elif cmd == "next":
            action = assistant.get_priority_action()
            print(f"\n🎯 NEXT ACTION: {action['title']}")
            print(f"   {action['reason']}")
            for step in action.get('instructions', [])[:3]:
                print(f"   {step}")
        elif cmd == "motivation":
            print(f"\n{assistant.get_motivational_message()}")
        else:
            assistant.run_interactive()
    else:
        assistant.run_interactive()


if __name__ == "__main__":
    main()
