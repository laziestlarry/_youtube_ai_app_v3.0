"""
Marketing Department
====================

The Marketing Department is responsible for brand awareness,
content creation, and campaign execution.

Philosophy: "Value first, sell second"
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("autonomax.agency.marketing")


class ContentType(Enum):
    POST = "post"
    THREAD = "thread"
    VIDEO = "video"
    STORY = "story"
    ARTICLE = "article"
    EMAIL = "email"
    AD = "ad"


class Platform(Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    REDDIT = "reddit"
    EMAIL = "email"


class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Content:
    """A piece of marketing content"""
    id: str
    type: ContentType
    platform: Platform
    title: str
    body: str
    cta: str
    hashtags: List[str] = field(default_factory=list)
    media_urls: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    performance: Dict[str, int] = field(default_factory=dict)


@dataclass
class Campaign:
    """A marketing campaign"""
    id: str
    name: str
    objective: str
    start_date: datetime
    end_date: datetime
    platforms: List[Platform]
    budget: float = 0.0
    status: CampaignStatus = CampaignStatus.DRAFT
    content_pieces: List[Content] = field(default_factory=list)
    kpis: Dict[str, Any] = field(default_factory=dict)


class ContentCreator:
    """
    Autonomous content creation agent.
    
    Creates engaging content across platforms following
    the brand voice and content strategy.
    """
    
    def __init__(self, name: str = "Creator-Alpha"):
        self.name = name
        self.daily_quota = 5
        self.created_today = 0
        
        # Brand voice guidelines
        self.brand_voice = {
            "tone": "friendly, professional, authentic",
            "personality": "Lazy Larry - the guardian of laziness",
            "values": ["automation", "freedom", "results"],
            "avoid": ["hype", "pushy sales", "jargon"],
        }
        
        # Content templates by type
        self.templates = {
            ContentType.POST: {
                "value_post": """🎯 {hook}

Here's what I learned:

{point_1}
{point_2}
{point_3}

{cta}

{hashtags}""",
                "story_post": """I used to {before_state}.

Then I discovered {insight}.

Now I {after_state}.

The difference? {key_lesson}

{cta}""",
                "list_post": """{number} {topic} that {benefit}:

1. {item_1}
2. {item_2}
3. {item_3}
4. {item_4}
5. {item_5}

Which one are you trying first?

{hashtags}""",
            },
            ContentType.THREAD: {
                "breakdown": """🧵 How to {outcome} (step-by-step):

1/{total}""",
            },
            ContentType.EMAIL: {
                "welcome": """Subject: Welcome to the lazy side 😎

Hey {name},

You're in!

Here's what happens next:
1. {step_1}
2. {step_2}
3. {step_3}

One quick thing: hit reply and tell me your #1 challenge with {topic}.
I read every email.

- Larry""",
                "value": """Subject: {curiosity_hook}

{name},

{value_content}

{cta}

