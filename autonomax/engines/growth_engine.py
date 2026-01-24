"""
Growth Engine - Autonomous marketing and customer acquisition
Handles content marketing, social media, SEO, and partnership development
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base_engine import BaseEngine, Job


class ContentType(Enum):
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    VIDEO_SHORT = "video_short"
    EMAIL = "email"
    CAROUSEL = "carousel"


class Channel(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    EMAIL = "email"
    SEO = "seo"


class CampaignType(Enum):
    LAUNCH = "launch"
    FLASH_SALE = "flash_sale"
    CONTENT_SERIES = "content_series"
    PARTNERSHIP = "partnership"
    RETARGETING = "retargeting"


@dataclass
class ContentPiece:
    """Content item for marketing"""
    id: str
    content_type: ContentType
    channel: Channel
    title: str
    body: str
    cta: str
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    engagement: Dict[str, int] = field(default_factory=lambda: {"views": 0, "clicks": 0, "conversions": 0})


@dataclass
class Campaign:
    """Marketing campaign"""
    id: str
    campaign_type: CampaignType
    name: str
    channels: List[Channel]
    content: List[ContentPiece] = field(default_factory=list)
    budget: float = 0.0
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    status: str = "draft"
    metrics: Dict[str, Any] = field(default_factory=dict)


class GrowthEngine(BaseEngine):
    """
    Engine for autonomous marketing and customer acquisition.
    
    Implements:
    - 7-Day Hype Machine
    - Zero-Ad Sales Plan
    - Partnership Power Plays
    - 60-Day Scale Sprint
    
    Responsibilities:
    - Generate marketing content
    - Schedule and publish social posts
    - Manage email campaigns
    - Track engagement and conversions
    - Optimize for growth
    """
    
    def __init__(self):
        super().__init__(
            name="growth",
            objective="Drive autonomous customer acquisition and engagement across all channels"
        )
        self.campaigns: List[Campaign] = []
        self.content_queue: List[ContentPiece] = []
        self.email_list_size = 0
        self.social_followers = {
            Channel.TWITTER: 0,
            Channel.LINKEDIN: 0,
            Channel.INSTAGRAM: 0,
            Channel.YOUTUBE: 0,
            Channel.TIKTOK: 0,
        }
    
    def get_inputs(self) -> List[str]:
        return [
            "product_catalog",
            "target_audience",
            "campaign_goals",
            "budget_allocation",
            "performance_data",
        ]
    
    def get_outputs(self) -> List[str]:
        return [
            "content_calendar",
            "social_posts",
            "email_campaigns",
            "partnership_outreach",
            "growth_report",
        ]
    
    def create_campaign(
        self,
        campaign_type: CampaignType,
        name: str,
        channels: List[Channel],
        budget: float = 0.0,
        duration_days: int = 7,
    ) -> Campaign:
        """Create a new marketing campaign"""
        campaign = Campaign(
            id=f"CAMP_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            campaign_type=campaign_type,
            name=name,
            channels=channels,
            budget=budget,
            end_date=datetime.utcnow() + timedelta(days=duration_days),
        )
        
        self.campaigns.append(campaign)
        
        # Enqueue content generation
        self.enqueue("generate_campaign_content", {
            "campaign_id": campaign.id,
            "campaign_type": campaign_type.value,
            "channels": [c.value for c in channels],
            "duration_days": duration_days,
        }, priority=8)
        
        self.logger.info(f"Created campaign: {campaign.name}")
        return campaign
    
    def process_job(self, job: Job) -> Dict[str, Any]:
        """Process growth engine jobs"""
        
        if job.job_type == "generate_campaign_content":
            return self._generate_campaign_content(job.payload)
        
        elif job.job_type == "schedule_content":
            return self._schedule_content(job.payload)
        
        elif job.job_type == "publish_content":
            return self._publish_content(job.payload)
        
        elif job.job_type == "run_hype_machine":
            return self._run_hype_machine(job.payload)
        
        elif job.job_type == "partnership_outreach":
            return self._partnership_outreach(job.payload)
        
        elif job.job_type == "generate_report":
            return self._generate_growth_report(job.payload)
        
        elif job.job_type == "dm_outreach":
            return self._dm_outreach(job.payload)
        
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")
    
    def _generate_campaign_content(self, payload: Dict) -> Dict[str, Any]:
        """Generate content for a campaign"""
        campaign_id = payload["campaign_id"]
        campaign_type = payload["campaign_type"]
        channels = payload["channels"]
        duration_days = payload["duration_days"]
        
        campaign = next((c for c in self.campaigns if c.id == campaign_id), None)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")
        
        content_pieces = []
        
        if campaign_type == "launch":
            content_pieces = self._generate_launch_content(channels, duration_days)
        elif campaign_type == "flash_sale":
            content_pieces = self._generate_flash_sale_content(channels)
        elif campaign_type == "content_series":
            content_pieces = self._generate_content_series(channels, duration_days)
        
        campaign.content = content_pieces
        campaign.status = "content_ready"
        
        # Schedule the content
        self.enqueue("schedule_content", {
            "campaign_id": campaign_id,
        }, priority=7)
        
        return {
            "campaign_id": campaign_id,
            "content_generated": len(content_pieces),
            "channels": channels,
        }
    
    def _generate_launch_content(self, channels: List[str], duration_days: int) -> List[ContentPiece]:
        """Generate launch campaign content (7-Day Hype Machine)"""
        content = []
        
        # Pre-launch teaser
        if "twitter" in channels:
            content.append(ContentPiece(
                id=f"CONT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_01",
                content_type=ContentType.SOCIAL_POST,
                channel=Channel.TWITTER,
                title="Pre-Launch Teaser",
                body="Something big is coming... 🚀\n\nIn 48 hours, we're dropping the most comprehensive automation toolkit we've ever built.\n\nReply 'READY' if you want early access.",
                cta="Reply READY",
            ))
        
        if "linkedin" in channels:
            content.append(ContentPiece(
                id=f"CONT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_02",
                content_type=ContentType.SOCIAL_POST,
                channel=Channel.LINKEDIN,
                title="LinkedIn Launch Announcement",
                body="📢 Big Announcement\n\nAfter months of development, I'm excited to share our new automation system.\n\nIt's designed for solopreneurs who want to:\n✅ Automate content creation\n✅ Scale without hiring\n✅ Build passive income streams\n\nEarly access link in comments 👇",
                cta="Get Early Access",
            ))
        
        # Launch day content
        content.append(ContentPiece(
            id=f"CONT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_03",
            content_type=ContentType.SOCIAL_POST,
            channel=Channel.TWITTER,
            title="Launch Day Thread",
            body="🚀 IT'S LIVE!\n\nIntroducing the AutonomaX Mastery Pack:\n\n• 50+ Zen Art Designs\n• Creator Launch Templates\n• Platform Playbooks\n• Automation SOPs\n• Revenue Dashboard\n\nAll for $497 (valued at $2,847)\n\n🔗 Link in bio\n\nThread 🧵",
            cta="Get the Pack",
        ))
        
        # Post-launch follow-up
        content.append(ContentPiece(
            id=f"CONT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_04",
            content_type=ContentType.EMAIL,
            channel=Channel.EMAIL,
            title="Launch Email",
            body="""Subject: It's Here - AutonomaX Mastery Pack is Live

