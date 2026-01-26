"""
Hunter Department
=================

The Hunter Department is responsible for lead discovery, opportunity
identification, and proactive outreach. Hunters find potential customers
before they find us.

Philosophy: "Hunt, Ideate, Define, Target, Inform"
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("autonomax.agency.hunters")


class LeadStatus(Enum):
    DISCOVERED = "discovered"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CONVERTED = "converted"
    LOST = "lost"


class HuntingGround(Enum):
    REDDIT = "reddit"
    INDIE_HACKERS = "indie_hackers"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    DISCORD = "discord"
    FACEBOOK_GROUPS = "facebook_groups"
    PRODUCT_HUNT = "product_hunt"
    HACKER_NEWS = "hacker_news"


@dataclass
class Lead:
    """A discovered potential customer"""
    id: str
    source: HuntingGround
    persona: str
    pain_points: List[str]
    contact_method: str
    status: LeadStatus = LeadStatus.DISCOVERED
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_contact: Optional[datetime] = None
    notes: List[str] = field(default_factory=list)
    score: int = 0  # 0-100 qualification score


@dataclass
class Opportunity:
    """A validated revenue opportunity"""
    id: str
    lead_id: str
    product_fit: str  # SKU that matches their need
    estimated_value: float
    probability: float  # 0.0-1.0
    next_action: str
    deadline: Optional[datetime] = None


class LeadHunter:
    """
    Autonomous lead discovery agent.
    
    Hunts for potential customers in online communities,
    identifies pain points, and prepares targeted outreach.
    """
    
    def __init__(self, name: str = "Hunter-Alpha"):
        self.name = name
        self.hunting_grounds = [
            HuntingGround.REDDIT,
            HuntingGround.INDIE_HACKERS,
            HuntingGround.LINKEDIN,
            HuntingGround.TWITTER,
        ]
        self.leads: List[Lead] = []
        self.daily_quota = 10
        self.hunts_today = 0
        
        # Target personas
        self.target_personas = [
            {
                "name": "Solopreneur Steve",
                "pain_points": ["time management", "automation", "scaling"],
                "keywords": ["solopreneur", "side hustle", "passive income"],
                "platforms": [HuntingGround.REDDIT, HuntingGround.INDIE_HACKERS],
            },
            {
                "name": "Creator Carla",
                "pain_points": ["content creation", "monetization", "audience growth"],
                "keywords": ["content creator", "youtube", "digital products"],
                "platforms": [HuntingGround.TWITTER, HuntingGround.LINKEDIN],
            },
            {
                "name": "Agency Adam",
                "pain_points": ["client delivery", "automation", "scaling services"],
                "keywords": ["agency owner", "freelancer", "client work"],
                "platforms": [HuntingGround.LINKEDIN, HuntingGround.TWITTER],
            },
            {
                "name": "Etsy Emily",
                "pain_points": ["product creation", "marketing", "SEO"],
                "keywords": ["etsy seller", "print on demand", "digital downloads"],
                "platforms": [HuntingGround.REDDIT, HuntingGround.FACEBOOK_GROUPS],
            },
        ]
    
    def hunt(self, ground: HuntingGround, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Hunt for leads in a specific hunting ground.
        
        In production, this would integrate with Reddit API, LinkedIn Sales Navigator,
        Twitter API, etc. For now, returns hunt strategy.
        """
        hunt_strategies = {
            HuntingGround.REDDIT: {
                "subreddits": [
                    "r/Entrepreneur",
                    "r/passive_income",
                    "r/SideProject",
                    "r/smallbusiness",
                    "r/startups",
                ],
                "search_queries": keywords,
                "engagement_method": "value_comment_then_dm",
                "response_template": self._get_reddit_template(),
            },
            HuntingGround.INDIE_HACKERS: {
                "groups": ["automation", "saas", "side-projects"],
                "search_queries": keywords,
                "engagement_method": "post_comment_engage",
                "response_template": self._get_ih_template(),
            },
            HuntingGround.LINKEDIN: {
                "search_filters": {
                    "title": ["Founder", "CEO", "Freelancer", "Agency Owner"],
                    "company_size": ["1-10", "11-50"],
                },
                "connection_message": self._get_linkedin_template(),
                "engagement_method": "connect_engage_offer",
            },
            HuntingGround.TWITTER: {
                "hashtags": ["#buildinpublic", "#indiehacker", "#solopreneur"],
                "search_queries": keywords,
                "engagement_method": "reply_value_dm",
                "response_template": self._get_twitter_template(),
            },
        }
        
        strategy = hunt_strategies.get(ground, {})
        strategy["keywords"] = keywords
        strategy["ground"] = ground.value
        strategy["hunter"] = self.name
        strategy["timestamp"] = datetime.utcnow().isoformat()
        
        self.hunts_today += 1
        logger.info(f"[{self.name}] Hunting in {ground.value} for {keywords}")
        
        return [strategy]
    
    def qualify_lead(self, lead: Lead) -> int:
        """
        Score a lead based on qualification criteria.
        Returns score 0-100.
        """
        score = 0
        
        # Pain point match (0-30)
        known_pain_points = ["automation", "time", "scaling", "revenue", "growth"]
        matching_pains = sum(1 for p in lead.pain_points if any(k in p.lower() for k in known_pain_points))
        score += min(30, matching_pains * 10)
        
        # Source quality (0-20)
        high_intent_sources = [HuntingGround.INDIE_HACKERS, HuntingGround.LINKEDIN]
        if lead.source in high_intent_sources:
            score += 20
        else:
            score += 10
        
        # Persona match (0-30)
        for persona in self.target_personas:
            if any(kw in lead.persona.lower() for kw in persona["keywords"]):
                score += 30
                break
        
        # Engagement potential (0-20)
        if lead.contact_method in ["dm", "email", "linkedin"]:
            score += 20
        elif lead.contact_method in ["comment", "reply"]:
            score += 10
        
        lead.score = score
        if score >= 60:
            lead.status = LeadStatus.QUALIFIED
        
        return score
    
    def generate_outreach(self, lead: Lead, product_sku: str) -> Dict[str, Any]:
        """Generate personalized outreach for a lead"""
        
        outreach = {
            "lead_id": lead.id,
            "product": product_sku,
            "channel": lead.contact_method,
            "messages": [],
        }
        
        # First touch - value first
        outreach["messages"].append({
            "sequence": 1,
            "type": "value_first",
            "template": f"""Hey! Noticed you mentioned {lead.pain_points[0] if lead.pain_points else 'automation'}.

I've been building tools to help with exactly that. Happy to share what's worked for me if you're interested.

No pitch, just genuinely curious about your approach.""",
            "delay_hours": 0,
        })
        
        # Second touch - soft offer
        outreach["messages"].append({
            "sequence": 2,
            "type": "soft_offer",
            "template": f"""Following up - I put together a quick guide on {lead.pain_points[0] if lead.pain_points else 'automation'}.

Would you want me to send it over? Totally free, just want to help.""",
            "delay_hours": 48,
        })
        
        # Third touch - direct offer
        outreach["messages"].append({
            "sequence": 3,
            "type": "direct_offer",
            "template": f"""Last one from me - we're running a 48-hour special on our automation toolkit.

20% off with code LAZY20 if it's helpful.

Either way, best of luck with your project!""",
            "delay_hours": 96,
        })
        
        return outreach
    
    def _get_reddit_template(self) -> str:
        return """[Value Comment]

Great question! I've been working on something similar.

Here's what I found works:
1. [Specific actionable tip]
2. [Another tip relevant to their post]
3. [Resource or tool suggestion]

Happy to share more if helpful. Been building in this space for a while."""
    
    def _get_ih_template(self) -> str:
        return """Congrats on the launch! 🎉

Quick question - how are you handling [pain point from their post]?

I've been experimenting with automation for that and curious how others approach it."""
    
    def _get_linkedin_template(self) -> str:
        return """Hi [Name],

Saw your profile - looks like you're building something interesting in [their space].

Always looking to connect with fellow builders. Would love to hear what you're working on!

- Larry"""
    
    def _get_twitter_template(self) -> str:
        return """This is great! 🔥

Have you tried [relevant tip]? Made a huge difference for me.

Happy to share more context if helpful."""
    
    def get_status(self) -> Dict[str, Any]:
        """Get hunter status"""
        return {
            "name": self.name,
            "leads_discovered": len(self.leads),
            "leads_qualified": len([l for l in self.leads if l.status == LeadStatus.QUALIFIED]),
            "hunts_today": self.hunts_today,
            "daily_quota": self.daily_quota,
            "quota_progress": f"{(self.hunts_today / self.daily_quota) * 100:.0f}%",
            "hunting_grounds": [g.value for g in self.hunting_grounds],
        }