- Larry""",
            },
        }
        
        # Platform-specific optimizations
        self.platform_specs = {
            Platform.LINKEDIN: {
                "max_chars": 3000,
                "best_times": ["8am", "12pm", "5pm"],
                "optimal_hashtags": 3,
                "post_style": "professional, story-driven",
            },
            Platform.TWITTER: {
                "max_chars": 280,
                "best_times": ["9am", "12pm", "6pm"],
                "optimal_hashtags": 2,
                "post_style": "punchy, conversational",
            },
            Platform.FACEBOOK: {
                "max_chars": 500,
                "best_times": ["1pm", "4pm", "9pm"],
                "optimal_hashtags": 0,
                "post_style": "engaging, community-focused",
            },
            Platform.INSTAGRAM: {
                "max_chars": 2200,
                "best_times": ["11am", "2pm", "7pm"],
                "optimal_hashtags": 15,
                "post_style": "visual, lifestyle-focused",
            },
        }
    
    def create_post(
        self,
        platform: Platform,
        topic: str,
        template_type: str = "value_post",
        **kwargs
    ) -> Content:
        """Create a social media post"""
        template = self.templates.get(ContentType.POST, {}).get(
            template_type,
            self.templates[ContentType.POST]["value_post"]
        )
        
        # Get platform specs
        specs = self.platform_specs.get(platform, {})
        
        # Generate content
        content_id = f"POST-{platform.value.upper()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Default content structure
        body = template.format(
            hook=kwargs.get("hook", f"Stop wasting time on {topic}"),
            point_1=kwargs.get("point_1", "Automate the repetitive stuff"),
            point_2=kwargs.get("point_2", "Focus on what actually matters"),
            point_3=kwargs.get("point_3", "Let systems do the heavy lifting"),
            cta=kwargs.get("cta", "Want to learn more? Link in bio."),
            hashtags=" ".join([f"#{h}" for h in kwargs.get("hashtags", ["automation", "productivity"])]),
            **kwargs
        )
        
        # Truncate if needed
        max_chars = specs.get("max_chars", 500)
        if len(body) > max_chars:
            body = body[:max_chars-3] + "..."
        
        content = Content(
            id=content_id,
            type=ContentType.POST,
            platform=platform,
            title=topic,
            body=body,
            cta=kwargs.get("cta", "Link in bio"),
            hashtags=kwargs.get("hashtags", []),
        )
        
        self.created_today += 1
        logger.info(f"[{self.name}] Created {platform.value} post: {content_id}")
        
        return content
    
    def create_email(
        self,
        email_type: str,
        subject: str,
        recipient_name: str = "there",
        **kwargs
    ) -> Content:
        """Create an email"""
        template = self.templates.get(ContentType.EMAIL, {}).get(
            email_type,
            self.templates[ContentType.EMAIL]["value"]
        )
        
        content_id = f"EMAIL-{email_type.upper()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        body = template.format(
            name=recipient_name,
            subject=subject,
            **kwargs
        )
        
        content = Content(
            id=content_id,
            type=ContentType.EMAIL,
            platform=Platform.EMAIL,
            title=subject,
            body=body,
            cta=kwargs.get("cta", "Check it out"),
        )
        
        self.created_today += 1
        return content
    
    def create_content_batch(
        self,
        topic: str,
        platforms: List[Platform],
    ) -> List[Content]:
        """Create content batch for multiple platforms"""
        batch = []
        
        for platform in platforms:
            content = self.create_post(
                platform=platform,
                topic=topic,
                hook=f"The secret to {topic} nobody talks about",
                point_1=f"Most people overcomplicate {topic}",
                point_2="The 80/20 rule applies here",
                point_3="Automation is your friend",
                cta="DM 'LAZY' for my free guide",
                hashtags=["automation", "productivity", "buildinpublic"],
            )
            batch.append(content)
        
        return batch
    
    def get_content_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate content calendar for upcoming days"""
        calendar = []
        topics = [
            "automation tips",
            "time management",
            "passive income",
            "building in public",
            "solopreneur life",
            "product launches",
            "customer success",
        ]
        
        for i in range(days):
            day = datetime.utcnow() + timedelta(days=i)
            calendar.append({
                "date": day.strftime("%Y-%m-%d"),
                "day": day.strftime("%A"),
                "content": [
                    {
                        "time": "9:00 AM",
                        "platform": Platform.LINKEDIN.value,
                        "type": "value_post",
                        "topic": topics[i % len(topics)],
                    },
                    {
                        "time": "12:00 PM",
                        "platform": Platform.TWITTER.value,
                        "type": "thread",
                        "topic": topics[(i + 1) % len(topics)],
                    },
                    {
                        "time": "6:00 PM",
                        "platform": Platform.FACEBOOK.value,
                        "type": "engagement_post",
                        "topic": topics[(i + 2) % len(topics)],
                    },
                ],
            })
        
        return calendar
    
    def get_status(self) -> Dict[str, Any]:
        """Get creator status"""
        return {
            "name": self.name,
            "created_today": self.created_today,
            "daily_quota": self.daily_quota,
            "quota_progress": f"{(self.created_today / self.daily_quota) * 100:.0f}%",
            "brand_voice": self.brand_voice["tone"],
        }