Hi {first_name},

The wait is over.

The AutonomaX Mastery Pack is now available.

Here's what you get:
- 50+ Premium Zen Art Designs ($199 value)
- Creator Launch Templates ($199 value)  
- Platform Playbooks ($299 value)
- Automation SOPs ($299 value)
- Notion Dashboard ($149 value)
- Revenue Intelligence Suite ($499 value)
- Community Access ($297 value)
- AI Prompt Library ($199 value)

Total Value: $2,847
Your Price: $497

That's 83% off.

But here's the thing...

This price is only available for the first 48 hours.

After that, it goes to $697.

[GET THE MASTERY PACK →]

To your success,
Lazy Larry
""",
            cta="Get the Mastery Pack",
        ))
        
        return content
    
    def _generate_flash_sale_content(self, channels: List[str]) -> List[ContentPiece]:
        """Generate flash sale content"""
        content = []
        
        urgency_post = ContentPiece(
            id=f"CONT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_flash",
            content_type=ContentType.SOCIAL_POST,
            channel=Channel.TWITTER,
            title="Flash Sale Announcement",
            body="⚡ 24-HOUR FLASH SALE ⚡\n\n30% off EVERYTHING\n\nUse code: FLASH30\n\n⏰ Ends midnight\n\n🔗 Link in bio",
            cta="Shop Now",
        )
        content.append(urgency_post)
        
        countdown_post = ContentPiece(
            id=f"CONT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_countdown",
            content_type=ContentType.SOCIAL_POST,
            channel=Channel.TWITTER,
            title="Countdown Post",
            body="⏰ 6 HOURS LEFT\n\nFlash sale ending soon.\n\nAfter midnight, prices go back to normal.\n\nDon't miss 30% off:\n🔗",
            cta="Last Chance",
        )
        content.append(countdown_post)
        
        return content
    
    def _generate_content_series(self, channels: List[str], duration_days: int) -> List[ContentPiece]:
        """Generate content series for ongoing engagement"""
        content = []
        
        topics = [
            ("Automation Tip #1", "The #1 automation tool that saved me 10 hours/week"),
            ("Automation Tip #2", "How to automate your content calendar in 15 minutes"),
            ("Automation Tip #3", "The email sequence that converts at 15%"),
            ("Automation Tip #4", "Chatbots: The secret weapon for 24/7 customer service"),
            ("Automation Tip #5", "One automation that generates $500/week passively"),
        ]
        
        for i, (title, hook) in enumerate(topics[:duration_days]):
            content.append(ContentPiece(
                id=f"CONT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{i}",
                content_type=ContentType.SOCIAL_POST,
                channel=Channel.TWITTER,
                title=title,
                body=f"{hook}\n\nThread 🧵\n\n(Want the full playbook? Link in bio)",
                cta="Get the Playbook",
            ))
        
        return content
    
    def _schedule_content(self, payload: Dict) -> Dict[str, Any]:
        """Schedule content for publishing"""
        campaign_id = payload["campaign_id"]
        
        campaign = next((c for c in self.campaigns if c.id == campaign_id), None)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")
        
        # Schedule content at optimal times
        scheduled = []
        base_time = datetime.utcnow()
        
        for i, content in enumerate(campaign.content):
            # Stagger posts by 4 hours
            content.scheduled_at = base_time + timedelta(hours=i * 4)
            scheduled.append({
                "content_id": content.id,
                "channel": content.channel.value,
                "scheduled_at": content.scheduled_at.isoformat(),
            })
            
            # Enqueue publishing job
            self.enqueue("publish_content", {
                "content_id": content.id,
                "campaign_id": campaign_id,
            }, priority=6)
        
        campaign.status = "scheduled"
        
        return {
            "campaign_id": campaign_id,
            "content_scheduled": len(scheduled),
            "schedule": scheduled,
        }
    
    def _publish_content(self, payload: Dict) -> Dict[str, Any]:
        """Publish content to channel"""
        content_id = payload["content_id"]
        campaign_id = payload["campaign_id"]
        
        campaign = next((c for c in self.campaigns if c.id == campaign_id), None)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")
        
        content = next((c for c in campaign.content if c.id == content_id), None)
        if not content:
            raise ValueError(f"Content not found: {content_id}")
        
        # In production, this would call social media APIs
        content.published_at = datetime.utcnow()
        
        self.logger.info(f"Published content {content_id} to {content.channel.value}")
        
        return {
            "content_id": content_id,
            "channel": content.channel.value,
            "published_at": content.published_at.isoformat(),
            "status": "published",
        }
    
    def _run_hype_machine(self, payload: Dict) -> Dict[str, Any]:
        """Execute the 7-Day Hype Machine launch sequence"""
        product_sku = payload.get("product_sku", "MASTERY-PACK-ULTIMATE")
        
        # Day-by-day launch sequence
        sequence = [
            {"day": -2, "action": "teaser_posts", "channels": ["twitter", "linkedin"]},
            {"day": -1, "action": "email_announcement", "channels": ["email"]},
            {"day": 0, "action": "launch_blast", "channels": ["twitter", "linkedin", "email"]},
            {"day": 1, "action": "social_proof", "channels": ["twitter", "instagram"]},
            {"day": 2, "action": "faq_content", "channels": ["twitter"]},
            {"day": 3, "action": "case_study", "channels": ["linkedin", "email"]},
            {"day": 4, "action": "urgency_push", "channels": ["twitter", "email"]},
            {"day": 5, "action": "last_chance", "channels": ["all"]},
            {"day": 6, "action": "closed_follow_up", "channels": ["email"]},
        ]
        
        # Create launch campaign
        campaign = self.create_campaign(
            campaign_type=CampaignType.LAUNCH,
            name=f"7-Day Hype Machine - {product_sku}",
            channels=[Channel.TWITTER, Channel.LINKEDIN, Channel.EMAIL],
            duration_days=7,
        )
        
        return {
            "campaign_id": campaign.id,
            "sequence": sequence,
            "product_sku": product_sku,
            "status": "hype_machine_activated",
        }
    
    def _partnership_outreach(self, payload: Dict) -> Dict[str, Any]:
        """Execute partnership outreach (Partnership Power Plays)"""
        target_count = payload.get("target_count", 10)
        partnership_type = payload.get("type", "affiliate")
        
        # Generate outreach templates
        templates = {
            "affiliate": {
                "subject": "Partnership Opportunity - 30% Commission",
                "body": """Hi {name},