class OpportunityScout:
    """
    Scouts for revenue opportunities in existing data.
    
    Analyzes customer behavior, market trends, and competitor
    gaps to identify new revenue opportunities.
    """
    
    def __init__(self, name: str = "Scout-Alpha"):
        self.name = name
        self.opportunities: List[Opportunity] = []
        
        # Opportunity sources
        self.sources = [
            "shopier_analytics",
            "social_mentions",
            "competitor_gaps",
            "customer_requests",
            "market_trends",
        ]
    
    def scout_product_gaps(self, catalog: List[Dict]) -> List[Dict[str, Any]]:
        """Identify gaps in current product catalog"""
        gaps = []
        
        # Price tier gaps
        prices = [p.get("price", 0) for p in catalog]
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            
            if min_price > 50:
                gaps.append({
                    "type": "price_tier_gap",
                    "description": "No entry-level products under $50",
                    "recommendation": "Create a starter kit at $29-49",
                    "estimated_impact": "$500-1000/month",
                })
            
            if max_price < 500:
                gaps.append({
                    "type": "price_tier_gap",
                    "description": "No premium offerings above $500",
                    "recommendation": "Create VIP/consulting tier at $997-2997",
                    "estimated_impact": "$2000-5000/month",
                })
        
        # Category gaps
        categories = set(p.get("category", "digital") for p in catalog)
        missing_categories = {"service", "consulting", "subscription"} - categories
        for cat in missing_categories:
            gaps.append({
                "type": "category_gap",
                "description": f"No {cat} offerings in catalog",
                "recommendation": f"Add {cat} product type",
                "estimated_impact": "$1000-3000/month",
            })
        
        return gaps
    
    def scout_upsell_opportunities(self, orders: List[Dict]) -> List[Dict[str, Any]]:
        """Identify upsell opportunities from order history"""
        opportunities = []
        
        # Bundle opportunity
        opportunities.append({
            "type": "bundle_upsell",
            "description": "Customers buying X often need Y",
            "recommendation": "Create X+Y bundle at 15% discount",
            "trigger": "post_purchase_email",
            "estimated_impact": "20% increase in AOV",
        })
        
        # Upgrade opportunity
        opportunities.append({
            "type": "tier_upgrade",
            "description": "40% of buyers are power users",
            "recommendation": "Offer Pro upgrade at 2x price",
            "trigger": "usage_milestone",
            "estimated_impact": "$500-1000/month",
        })
        
        return opportunities
    
    def get_status(self) -> Dict[str, Any]:
        """Get scout status"""
        return {
            "name": self.name,
            "opportunities_found": len(self.opportunities),
            "sources_monitored": self.sources,
        }


