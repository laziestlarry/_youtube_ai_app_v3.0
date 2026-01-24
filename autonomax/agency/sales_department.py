"""
Sales Department
================

The Sales Department is responsible for converting leads into customers.
Handles deal closing, objection handling, and conversion optimization.

Philosophy: "Every interaction is an opportunity to provide value"
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("autonomax.agency.sales")


class DealStage(Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ObjectionType(Enum):
    PRICE = "price"
    TIMING = "timing"
    NEED = "need"
    TRUST = "trust"
    AUTHORITY = "authority"
    COMPETITION = "competition"


@dataclass
class Deal:
    """A sales deal in the pipeline"""
    id: str
    lead_id: str
    product_sku: str
    value: float
    stage: DealStage = DealStage.LEAD
    probability: float = 0.1
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    close_date: Optional[datetime] = None
    objections: List[ObjectionType] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class Objection:
    """A customer objection and response"""
    type: ObjectionType
    customer_statement: str
    response: str
    follow_up: str


class DealCloser:
    """
    Autonomous deal closing agent.
    
    Manages deals through the pipeline, handles objections,
    and optimizes for conversion.
    """
    
    def __init__(self, name: str = "Closer-Alpha"):
        self.name = name
        self.deals: List[Deal] = []
        self.daily_target = 5  # deals to close
        self.closed_today = 0
        
        # Objection handlers
        self.objection_responses = {
            ObjectionType.PRICE: [
                {
                    "trigger": "too expensive",
                    "response": "I totally get it - budget matters. Let me share what others in your situation found: the ROI usually comes within 30 days. Would a payment plan help?",
                    "follow_up": "Also, we have a starter tier at half the price. Want me to walk you through what's included?",
                },
                {
                    "trigger": "can't afford",
                    "response": "Completely understand. Here's the thing - most of our customers said the same thing, then realized it paid for itself in week 1 through time saved. What if we did a trial first?",
                    "follow_up": "Or I can give you 20% off with code LAZY20 - makes it more accessible.",
                },
            ],
            ObjectionType.TIMING: [
                {
                    "trigger": "not now",
                    "response": "No pressure at all. Quick question though - what would need to change for the timing to be right?",
                    "follow_up": "Happy to check back in [timeframe]. Meanwhile, I'll send you our free guide so you're ready when you are.",
                },
                {
                    "trigger": "too busy",
                    "response": "That's actually why this exists - to give you time back. Most customers say it saves them 10+ hours/week. What if we started with just the automation piece?",
                    "follow_up": "I can set everything up for you. Zero time investment on your end.",
                },
            ],
            ObjectionType.NEED: [
                {
                    "trigger": "don't need",
                    "response": "Fair enough! Out of curiosity - how are you currently handling [pain point]? Just want to make sure I understand your setup.",
                    "follow_up": "Got it. If that ever changes, I'll be here. Mind if I send a quick case study showing how someone in your situation used it?",
                },
            ],
            ObjectionType.TRUST: [
                {
                    "trigger": "not sure",
                    "response": "Totally valid - you should be sure. Here's what I'd suggest: check out these 3 reviews from people in similar situations. If you have questions after, I'm here.",
                    "follow_up": "Also happy to jump on a quick call to answer anything. No pitch, just answers.",
                },
                {
                    "trigger": "never heard of you",
                    "response": "We're newer to the scene but growing fast - 500+ customers in 6 months. Here's our founder's story if you want the background. We also have a 30-day guarantee.",
                    "follow_up": "Want me to connect you with a current customer for a reference?",
                },
            ],
            ObjectionType.AUTHORITY: [
                {
                    "trigger": "need to check",
                    "response": "Of course! What information would help make their decision easier? I can put together a summary.",
                    "follow_up": "Also happy to jump on a call with both of you if that helps.",
                },
            ],
            ObjectionType.COMPETITION: [
                {
                    "trigger": "using something else",
                    "response": "Nice! What do you like most about it? Genuinely curious.",
                    "follow_up": "Makes sense. If you ever want to compare features, I can show you what's different. No pressure though.",
                },
            ],
        }
        
        # Closing techniques
        self.closing_techniques = [
            {
                "name": "Assumptive Close",
                "script": "Great! So should I set you up with the Pro plan or the Starter? Most people in your situation go Pro for the automation features.",
                "best_for": ["warm_leads", "high_intent"],
            },
            {
                "name": "Scarcity Close",
                "script": "Just a heads up - this 20% off ends in 24 hours. After that it goes back to full price. Want me to lock in the discount for you?",
                "best_for": ["price_sensitive", "procrastinators"],
            },
            {
                "name": "Value Summary Close",
                "script": "So to recap: you get [benefit 1], [benefit 2], and [benefit 3] - all for less than the cost of [relatable comparison]. Ready to get started?",
                "best_for": ["analytical", "value_focused"],
            },
            {
                "name": "Question Close",
                "script": "Is there anything else you need to know before we get you set up?",
                "best_for": ["information_seekers", "hesitant"],
            },
            {
                "name": "Trial Close",
                "script": "How about this - try it for 7 days. If it doesn't save you at least 5 hours, I'll refund you no questions asked. Fair?",
                "best_for": ["skeptical", "risk_averse"],
            },
        ]
    
    def handle_objection(self, objection_type: ObjectionType, customer_statement: str) -> Dict[str, Any]:
        """Generate response to customer objection"""
        responses = self.objection_responses.get(objection_type, [])
        
        # Find best matching response
        best_response = responses[0] if responses else {
            "response": "I understand. What would help you feel more confident about this?",
            "follow_up": "Happy to answer any questions you have.",
        }
        
        for resp in responses:
            if resp.get("trigger", "").lower() in customer_statement.lower():
                best_response = resp
                break
        
        return {
            "objection_type": objection_type.value,
            "customer_statement": customer_statement,
            "response": best_response["response"],
            "follow_up": best_response["follow_up"],
            "handler": self.name,
        }
    
    def advance_deal(self, deal: Deal) -> Deal:
        """Advance deal to next stage"""
        stage_progression = {
            DealStage.LEAD: DealStage.QUALIFIED,
            DealStage.QUALIFIED: DealStage.PROPOSAL,
            DealStage.PROPOSAL: DealStage.NEGOTIATION,
            DealStage.NEGOTIATION: DealStage.CLOSED_WON,
        }
        
        probability_by_stage = {
            DealStage.LEAD: 0.1,
            DealStage.QUALIFIED: 0.25,
            DealStage.PROPOSAL: 0.50,
            DealStage.NEGOTIATION: 0.75,
            DealStage.CLOSED_WON: 1.0,
        }
        
        next_stage = stage_progression.get(deal.stage)
        if next_stage:
            deal.stage = next_stage
            deal.probability = probability_by_stage.get(next_stage, deal.probability)
            deal.last_activity = datetime.utcnow()
            
            if next_stage == DealStage.CLOSED_WON:
                deal.close_date = datetime.utcnow()
                self.closed_today += 1
                logger.info(f"[{self.name}] Deal {deal.id} CLOSED WON: ${deal.value}")
        
        return deal
    
    def select_closing_technique(self, deal: Deal, buyer_type: str = "warm_leads") -> Dict[str, Any]:
        """Select best closing technique for the situation"""
        for technique in self.closing_techniques:
            if buyer_type in technique.get("best_for", []):
                return {
                    "technique": technique["name"],
                    "script": technique["script"],
                    "deal_id": deal.id,
                    "recommended_for": technique["best_for"],
                }
        
        # Default to value summary
        return {
            "technique": self.closing_techniques[2]["name"],
            "script": self.closing_techniques[2]["script"],
            "deal_id": deal.id,
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get closer status"""
        pipeline_value = sum(d.value * d.probability for d in self.deals)
        return {
            "name": self.name,
            "deals_in_pipeline": len(self.deals),
            "pipeline_value": pipeline_value,
            "closed_today": self.closed_today,
            "daily_target": self.daily_target,
            "close_rate": f"{(self.closed_today / max(1, self.daily_target)) * 100:.0f}%",
        }