I love your content on {topic}. Your audience would really benefit from our automation tools.

Would you be interested in an affiliate partnership?

Here's what we offer:
- 30% commission on all sales
- Custom discount code for your audience
- Promotional assets and content
- Monthly performance reports

Let me know if you'd like to chat!

Best,
Lazy Larry
AutonomaX Team
""",
            },
            "collab": {
                "subject": "Collaboration Idea",
                "body": """Hi {name},

Quick idea: What if we created a joint product together?

Your expertise in {topic} + our automation platform = something powerful.

Thinking a 50/50 revenue split.

Worth a 15-minute call to explore?

Best,
Lazy Larry
""",
            },
        }
        
        template = templates.get(partnership_type, templates["affiliate"])
        
        # Generate outreach list (in production, this would be from a database)
        outreach_list = [
            {"name": f"Creator_{i}", "email": f"creator{i}@example.com", "topic": "productivity"}
            for i in range(target_count)
        ]
        
        return {
            "partnership_type": partnership_type,
            "outreach_count": target_count,
            "template": template,
            "outreach_list": outreach_list,
            "status": "outreach_prepared",
        }
    
    def _dm_outreach(self, payload: Dict) -> Dict[str, Any]:
        """Execute DM outreach campaign"""
        platform = payload.get("platform", "twitter")
        message = payload.get("message", "")
        target_count = payload.get("count", 10)
        
        # DM template
        default_message = """Hey {name}!

