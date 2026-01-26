"""
Commander Engine - Central orchestration and control
Implements the PROFIT OS COMMANDER pattern from knowledge base

The Commander is the chief architect + COO + revenue director of the
AI-native business system. It orchestrates all other engines and
manages the organizational structure.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base_engine import BaseEngine, Job, JobStatus


class DirectorRole(Enum):
    """Executive directors managed by the Commander"""
    COMMERCE = "commerce"       # Offers, pricing, bundles, channels
    SUPPLY = "supply"           # Catalog, quality, IP/licensing
    GROWTH = "growth"           # Social, SEO, email, partnerships
    TECHNOLOGY = "technology"   # Code, infra, bots, deployments
    EVIDENCE = "evidence"       # Metrics, cashflow, ROI


@dataclass
class Director:
    """AI Director persona that handles specific domain responsibilities"""
    role: DirectorRole
    name: str
    active_tasks: List[str] = field(default_factory=list)
    completed_tasks: int = 0
    kpis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MissionBrief:
    """Structured mission for execution"""
    id: str
    title: str
    objective: str
    income_streams: List[str]
    time_horizon: str  # NOW (0-48h), NEAR (7-30d), LATER (30-90d)
    profit_modules: List[str]
    tier1_actions: List[str]  # Urgent revenue actions
    tier2_actions: List[str]  # 7-30 day build-out
    tier3_actions: List[str]  # 30-90 day scale
    kpis: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)


class CommanderEngine(BaseEngine):
    """
    Central orchestration engine that coordinates all business operations.
    
    Responsibilities:
    - Approve budget and go-live decisions
    - Coordinate directors and leads
    - Manage mission execution
    - Track organizational KPIs
    """
    
    PROFIT_MODULES = [
        "profit_radar",           # Analyze niche, target audience, opportunities
        "offer_that_prints_money", # Convert ideas into concrete offers
        "instant_brand_in_a_box", # Brand identity creation
        "website_that_sells",     # Funnel-aligned pages
        "7_day_hype_machine",     # Launch campaign system
        "zero_ad_sales_plan",     # No-paid-ads sales routes
        "objection_killer",       # Identify and address objections
        "partnership_power_plays", # Collaboration strategies
        "60_day_scale_sprint",    # Weekly milestones and experiments
        "automation_money_machine", # Turn manual steps into automations
    ]
    
    def __init__(self):
        super().__init__(
            name="commander",
            objective="Orchestrate AI-first Profit OS across products, services, content, and automation"
        )
        self.directors = self._initialize_directors()
        self.missions: List[MissionBrief] = []
        self.budget_remaining = 10000.0  # Starting budget
        self.revenue_target = 50000.0    # Monthly target
        self.current_revenue = 0.0
    
    def _initialize_directors(self) -> Dict[DirectorRole, Director]:
        """Initialize the AI director team"""
        return {
            DirectorRole.COMMERCE: Director(
                role=DirectorRole.COMMERCE,
                name="Director of Commerce",
                kpis={"conversion_rate": 0.0, "aov": 0.0, "revenue": 0.0}
            ),
            DirectorRole.SUPPLY: Director(
                role=DirectorRole.SUPPLY,
                name="Director of Supply & Product",
                kpis={"active_skus": 0, "quality_score": 0.0, "ip_coverage": 0.0}
            ),
            DirectorRole.GROWTH: Director(
                role=DirectorRole.GROWTH,
                name="Director of Growth",
                kpis={"traffic": 0, "leads": 0, "engagement_rate": 0.0}
            ),
            DirectorRole.TECHNOLOGY: Director(
                role=DirectorRole.TECHNOLOGY,
                name="Director of Technology",
                kpis={"uptime": 99.9, "automation_coverage": 0.0, "deploy_success": 0.0}
            ),
            DirectorRole.EVIDENCE: Director(
                role=DirectorRole.EVIDENCE,
                name="Director of Evidence & Finance",
                kpis={"revenue": 0.0, "profit_margin": 0.0, "cac": 0.0, "ltv": 0.0}
            ),
        }
    
    def get_inputs(self) -> List[str]:
        return [
            "mission_request",
            "budget_allocation",
            "revenue_data",
            "market_signals",
            "team_capacity",
        ]
    
    def get_outputs(self) -> List[str]:
        return [
            "mission_brief",
            "director_assignments",
            "job_queues",
            "kpi_dashboard",
            "execution_report",
        ]
    
    def create_mission(
        self,
        title: str,
        objective: str,
        income_streams: List[str],
        time_horizon: str = "NOW"
    ) -> MissionBrief:
        """Create a structured mission for execution"""
        
        mission = MissionBrief(
            id=f"MISSION_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=title,
            objective=objective,
            income_streams=income_streams,
            time_horizon=time_horizon,
            profit_modules=self._select_profit_modules(objective),
            tier1_actions=self._generate_tier1_actions(income_streams),
            tier2_actions=self._generate_tier2_actions(income_streams),
            tier3_actions=self._generate_tier3_actions(income_streams),
            kpis=self._define_mission_kpis(income_streams),
        )
        
        self.missions.append(mission)
        self.logger.info(f"Created mission: {mission.id} - {mission.title}")
        
        # Enqueue execution jobs
        self.enqueue("execute_mission", {"mission_id": mission.id}, priority=10)
        
        return mission
    
    def _select_profit_modules(self, objective: str) -> List[str]:
        """Select relevant profit modules based on objective"""
        objective_lower = objective.lower()
        modules = []
        
        if "launch" in objective_lower or "first sale" in objective_lower:
            modules.extend(["profit_radar", "offer_that_prints_money", "7_day_hype_machine"])
        if "scale" in objective_lower or "grow" in objective_lower:
            modules.extend(["60_day_scale_sprint", "partnership_power_plays"])
        if "automate" in objective_lower:
            modules.append("automation_money_machine")
        if "brand" in objective_lower:
            modules.append("instant_brand_in_a_box")
        
        # Always include evidence tracking
        modules.append("profit_radar")
        
        return list(set(modules))
    
    def _generate_tier1_actions(self, income_streams: List[str]) -> List[str]:
        """Generate urgent revenue actions (0-48h)"""
        actions = []
        
        for stream in income_streams:
            if "shopify" in stream.lower() or "product" in stream.lower():
                actions.extend([
                    "Publish 3 ready products to Shopify",
                    "Configure auto-delivery for digital products",
                    "Set up flash sale campaign (48h, 20% off)",
                ])
            if "fiverr" in stream.lower() or "service" in stream.lower():
                actions.extend([
                    "Create 1 Fiverr gig with ready assets",
                    "Optimize gig tags and description",
                    "Send 10 outreach DMs to potential clients",
                ])
            if "content" in stream.lower() or "youtube" in stream.lower():
                actions.extend([
                    "Publish 1 YouTube Short with product CTA",
                    "Create 3 social media posts",
                    "Schedule content for next 7 days",
                ])
        
        return actions[:10]  # Cap at 10 urgent actions
    
    def _generate_tier2_actions(self, income_streams: List[str]) -> List[str]:
        """Generate 7-30 day build-out actions"""
        return [
            "Expand to 15 active product listings",
            "Create 3 bundle offers with tier pricing",
            "Launch on secondary channel (Etsy/Gumroad)",
            "Implement review request automation",
            "Build email list to 500+ subscribers",
            "Set up chatbot for customer service",
            "Create weekly content calendar",
            "Establish social posting schedule (daily)",
        ]
    
    def _generate_tier3_actions(self, income_streams: List[str]) -> List[str]:
        """Generate 30-90 day scale actions"""
        return [
            "Expand to 50+ active listings",
            "Launch B2B white-label offering",
            "Build affiliate program",
            "Hire/contract VA for support",
            "Implement retargeting ads",
            "Create high-ticket consulting package",
            "Develop recurring subscription product",
            "Establish partnership with 5+ creators",
        ]
    
    def _define_mission_kpis(self, income_streams: List[str]) -> Dict[str, Any]:
        """Define KPIs for mission success"""
        return {
            "revenue_target_48h": 200,
            "revenue_target_7d": 1000,
            "revenue_target_30d": 5000,
            "conversion_rate_target": 0.03,
            "products_live_target": 10,
            "reviews_target": 20,
            "email_subscribers_target": 500,
        }
    
    def delegate_to_director(self, role: DirectorRole, task: str) -> str:
        """Delegate a task to a specific director"""
        director = self.directors[role]
        director.active_tasks.append(task)
        self.logger.info(f"Delegated to {director.name}: {task}")
        return f"Task delegated to {director.name}"
    
    def complete_director_task(self, role: DirectorRole, task: str):
        """Mark a director's task as complete"""
        director = self.directors[role]
        if task in director.active_tasks:
            director.active_tasks.remove(task)
            director.completed_tasks += 1
    
    def process_job(self, job: Job) -> Dict[str, Any]:
        """Process commander jobs"""
        
        if job.job_type == "execute_mission":
            return self._execute_mission(job.payload["mission_id"])
        
        elif job.job_type == "create_mission":
            mission = self.create_mission(**job.payload)
            return {"mission_id": mission.id, "status": "created"}
        
        elif job.job_type == "delegate_task":
            result = self.delegate_to_director(
                DirectorRole(job.payload["role"]),
                job.payload["task"]
            )
            return {"delegation": result}
        
        elif job.job_type == "update_kpis":
            return self._update_kpis(job.payload)
        
        elif job.job_type == "approve_budget":
            return self._approve_budget(job.payload)
        
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")
    
    def _execute_mission(self, mission_id: str) -> Dict[str, Any]:
        """Execute a mission by distributing work to directors"""
        mission = next((m for m in self.missions if m.id == mission_id), None)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")
        
        mission.status = "in_progress"
        
        # Distribute tier 1 actions to directors
        assignments = []
        
        for action in mission.tier1_actions:
            action_lower = action.lower()
            
            if "product" in action_lower or "listing" in action_lower:
                self.delegate_to_director(DirectorRole.SUPPLY, action)
                assignments.append({"director": "supply", "action": action})
            
            elif "campaign" in action_lower or "sale" in action_lower:
                self.delegate_to_director(DirectorRole.COMMERCE, action)
                assignments.append({"director": "commerce", "action": action})
            
            elif "content" in action_lower or "social" in action_lower:
                self.delegate_to_director(DirectorRole.GROWTH, action)
                assignments.append({"director": "growth", "action": action})
            
            elif "automat" in action_lower or "deliver" in action_lower:
                self.delegate_to_director(DirectorRole.TECHNOLOGY, action)
                assignments.append({"director": "technology", "action": action})
            
            else:
                # Default to commerce for revenue-focused actions
                self.delegate_to_director(DirectorRole.COMMERCE, action)
                assignments.append({"director": "commerce", "action": action})
        
        return {
            "mission_id": mission_id,
            "status": "executing",
            "assignments": assignments,
            "tier1_actions": len(mission.tier1_actions),
        }
    
    def _update_kpis(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update organizational KPIs"""
        for role, kpis in kpi_data.items():
            if role in [r.value for r in DirectorRole]:
                director = self.directors[DirectorRole(role)]
                director.kpis.update(kpis)
        
        return {"kpis_updated": True, "data": kpi_data}
    
    def _approve_budget(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Approve budget allocation for initiatives"""
        amount = request.get("amount", 0)
        purpose = request.get("purpose", "")
        
        if amount > self.budget_remaining:
            return {"approved": False, "reason": "Insufficient budget"}
        
        self.budget_remaining -= amount
        return {
            "approved": True,
            "amount": amount,
            "purpose": purpose,
            "remaining_budget": self.budget_remaining,
        }
    
    def get_organizational_status(self) -> Dict[str, Any]:
        """Get complete organizational status"""
        return {
            "commander_status": self.get_status(),
            "directors": {
                role.value: {
                    "name": director.name,
                    "active_tasks": len(director.active_tasks),
                    "completed_tasks": director.completed_tasks,
                    "kpis": director.kpis,
                }
                for role, director in self.directors.items()
            },
            "missions": [
                {
                    "id": m.id,
                    "title": m.title,
                    "status": m.status,
                    "time_horizon": m.time_horizon,
                }
                for m in self.missions
            ],
            "financials": {
                "budget_remaining": self.budget_remaining,
                "revenue_target": self.revenue_target,
                "current_revenue": self.current_revenue,
                "progress": f"{(self.current_revenue / self.revenue_target) * 100:.1f}%",
            }
        }
