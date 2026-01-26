"""
Brand Director - Owns Lazy Larry identity, social presence, community engagement
Reports to Commander with brand and network KPIs
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .base_director import BaseDirector, DirectorTask


class BrandDirector(BaseDirector):
    """
    Director of Brand & Community
    
    Responsibilities:
    - Lazy Larry brand identity and voice
    - Social media presence across platforms
    - Community engagement and network expansion
    - Content consistency and brand guidelines
    
    KPIs:
    - Social followers (combined)
    - Engagement rate
    - Community memberships
    - Brand mentions
    - Content output
    """
    
    SOCIAL_PLATFORMS = {
        "linkedin": {
            "url": "https://www.linkedin.com/in/lazy-larry-344631373/",
            "handle": "lazy-larry-344631373",
        },
        "twitter": {
            "url": "https://x.com/lazylarries",
            "handle": "@lazylarries",
        },
        "facebook": {
            "url": "https://www.facebook.com/profile.php?id=61578065763242",
            "handle": "LazyLarryAutonomaX",
        },
        "instagram": {
            "url": None,  # To be created
            "handle": "@lazylarry.autonomax",
        },
        "youtube": {
            "url": None,  # To be created
            "handle": "@LazyLarryAutonomaX",
        },
    }
    
    FOCUS_COMMUNITIES = [
        {"name": "Indie Hackers", "platform": "web", "url": "https://www.indiehackers.com/", "priority": 1},
        {"name": "r/Entrepreneur", "platform": "reddit", "url": "https://reddit.com/r/Entrepreneur", "priority": 1},
        {"name": "r/passive_income", "platform": "reddit", "url": "https://reddit.com/r/passive_income", "priority": 1},
        {"name": "r/SideProject", "platform": "reddit", "url": "https://reddit.com/r/SideProject", "priority": 2},
        {"name": "Digital Nomads", "platform": "facebook", "url": None, "priority": 2},
        {"name": "Etsy Sellers", "platform": "facebook", "url": None, "priority": 2},
        {"name": "Shopify Entrepreneurs", "platform": "facebook", "url": None, "priority": 3},
        {"name": "No-Code Founders", "platform": "slack", "url": None, "priority": 3},
    ]
    
    def __init__(self):
        super().__init__(
            name="Director of Brand & Community",
            domain="brand"
        )
        self.content_calendar: List[Dict] = []
        self.community_memberships: List[str] = []
    
    def _initialize_kpis(self):
        """Initialize brand-specific KPIs"""
        # Social Presence KPIs
        self.kpis.add_metric("linkedin_connections", target=1000, unit="connections", period="monthly")
        self.kpis.add_metric("twitter_followers", target=2000, unit="followers", period="monthly")
        self.kpis.add_metric("combined_followers", target=5000, unit="followers", period="monthly")
        
        # Engagement KPIs
        self.kpis.add_metric("engagement_rate", target=5.0, unit="%", period="weekly")
        self.kpis.add_metric("posts_per_week", target=15, unit="posts", period="weekly")
        self.kpis.add_metric("replies_per_week", target=50, unit="replies", period="weekly")
        
        # Community KPIs
        self.kpis.add_metric("communities_joined", target=8, unit="communities", period="monthly")
        self.kpis.add_metric("community_posts", target=20, unit="posts", period="monthly")
        
        # Brand KPIs
        self.kpis.add_metric("brand_mentions", target=50, unit="mentions", period="monthly")
        self.kpis.add_metric("dm_conversations", target=30, unit="conversations", period="monthly")
        self.kpis.add_metric("leads_from_social", target=20, unit="leads", period="monthly")
    
    def execute_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Execute brand-specific tasks"""
        task_type = task.title.lower()
        
        if "profile" in task_type or "update" in task_type:
            return self._update_social_profiles(task)
        
        elif "community" in task_type or "join" in task_type:
            return self._join_community(task)
        
        elif "content" in task_type or "post" in task_type:
            return self._create_content(task)
        
        elif "engage" in task_type or "reply" in task_type:
            return self._engage_community(task)
        
        else:
            return self._generic_brand_task(task)
    
    def _update_social_profiles(self, task: DirectorTask) -> Dict[str, Any]:
        """Update social media profiles with brand content"""
        # Reference the ready-to-deploy content
        content_path = "docs/brand/SOCIAL_PROFILE_CONTENT.md"
        
        updates = []
        for platform, info in self.SOCIAL_PLATFORMS.items():
            if info["url"]:
                updates.append({
                    "platform": platform,
                    "url": info["url"],
                    "status": "ready_for_update",
                    "content_source": content_path,
                })
            else:
                updates.append({
                    "platform": platform,
                    "handle": info["handle"],
                    "status": "needs_creation",
                })
        
        self.log_execution("update_social_profiles", {"updates": updates})
        return {
            "action": "profile_updates_prepared",
            "platforms": len(updates),
            "updates": updates,
        }
    
    def _join_community(self, task: DirectorTask) -> Dict[str, Any]:
        """Join and introduce to a community"""
        community_name = task.description
        
        # Find community in focus list
        community = next(
            (c for c in self.FOCUS_COMMUNITIES if c["name"].lower() in community_name.lower()),
            None
        )
        
        if community:
            self.community_memberships.append(community["name"])
            self.kpis.increment_metric("communities_joined", 1)
            
            # Generate introduction post
            intro = self._generate_community_intro(community)
            
            return {
                "action": "community_joined",
                "community": community["name"],
                "platform": community["platform"],
                "url": community["url"],
                "intro_post": intro,
            }
        
        return {"action": "community_not_found", "query": community_name}
    
    def _generate_community_intro(self, community: Dict) -> str:
        """Generate community-specific introduction"""
        base_intro = """Hey everyone! 👋

I'm Larry (yes, Lazy Larry - I own it).

Founder of Propulse-AutonomaX, building automation systems for solopreneurs.

Background: Escaped the 80-hour grind by obsessing over automation.

Currently building:
• AutonomaX - AI business operating system
• Zen Collections - Digital art products
• Automation playbooks and templates

Here to learn from this community and share what's working.

What's everyone working on?"""
        
        # Customize for platform
        if community["platform"] == "reddit":
            return base_intro.replace("👋", "").replace("•", "-")
        
        return base_intro
    
    def _create_content(self, task: DirectorTask) -> Dict[str, Any]:
        """Create content for social media"""
        content_type = task.description.lower()
        
        content_templates = {
            "value_post": self._generate_value_post(),
            "story": self._generate_story_post(),
            "engagement": self._generate_engagement_post(),
            "product": self._generate_product_post(),
        }
        
        # Match content type
        for key, content in content_templates.items():
            if key in content_type:
                self.kpis.increment_metric("posts_per_week", 1)
                return {"action": "content_created", "type": key, "content": content}
        
        # Default to value post
        self.kpis.increment_metric("posts_per_week", 1)
        return {"action": "content_created", "type": "value_post", "content": content_templates["value_post"]}
    
    def _generate_value_post(self) -> Dict[str, str]:
        """Generate a value-focused post"""
        return {
            "linkedin": """🚀 The "Set It and Forget It" System

I spent 2 hours setting up this email sequence 18 months ago.

Since then:
→ 500+ customers onboarded automatically
→ 0 hours spent on welcome emails
→ 4.8/5 average satisfaction

The sequence:
• Day 0: Welcome + downloads
• Day 1: Quick win tutorial
• Day 3: Check-in
• Day 7: Bonus resource

The lazy way is the smart way.

What's your best automation win?

#Automation #PassiveIncome #Solopreneur""",
            "twitter": """I spent 2 hours setting up an email sequence 18 months ago.

Since then:
• 500+ customers onboarded
• 0 hours on welcome emails
• 4.8/5 satisfaction

The lazy way is the smart way.

What's your best automation? 🧵""",
        }
    
    def _generate_story_post(self) -> Dict[str, str]:
        """Generate a story-focused post"""
        return {
            "linkedin": """3 years ago I was working 80-hour weeks.

Today I work 20 hours and make more money.

The difference? I stopped trading time for money and started building systems.

Here's what changed:
1. Automated all repetitive tasks
2. Built products that sell while I sleep
3. Set up systems that handle customers 24/7

The hardest part? Accepting that "lazy" is actually smart.

What's one task you wish you could automate?

#Entrepreneurship #Automation #WorkSmarter""",
            "twitter": """3 years ago: 80-hour weeks, burning out

Today: 20 hours/week, making more

The shift? I stopped hustling and started automating.

The "lazy" way turned out to be the smart way.""",
        }
    
    def _generate_engagement_post(self) -> Dict[str, str]:
        """Generate an engagement-focused post"""
        return {
            "linkedin": """Quick poll for the solopreneurs:

What's your biggest time sink right now?

A) Customer support inquiries
B) Content creation
C) Order fulfillment
D) Admin/bookkeeping

Drop your answer below - I'll share automation solutions for the top pick.

#Productivity #Automation""",
            "twitter": """Solopreneurs - what eats most of your time?

A) Customer support
B) Content creation
C) Order fulfillment
D) Admin tasks

Reply with your pick 👇""",
        }
    
    def _generate_product_post(self) -> Dict[str, str]:
        """Generate a product-focused post"""
        return {
            "linkedin": """📦 New: AutonomaX Mastery Pack

Everything you need to build automated income:
✅ 50+ Zen Art Printables
✅ Creator Launch Templates
✅ Platform Playbooks
✅ 50+ Automation SOPs
✅ Notion Revenue Dashboard

$2,847 value → $497 launch price

Link in comments 👇

#DigitalProducts #PassiveIncome""",
            "twitter": """📦 AutonomaX Mastery Pack is live

50+ digital products
Launch templates
Automation SOPs
Revenue dashboard

$2,847 value → $497

#buildinpublic""",
        }
    
    def _engage_community(self, task: DirectorTask) -> Dict[str, Any]:
        """Engage with community through replies and comments"""
        self.kpis.increment_metric("replies_per_week", 1)
        return {
            "action": "community_engagement",
            "type": "reply",
            "guidance": "Reply with value, no direct selling, ask follow-up questions",
        }
    
    def _generic_brand_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Handle generic brand tasks"""
        return {
            "action": "task_acknowledged",
            "task": task.title,
            "status": "queued_for_manual_review",
        }
    
    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """Get prioritized actions to improve brand KPIs"""
        actions = []
        
        # Check at-risk KPIs and generate actions
        at_risk = self.kpis.get_at_risk()
        
        if "communities_joined" in at_risk:
            for community in self.FOCUS_COMMUNITIES[:3]:
                if community["name"] not in self.community_memberships:
                    actions.append({
                        "action": "join_community",
                        "target": community["name"],
                        "priority": community["priority"],
                        "kpi_impact": ["communities_joined", "community_posts"],
                    })
        
        if "posts_per_week" in at_risk:
            actions.append({
                "action": "create_content_batch",
                "target": "5 posts (2 LinkedIn, 2 Twitter, 1 cross-platform)",
                "priority": 1,
                "kpi_impact": ["posts_per_week", "engagement_rate"],
            })
        
        if "linkedin_connections" in at_risk:
            actions.append({
                "action": "linkedin_outreach",
                "target": "Send 10 connection requests to target audience",
                "priority": 2,
                "kpi_impact": ["linkedin_connections", "leads_from_social"],
            })
        
        if "engagement_rate" in at_risk:
            actions.append({
                "action": "engagement_push",
                "target": "Reply to 20 posts in target communities",
                "priority": 2,
                "kpi_impact": ["engagement_rate", "replies_per_week"],
            })
        
        # Always have baseline actions
        if not actions:
            actions = [
                {"action": "daily_content", "target": "Post 1 value post", "priority": 3},
                {"action": "community_engage", "target": "10 thoughtful replies", "priority": 3},
                {"action": "dm_check", "target": "Respond to all DMs", "priority": 2},
            ]
        
        return sorted(actions, key=lambda x: x.get("priority", 5))
    
    def get_content_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate content calendar for upcoming days"""
        calendar = []
        today = datetime.utcnow()
        
        content_schedule = [
            {"day": 0, "type": "value_post", "platforms": ["linkedin", "twitter"]},
            {"day": 1, "type": "engagement", "platforms": ["twitter"]},
            {"day": 2, "type": "story", "platforms": ["linkedin"]},
            {"day": 3, "type": "value_post", "platforms": ["twitter", "facebook"]},
            {"day": 4, "type": "engagement", "platforms": ["linkedin"]},
            {"day": 5, "type": "product", "platforms": ["linkedin", "twitter"]},
            {"day": 6, "type": "behind_scenes", "platforms": ["twitter", "instagram"]},
        ]
        
        for schedule in content_schedule[:days]:
            date = today + timedelta(days=schedule["day"])
            calendar.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "content_type": schedule["type"],
                "platforms": schedule["platforms"],
                "status": "scheduled",
            })
        
        return calendar