class CampaignManager:
    """
    Manages marketing campaigns.
    
    Plans, executes, and optimizes marketing campaigns
    across multiple channels.
    """
    
    def __init__(self, name: str = "Manager-Alpha"):
        self.name = name
        self.campaigns: List[Campaign] = []
        
        # Campaign templates
        self.campaign_templates = {
            "flash_sale": {
                "duration_days": 2,
                "platforms": [Platform.LINKEDIN, Platform.TWITTER, Platform.FACEBOOK, Platform.EMAIL],
                "content_sequence": [
                    {"day": 1, "hour": 0, "type": "announcement"},
                    {"day": 1, "hour": 8, "type": "reminder"},
                    {"day": 2, "hour": 0, "type": "last_chance"},
                    {"day": 2, "hour": 20, "type": "final_call"},
                ],
                "kpis": {
                    "impressions": 10000,
                    "clicks": 500,
                    "conversions": 25,
                    "revenue": 2500,
                },
            },
            "product_launch": {
                "duration_days": 7,
                "platforms": [Platform.LINKEDIN, Platform.TWITTER, Platform.YOUTUBE, Platform.EMAIL],
                "content_sequence": [
                    {"day": -3, "type": "teaser"},
                    {"day": -1, "type": "countdown"},
                    {"day": 0, "type": "launch"},
                    {"day": 1, "type": "social_proof"},
                    {"day": 3, "type": "faq"},
                    {"day": 5, "type": "case_study"},
                    {"day": 7, "type": "recap"},
                ],
                "kpis": {
                    "impressions": 50000,
                    "clicks": 2500,
                    "signups": 500,
                    "conversions": 50,
                    "revenue": 5000,
                },
            },
            "community_growth": {
                "duration_days": 30,
                "platforms": [Platform.LINKEDIN, Platform.TWITTER, Platform.REDDIT],
                "content_sequence": [
                    {"frequency": "daily", "type": "value_post"},
                    {"frequency": "weekly", "type": "community_spotlight"},
                    {"frequency": "biweekly", "type": "ama"},
                ],
                "kpis": {
                    "followers_gained": 1000,
                    "engagement_rate": 5.0,
                    "community_members": 200,
                },
            },
        }
    
    def create_campaign(
        self,
        name: str,
        template_type: str,
        start_date: datetime = None,
        budget: float = 0.0,
    ) -> Campaign:
        """Create a new campaign from template"""
        template = self.campaign_templates.get(template_type, self.campaign_templates["flash_sale"])
        
        if start_date is None:
            start_date = datetime.utcnow()
        
        end_date = start_date + timedelta(days=template["duration_days"])
        
        campaign = Campaign(
            id=f"CAMP-{template_type.upper()}-{datetime.utcnow().strftime('%Y%m%d')}",
            name=name,
            objective=f"{template_type.replace('_', ' ').title()} Campaign",
            start_date=start_date,
            end_date=end_date,
            platforms=[Platform(p) if isinstance(p, str) else p for p in template["platforms"]],
            budget=budget,
            status=CampaignStatus.DRAFT,
            kpis=template["kpis"],
        )
        
        self.campaigns.append(campaign)
        logger.info(f"[{self.name}] Created campaign: {campaign.id}")
        
        return campaign
    
    def generate_campaign_content(self, campaign: Campaign) -> List[Content]:
        """Generate all content for a campaign"""
        creator = ContentCreator()
        content_pieces = []
        
        for platform in campaign.platforms:
            # Create announcement
            content = creator.create_post(
                platform=platform,
                topic=campaign.name,
                template_type="value_post",
                hook=f"🚀 {campaign.name} is LIVE!",
                point_1="Everything you need to automate",
                point_2="20% off for 48 hours",
                point_3="Code: LAZY20",
                cta="Grab it now 👇",
            )
            content_pieces.append(content)
        
        campaign.content_pieces = content_pieces
        return content_pieces
    
    def get_campaign_performance(self, campaign: Campaign) -> Dict[str, Any]:
        """Get campaign performance metrics"""
        return {
            "campaign_id": campaign.id,
            "name": campaign.name,
            "status": campaign.status.value,
            "duration": f"{(campaign.end_date - campaign.start_date).days} days",
            "progress": self._calculate_progress(campaign),
            "kpis": campaign.kpis,
            "content_pieces": len(campaign.content_pieces),
            "platforms": [p.value for p in campaign.platforms],
        }
    
    def _calculate_progress(self, campaign: Campaign) -> str:
        """Calculate campaign progress percentage"""
        now = datetime.utcnow()
        if now < campaign.start_date:
            return "0%"
        elif now > campaign.end_date:
            return "100%"
        else:
            total_duration = (campaign.end_date - campaign.start_date).total_seconds()
            elapsed = (now - campaign.start_date).total_seconds()
            return f"{(elapsed / total_duration) * 100:.0f}%"
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        active_campaigns = [c for c in self.campaigns if c.status == CampaignStatus.ACTIVE]
        return {
            "name": self.name,
            "total_campaigns": len(self.campaigns),
            "active_campaigns": len(active_campaigns),
            "campaign_templates": list(self.campaign_templates.keys()),
        }


class MarketingDepartment:
    """
    Marketing Department orchestrates all marketing operations.
    
    Manages content creators and campaign managers to
    drive awareness and demand.
    """
    
    def __init__(self):
        self.name = "Marketing Department"
        self.creators = [
            ContentCreator("Creator-Alpha"),
            ContentCreator("Creator-Beta"),
        ]
        self.managers = [
            CampaignManager("Manager-Alpha"),
        ]
        
        # KPIs
        self.kpis = {
            "content_published": {"target": 50, "current": 0},
            "impressions": {"target": 100000, "current": 0},
            "engagement_rate": {"target": 5.0, "current": 0.0},
            "followers_gained": {"target": 500, "current": 0},
            "leads_generated": {"target": 100, "current": 0},
        }
    
    def launch_flash_sale(self, campaign_name: str) -> Dict[str, Any]:
        """Launch a flash sale campaign"""
        manager = self.managers[0]
        campaign = manager.create_campaign(
            name=campaign_name,
            template_type="flash_sale",
        )
        content = manager.generate_campaign_content(campaign)
        campaign.status = CampaignStatus.ACTIVE
        
        return {
            "campaign": campaign.id,
            "status": "launched",
            "content_pieces": len(content),
            "platforms": [p.value for p in campaign.platforms],
        }
    
    def get_department_status(self) -> Dict[str, Any]:
        """Get full department status"""
        return {
            "department": self.name,
            "creators": [c.get_status() for c in self.creators],
            "managers": [m.get_status() for m in self.managers],
            "kpis": self.kpis,
            "health": self._calculate_health(),
        }
    
    def _calculate_health(self) -> float:
        """Calculate department health score"""
        scores = []
        for kpi, data in self.kpis.items():
            if data["target"] > 0:
                progress = min(100, (data["current"] / data["target"]) * 100)
                scores.append(progress)
        return sum(scores) / len(scores) if scores else 0.0
