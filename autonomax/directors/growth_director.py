"""
Growth Director - Owns customer acquisition, traffic, marketing, partnerships
Reports to Commander with growth and acquisition KPIs
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .base_director import BaseDirector, DirectorTask


class GrowthDirector(BaseDirector):
    """
    Director of Growth & Acquisition
    
    Responsibilities:
    - Traffic generation (organic & paid)
    - Lead generation and nurturing
    - Email marketing and sequences
    - SEO and content marketing
    - Partnership development
    - Affiliate program management
    
    KPIs:
    - Monthly website traffic
    - Email list size
    - Lead conversion rate
    - Traffic sources breakdown
    - Partnership revenue
    """
    
    TRAFFIC_CHANNELS = [
        {"name": "organic_search", "type": "owned", "priority": 1},
        {"name": "social_media", "type": "owned", "priority": 1},
        {"name": "email", "type": "owned", "priority": 1},
        {"name": "referral", "type": "earned", "priority": 2},
        {"name": "direct", "type": "owned", "priority": 3},
        {"name": "paid_ads", "type": "paid", "priority": 4},
    ]
    
    EMAIL_SEQUENCES = {
        "welcome": {
            "trigger": "signup",
            "emails": [
                {"day": 0, "subject": "Welcome to the Lazy Revolution", "type": "welcome"},
                {"day": 1, "subject": "Your first automation win (takes 5 min)", "type": "value"},
                {"day": 3, "subject": "The mistake I made (so you don't have to)", "type": "story"},
                {"day": 7, "subject": "Ready for the next level?", "type": "soft_pitch"},
            ],
        },
        "abandoned_cart": {
            "trigger": "cart_abandon",
            "emails": [
                {"day": 0, "subject": "You left something behind", "type": "reminder", "delay_hours": 1},
                {"day": 1, "subject": "Still thinking about it?", "type": "objection_handler"},
                {"day": 3, "subject": "Last chance: 10% off expires tonight", "type": "urgency"},
            ],
        },
        "post_purchase": {
            "trigger": "purchase",
            "emails": [
                {"day": 0, "subject": "Your download is ready!", "type": "delivery"},
                {"day": 1, "subject": "Quick start guide (read this first)", "type": "onboarding"},
                {"day": 3, "subject": "How's it going?", "type": "check_in"},
                {"day": 7, "subject": "Bonus: Exclusive resource inside", "type": "surprise"},
                {"day": 14, "subject": "Quick favor? (takes 30 seconds)", "type": "review_request"},
            ],
        },
        "re_engagement": {
            "trigger": "inactive_30d",
            "emails": [
                {"day": 0, "subject": "We miss you!", "type": "re_engagement"},
                {"day": 7, "subject": "Here's what you're missing", "type": "value"},
                {"day": 14, "subject": "Special offer just for you", "type": "win_back"},
            ],
        },
    }
    
    def __init__(self):
        super().__init__(
            name="Director of Growth & Acquisition",
            domain="growth"
        )
        self.traffic_data: Dict[str, int] = {}
        self.email_list_segments: Dict[str, int] = {}
        self.active_campaigns: List[Dict] = []
        self.partnerships: List[Dict] = []
    
    def _initialize_kpis(self):
        """Initialize growth-specific KPIs"""
        # Traffic KPIs
        self.kpis.add_metric("monthly_visitors", target=5000, unit="visitors", period="monthly")
        self.kpis.add_metric("weekly_visitors", target=1250, unit="visitors", period="weekly")
        
        # Email KPIs
        self.kpis.add_metric("email_subscribers", target=2000, unit="subscribers", period="monthly")
        self.kpis.add_metric("email_open_rate", target=35, unit="%", period="weekly")
        self.kpis.add_metric("email_click_rate", target=5, unit="%", period="weekly")
        self.kpis.add_metric("new_subscribers_weekly", target=100, unit="subscribers", period="weekly")
        
        # Lead KPIs
        self.kpis.add_metric("leads_generated", target=200, unit="leads", period="monthly")
        self.kpis.add_metric("lead_conversion_rate", target=5, unit="%", period="monthly")
        
        # Partnership KPIs
        self.kpis.add_metric("active_partnerships", target=5, unit="partnerships", period="monthly")
        self.kpis.add_metric("referral_revenue", target=500, unit="USD", period="monthly")
        
        # Content KPIs
        self.kpis.add_metric("content_pieces_published", target=20, unit="pieces", period="monthly")
        self.kpis.add_metric("seo_keywords_ranking", target=10, unit="keywords", period="monthly")
    
    def execute_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Execute growth-specific tasks"""
        task_type = task.title.lower()
        
        if "email" in task_type or "sequence" in task_type:
            return self._manage_email_campaign(task)
        
        elif "lead" in task_type or "magnet" in task_type:
            return self._create_lead_magnet(task)
        
        elif "seo" in task_type or "content" in task_type:
            return self._optimize_seo(task)
        
        elif "partner" in task_type or "affiliate" in task_type:
            return self._manage_partnership(task)
        
        elif "traffic" in task_type or "acquisition" in task_type:
            return self._drive_traffic(task)
        
        else:
            return self._generic_growth_task(task)
    
    def _manage_email_campaign(self, task: DirectorTask) -> Dict[str, Any]:
        """Create or manage email campaigns"""
        # Determine sequence type
        sequence_type = "welcome"
        for seq_name in self.EMAIL_SEQUENCES.keys():
            if seq_name in task.description.lower():
                sequence_type = seq_name
                break
        
        sequence = self.EMAIL_SEQUENCES[sequence_type]
        
        # Generate email content
        emails_content = []
        for email in sequence["emails"]:
            content = self._generate_email_content(email)
            emails_content.append({
                "day": email["day"],
                "subject": email["subject"],
                "type": email["type"],
                "content_preview": content[:200] + "...",
            })
        
        return {
            "action": "email_sequence_created",
            "sequence_name": sequence_type,
            "trigger": sequence["trigger"],
            "email_count": len(sequence["emails"]),
            "emails": emails_content,
            "estimated_completion_rate": "65%",
        }
    
    def _generate_email_content(self, email_config: Dict) -> str:
        """Generate email content based on type"""
        templates = {
            "welcome": """Hey there!

Welcome to the Lazy Revolution.

I'm Larry, and I'm going to help you build systems that work while you sleep.

First things first: here's your download link:
[DOWNLOAD LINK]

Over the next few days, I'll share:
• Quick automation wins you can implement today
• The exact systems I use to run my business in 20 hours/week
• Exclusive resources I don't share anywhere else

Talk soon,
Lazy Larry

P.S. Hit reply and tell me your biggest time-waster. I might have an automation for that.""",

            "value": """Quick win for you today:

The "5-Minute Email Automation" that saves me hours every week.

Here's the setup:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Total time: 5 minutes
Hours saved: 3+ per week

Try it and let me know how it goes.

- Larry""",

            "story": """I made a mistake that cost me 6 months of progress.

Here's what happened...

[STORY]

The lesson? [LESSON]

Don't make the same mistake I did.

- Larry""",

            "soft_pitch": """You've been getting my emails for a week now.

Quick question: Are you ready to take action?

If you've been thinking about building automated income streams but haven't started yet, I put together something that might help.

[PRODUCT INFO]

No pressure - just wanted to make sure you knew it existed.

- Larry""",

            "delivery": """Your purchase is ready!

Download link: [LINK]

Quick start guide:
1. Download the files
2. Open the README first
3. Follow the 5-minute setup

Questions? Just reply to this email.

Thanks for your trust,
Larry""",

            "review_request": """Quick favor?

You've had [PRODUCT] for a couple weeks now.

If it's helped you at all, would you mind leaving a quick review?

[REVIEW LINK]

Takes about 30 seconds, but it helps other solopreneurs find us.

Thanks!
Larry""",
        }
        
        return templates.get(email_config["type"], templates["value"])
    
    def _create_lead_magnet(self, task: DirectorTask) -> Dict[str, Any]:
        """Create a lead magnet for list building"""
        lead_magnets = [
            {
                "name": "Automation Starter Kit",
                "type": "checklist",
                "description": "10 automations every solopreneur needs",
                "estimated_conversion": "25%",
            },
            {
                "name": "Passive Income Calculator",
                "type": "tool",
                "description": "Calculate your passive income potential",
                "estimated_conversion": "30%",
            },
            {
                "name": "7-Day Lazy Launch Plan",
                "type": "mini_course",
                "description": "Email course to launch your first digital product",
                "estimated_conversion": "20%",
            },
            {
                "name": "SOP Template Pack",
                "type": "templates",
                "description": "5 ready-to-use automation SOPs",
                "estimated_conversion": "22%",
            },
        ]
        
        # Select based on task description or default to first
        selected = lead_magnets[0]
        for magnet in lead_magnets:
            if magnet["type"] in task.description.lower():
                selected = magnet
                break
        
        return {
            "action": "lead_magnet_created",
            "magnet": selected,
            "landing_page_required": True,
            "email_sequence": "welcome",
            "promotion_channels": ["social_media", "content", "exit_popup"],
        }
    
    def _optimize_seo(self, task: DirectorTask) -> Dict[str, Any]:
        """SEO optimization tasks"""
        seo_actions = {
            "target_keywords": [
                "automation for solopreneurs",
                "passive income digital products",
                "etsy automation tools",
                "shopify auto delivery",
                "notion templates business",
                "fiverr ai services",
                "lazy entrepreneur",
                "work less earn more",
            ],
            "content_ideas": [
                {"title": "10 Automations That Save Me 20 Hours/Week", "type": "listicle", "keyword": "automation"},
                {"title": "How to Launch a Digital Product in 7 Days", "type": "guide", "keyword": "digital products"},
                {"title": "The Lazy Entrepreneur's Guide to Passive Income", "type": "pillar", "keyword": "passive income"},
                {"title": "Shopier vs Gumroad: Which is Better for Digital Products?", "type": "comparison", "keyword": "shopier"},
            ],
            "technical_seo": [
                "Optimize meta titles and descriptions",
                "Add schema markup for products",
                "Improve page load speed",
                "Create XML sitemap",
                "Set up Google Search Console",
            ],
        }
        
        self.kpis.increment_metric("content_pieces_published", 1)
        
        return {
            "action": "seo_optimization",
            "keywords_targeted": len(seo_actions["target_keywords"]),
            "content_plan": seo_actions["content_ideas"],
            "technical_tasks": seo_actions["technical_seo"],
        }
    
    def _manage_partnership(self, task: DirectorTask) -> Dict[str, Any]:
        """Manage partnerships and affiliates"""
        partnership_opportunities = [
            {
                "type": "podcast",
                "target": "Side Hustle School, Indie Hackers Podcast",
                "approach": "Pitch automation story angle",
                "value": "Audience exposure",
            },
            {
                "type": "newsletter_swap",
                "target": "Solopreneur newsletters (5K+ subscribers)",
                "approach": "Offer mutual promotion",
                "value": "List growth",
            },
            {
                "type": "affiliate",
                "target": "Productivity YouTubers, course creators",
                "approach": "30% commission on referrals",
                "value": "Revenue share",
            },
            {
                "type": "tool_ambassador",
                "target": "Notion, Zapier, Make",
                "approach": "Apply to ambassador programs",
                "value": "Credibility + perks",
            },
        ]
        
        self.kpis.increment_metric("active_partnerships", 1)
        
        return {
            "action": "partnership_outreach",
            "opportunities": partnership_opportunities,
            "outreach_templates_ready": True,
            "expected_timeline": "2-4 weeks for first partnership",
        }
    
    def _drive_traffic(self, task: DirectorTask) -> Dict[str, Any]:
        """Drive traffic through various channels"""
        traffic_strategies = {
            "organic_social": {
                "actions": [
                    "Post 3x daily on Twitter",
                    "Post 1x daily on LinkedIn",
                    "Engage in 20+ conversations per day",
                    "Share user-generated content",
                ],
                "expected_traffic": "+500 visitors/week",
            },
            "content_marketing": {
                "actions": [
                    "Publish 2 blog posts per week",
                    "Create 1 pillar content piece per month",
                    "Repurpose content across platforms",
                ],
                "expected_traffic": "+300 visitors/week (builds over time)",
            },
            "community_engagement": {
                "actions": [
                    "Participate in 5 communities",
                    "Answer 10 questions per week",
                    "Share valuable resources (no selling)",
                ],
                "expected_traffic": "+200 visitors/week",
            },
            "email_marketing": {
                "actions": [
                    "Send weekly newsletter",
                    "Segment list for personalization",
                    "A/B test subject lines",
                ],
                "expected_traffic": "+100 visitors/week (high quality)",
            },
        }
        
        return {
            "action": "traffic_generation_plan",
            "strategies": traffic_strategies,
            "total_expected_increase": "+1,100 visitors/week",
            "priority_order": ["organic_social", "content_marketing", "community_engagement", "email_marketing"],
        }
    
    def _generic_growth_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Handle generic growth tasks"""
        return {
            "action": "task_acknowledged",
            "task": task.title,
            "status": "queued_for_review",
        }
    
    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """Get prioritized actions to improve growth KPIs"""
        actions = []
        at_risk = self.kpis.get_at_risk()
        
        if "email_subscribers" in at_risk or "new_subscribers_weekly" in at_risk:
            actions.append({
                "action": "lead_magnet_launch",
                "target": "Create and promote new lead magnet",
                "priority": 1,
                "kpi_impact": ["email_subscribers", "new_subscribers_weekly"],
                "expected_lift": "+200 subscribers/month",
            })
        
        if "monthly_visitors" in at_risk or "weekly_visitors" in at_risk:
            actions.append({
                "action": "content_push",
                "target": "Publish 5 SEO-optimized articles",
                "priority": 1,
                "kpi_impact": ["monthly_visitors", "seo_keywords_ranking"],
            })
        
        if "email_open_rate" in at_risk:
            actions.append({
                "action": "email_optimization",
                "target": "A/B test subject lines, clean list",
                "priority": 2,
                "kpi_impact": ["email_open_rate", "email_click_rate"],
            })
        
        if "active_partnerships" in at_risk:
            actions.append({
                "action": "partnership_outreach",
                "target": "Reach out to 10 potential partners",
                "priority": 2,
                "kpi_impact": ["active_partnerships", "referral_revenue"],
            })
        
        if "leads_generated" in at_risk:
            actions.append({
                "action": "conversion_optimization",
                "target": "Add exit popups, improve CTAs",
                "priority": 2,
                "kpi_impact": ["leads_generated", "lead_conversion_rate"],
            })
        
        # Baseline actions
        if not actions:
            actions = [
                {"action": "weekly_newsletter", "target": "Send value-packed newsletter", "priority": 2},
                {"action": "social_engagement", "target": "30 minutes community engagement", "priority": 3},
                {"action": "content_creation", "target": "Draft 2 blog posts", "priority": 3},
            ]
        
        return sorted(actions, key=lambda x: x.get("priority", 5))
    
    def get_funnel_metrics(self) -> Dict[str, Any]:
        """Get marketing funnel metrics"""
        visitors = self.kpis.metrics.get("monthly_visitors")
        leads = self.kpis.metrics.get("leads_generated")
        
        return {
            "top_of_funnel": {
                "visitors": visitors.current if visitors else 0,
                "sources": self.traffic_data,
            },
            "middle_of_funnel": {
                "leads": leads.current if leads else 0,
                "email_subscribers": self.kpis.metrics.get("email_subscribers", {}).current if "email_subscribers" in self.kpis.metrics else 0,
            },
            "conversion_rates": {
                "visitor_to_lead": f"{(leads.current / max(1, visitors.current)) * 100:.1f}%" if visitors and leads else "0%",
                "lead_to_customer": f"{self.kpis.metrics.get('lead_conversion_rate', {}).current if 'lead_conversion_rate' in self.kpis.metrics else 0}%",
            },
        }