class ConversionOptimizer:
    """
    Optimizes conversion rates across the sales funnel.
    
    Analyzes funnel performance, identifies bottlenecks,
    and recommends optimizations.
    """
    
    def __init__(self, name: str = "Optimizer-Alpha"):
        self.name = name
        
        # Conversion benchmarks
        self.benchmarks = {
            "visitor_to_lead": 0.05,  # 5%
            "lead_to_qualified": 0.40,  # 40%
            "qualified_to_proposal": 0.50,  # 50%
            "proposal_to_close": 0.30,  # 30%
            "overall": 0.03,  # 3%
        }
        
        # Optimization levers
        self.optimization_levers = {
            "visitor_to_lead": [
                "Add exit-intent popup with lead magnet",
                "Improve headline clarity",
                "Add social proof above fold",
                "Simplify opt-in form (2 fields max)",
                "Add urgency element (countdown, limited)",
            ],
            "lead_to_qualified": [
                "Implement lead scoring",
                "Add qualification questions to opt-in",
                "Send immediate welcome sequence",
                "Segment by pain point",
                "Add quick-win content in first email",
            ],
            "qualified_to_proposal": [
                "Reduce time-to-contact to <5 minutes",
                "Personalize outreach based on behavior",
                "Include case study in first touch",
                "Offer low-friction next step (demo, audit)",
                "Address common objections preemptively",
            ],
            "proposal_to_close": [
                "Add urgency (expiring offer)",
                "Include guarantee prominently",
                "Simplify pricing (3 tiers max)",
                "Add payment plan option",
                "Follow up within 24 hours",
            ],
        }
    
    def analyze_funnel(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze funnel and identify bottlenecks"""
        bottlenecks = []
        recommendations = []
        
        for stage, benchmark in self.benchmarks.items():
            actual = metrics.get(stage, 0)
            if actual < benchmark * 0.8:  # Below 80% of benchmark
                bottlenecks.append({
                    "stage": stage,
                    "actual": f"{actual * 100:.1f}%",
                    "benchmark": f"{benchmark * 100:.1f}%",
                    "gap": f"{(benchmark - actual) * 100:.1f}%",
                    "priority": "high" if actual < benchmark * 0.5 else "medium",
                })
                
                # Get optimization recommendations
                stage_recommendations = self.optimization_levers.get(stage, [])[:3]
                recommendations.extend([
                    {"stage": stage, "action": rec}
                    for rec in stage_recommendations
                ])
        
        return {
            "analyzed_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "benchmarks": self.benchmarks,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "health_score": self._calculate_funnel_health(metrics),
        }
    
    def _calculate_funnel_health(self, metrics: Dict[str, float]) -> float:
        """Calculate overall funnel health score (0-100)"""
        if not metrics:
            return 0.0
        
        scores = []
        for stage, benchmark in self.benchmarks.items():
            actual = metrics.get(stage, 0)
            score = min(100, (actual / benchmark) * 100) if benchmark > 0 else 0
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def generate_ab_test(self, stage: str, hypothesis: str) -> Dict[str, Any]:
        """Generate A/B test for a funnel stage"""
        return {
            "test_id": f"TEST-{stage.upper()}-{datetime.utcnow().strftime('%Y%m%d')}",
            "stage": stage,
            "hypothesis": hypothesis,
            "variants": {
                "control": "Current version",
                "treatment": f"Optimized based on: {hypothesis}",
            },
            "sample_size_needed": 1000,
            "duration_days": 14,
            "success_metric": f"{stage}_conversion_rate",
            "minimum_detectable_effect": 0.10,  # 10% improvement
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get optimizer status"""
        return {
            "name": self.name,
            "benchmarks": self.benchmarks,
            "optimization_levers_count": sum(len(v) for v in self.optimization_levers.values()),
        }


class SalesDepartment:
    """
    Sales Department orchestrates all sales operations.
    
    Manages deal closers and conversion optimizers to
    maximize revenue from the lead pipeline.
    """
    
    def __init__(self):
        self.name = "Sales Department"
        self.closers = [
            DealCloser("Closer-Alpha"),
            DealCloser("Closer-Beta"),
        ]
        self.optimizers = [
            ConversionOptimizer("Optimizer-Alpha"),
        ]
        
        # KPIs
        self.kpis = {
            "deals_closed": {"target": 10, "current": 0},
            "revenue_closed": {"target": 5000, "current": 0},
            "conversion_rate": {"target": 5.0, "current": 0.0},
            "average_deal_size": {"target": 100, "current": 0},
            "pipeline_value": {"target": 20000, "current": 0},
        }
    
    def get_department_status(self) -> Dict[str, Any]:
        """Get full department status"""
        return {
            "department": self.name,
            "closers": [c.get_status() for c in self.closers],
            "optimizers": [o.get_status() for o in self.optimizers],
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