Saw your post about {topic} - really resonated with me.

We just launched a toolkit that automates a lot of what you talked about.

Would love to get your feedback if you have 2 mins to check it out: {link}

No pressure at all, just thought it might be useful!

Cheers,
Larry
"""
        
        return {
            "platform": platform,
            "message": message or default_message,
            "target_count": target_count,
            "status": "dm_outreach_queued",
        }
    
    def _generate_growth_report(self, payload: Dict) -> Dict[str, Any]:
        """Generate growth performance report"""
        period_days = payload.get("period_days", 7)
        
        # Calculate engagement metrics
        total_views = sum(
            c.engagement["views"]
            for campaign in self.campaigns
            for c in campaign.content
        )
        total_clicks = sum(
            c.engagement["clicks"]
            for campaign in self.campaigns
            for c in campaign.content
        )
        total_conversions = sum(
            c.engagement["conversions"]
            for campaign in self.campaigns
            for c in campaign.content
        )
        
        return {
            "period_days": period_days,
            "campaigns_active": len([c for c in self.campaigns if c.status == "active"]),
            "total_content_published": sum(
                len([p for p in c.content if p.published_at])
                for c in self.campaigns
            ),
            "engagement": {
                "views": total_views,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "ctr": f"{(total_clicks / total_views * 100) if total_views else 0:.2f}%",
                "conversion_rate": f"{(total_conversions / total_clicks * 100) if total_clicks else 0:.2f}%",
            },
            "channels": {
                channel.value: followers
                for channel, followers in self.social_followers.items()
            },
            "email_list_size": self.email_list_size,
        }
    
    def get_growth_dashboard(self) -> Dict[str, Any]:
        """Get growth dashboard data"""
        return {
            "campaigns": len(self.campaigns),
            "active_campaigns": len([c for c in self.campaigns if c.status in ["active", "scheduled"]]),
            "content_queue": len(self.content_queue),
            "social_followers": {
                k.value: v for k, v in self.social_followers.items()
            },
            "email_list": self.email_list_size,
            "total_reach": sum(self.social_followers.values()) + self.email_list_size,
        }