class HunterDepartment:
    """
    Hunter Department orchestrates all hunting operations.
    
    Manages lead hunters and opportunity scouts to maintain
    a healthy pipeline of potential customers.
    """
    
    def __init__(self):
        self.name = "Hunter Department"
        self.hunters = [
            LeadHunter("Hunter-Alpha"),
            LeadHunter("Hunter-Beta"),
        ]
        self.scouts = [
            OpportunityScout("Scout-Alpha"),
        ]
        
        # KPIs
        self.kpis = {
            "leads_per_day": {"target": 20, "current": 0},
            "qualified_leads": {"target": 50, "current": 0},
            "opportunities_found": {"target": 10, "current": 0},
            "outreach_sent": {"target": 30, "current": 0},
            "conversion_rate": {"target": 5.0, "current": 0.0},
        }
    
    def daily_hunt(self, keywords: List[str] = None) -> Dict[str, Any]:
        """Execute daily hunting operations"""
        if keywords is None:
            keywords = ["automation", "passive income", "side hustle", "solopreneur"]
        
        results = {
            "date": datetime.utcnow().isoformat(),
            "hunts": [],
            "leads_discovered": 0,
        }
        
        for hunter in self.hunters:
            for ground in hunter.hunting_grounds[:2]:  # 2 grounds per hunter
                hunt_result = hunter.hunt(ground, keywords)
                results["hunts"].extend(hunt_result)
        
        return results
    
    def get_department_status(self) -> Dict[str, Any]:
        """Get full department status"""
        return {
            "department": self.name,
            "hunters": [h.get_status() for h in self.hunters],
            "scouts": [s.get_status() for s in self.scouts],
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
