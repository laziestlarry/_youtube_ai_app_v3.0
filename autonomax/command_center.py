"""
AutonomaX Command Center
Central orchestration hub that coordinates all directors toward KPI targets

The Command Center is the operational brain of Propulse-AutonomaX.
It assigns missions, monitors KPIs, and ensures all directors work
together toward organizational goals.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

from .directors import (
    BaseDirector,
    BrandDirector,
    CommerceDirector,
    GrowthDirector,
    OperationsDirector,
)


class MissionPriority(Enum):
    CRITICAL = 1  # Revenue emergency, system down
    HIGH = 2      # KPI at risk, opportunity window
    MEDIUM = 3    # Standard operations
    LOW = 4       # Optimization, nice-to-have


class MissionStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Mission:
    """Strategic mission assigned by Command Center"""
    id: str
    title: str
    objective: str
    priority: MissionPriority
    directors_assigned: List[str]
    kpi_targets: Dict[str, float]
    deadline: datetime
    status: MissionStatus = MissionStatus.PLANNED
    created_at: datetime = field(default_factory=datetime.utcnow)
    progress: float = 0.0
    blockers: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrganizationalKPIs:
    """Top-level organizational KPIs that roll up from directors"""
    
    # Revenue (from Commerce Director)
    monthly_revenue_target: float = 5000.0
    monthly_revenue_actual: float = 0.0
    
    # Growth (from Growth Director)
    email_list_target: int = 2000
    email_list_actual: int = 0
    monthly_traffic_target: int = 5000
    monthly_traffic_actual: int = 0
    
    # Brand (from Brand Director)
    social_followers_target: int = 5000
    social_followers_actual: int = 0
    communities_target: int = 8
    communities_actual: int = 0
    
    # Operations (from Operations Director)
    delivery_success_target: float = 99.5
    delivery_success_actual: float = 0.0
    automation_coverage_target: float = 80.0
    automation_coverage_actual: float = 0.0
    
    def calculate_health_score(self) -> float:
        """Calculate overall organizational health (0-100)"""
        scores = []
        
        if self.monthly_revenue_target > 0:
            scores.append(min(100, (self.monthly_revenue_actual / self.monthly_revenue_target) * 100))
        if self.email_list_target > 0:
            scores.append(min(100, (self.email_list_actual / self.email_list_target) * 100))
        if self.social_followers_target > 0:
            scores.append(min(100, (self.social_followers_actual / self.social_followers_target) * 100))
        if self.delivery_success_target > 0:
            scores.append(min(100, (self.delivery_success_actual / self.delivery_success_target) * 100))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_at_risk_areas(self) -> List[str]:
        """Identify areas that are significantly behind target"""
        at_risk = []
        
        if self.monthly_revenue_target > 0 and self.monthly_revenue_actual < self.monthly_revenue_target * 0.5:
            at_risk.append("revenue")
        if self.email_list_target > 0 and self.email_list_actual < self.email_list_target * 0.5:
            at_risk.append("email_list")
        if self.social_followers_target > 0 and self.social_followers_actual < self.social_followers_target * 0.5:
            at_risk.append("social_presence")
        if self.delivery_success_target > 0 and self.delivery_success_actual < self.delivery_success_target * 0.95:
            at_risk.append("operations")
        
        return at_risk


class CommandCenter:
    """
    Central Command for Propulse-AutonomaX
    
    Responsibilities:
    - Set organizational KPI targets
    - Create and assign missions to directors
    - Monitor progress and health
    - Escalate issues and reallocate resources
    - Generate executive reports
    """
    
    def __init__(self):
        self.logger = logging.getLogger("command_center")
        
        # Initialize directors
        self.directors: Dict[str, BaseDirector] = {
            "brand": BrandDirector(),
            "commerce": CommerceDirector(),
            "growth": GrowthDirector(),
            "operations": OperationsDirector(),
        }
        
        # Organizational state
        self.org_kpis = OrganizationalKPIs()
        self.missions: List[Mission] = []
        self.execution_log: List[Dict] = []
        
        # Initialize with startup mission
        self._create_startup_mission()
    
    def _create_startup_mission(self):
        """Create initial mission for new organization"""
        mission = Mission(
            id="MISSION_STARTUP_001",
            title="First $500 Sprint",
            objective="Generate first $500 in revenue within 7 days",
            priority=MissionPriority.HIGH,
            directors_assigned=["commerce", "brand", "growth"],
            kpi_targets={
                "revenue": 500,
                "products_live": 10,
                "social_posts": 20,
                "communities_joined": 3,
            },
            deadline=datetime.utcnow() + timedelta(days=7),
        )
        self.missions.append(mission)
    
    def create_mission(
        self,
        title: str,
        objective: str,
        priority: MissionPriority,
        directors: List[str],
        kpi_targets: Dict[str, float],
        deadline_days: int = 7,
    ) -> Mission:
        """Create a new mission and assign to directors"""
        mission = Mission(
            id=f"MISSION_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=title,
            objective=objective,
            priority=priority,
            directors_assigned=directors,
            kpi_targets=kpi_targets,
            deadline=datetime.utcnow() + timedelta(days=deadline_days),
        )
        
        self.missions.append(mission)
        self.logger.info(f"Mission created: {mission.id} - {mission.title}")
        
        # Notify directors
        for director_id in directors:
            if director_id in self.directors:
                director = self.directors[director_id]
                director.receive_task(
                    title=f"Mission: {mission.title}",
                    description=mission.objective,
                    priority=priority.value,
                    kpi_impact=list(kpi_targets.keys()),
                    due_date=mission.deadline,
                )
        
        return mission
    
    def activate_mission(self, mission_id: str) -> Dict[str, Any]:
        """Activate a mission and distribute tasks to directors"""
        mission = self._get_mission(mission_id)
        if not mission:
            return {"error": f"Mission {mission_id} not found"}
        
        mission.status = MissionStatus.ACTIVE
        
        # Generate specific tasks for each director based on KPI targets
        tasks_assigned = []
        
        for director_id in mission.directors_assigned:
            director = self.directors.get(director_id)
            if not director:
                continue
            
            # Get priority actions from director
            priority_actions = director.get_priority_actions()[:3]
            
            for action in priority_actions:
                task = director.receive_task(
                    title=action.get("action", "Execute priority action"),
                    description=action.get("target", ""),
                    priority=action.get("priority", 3),
                    kpi_impact=action.get("kpi_impact", []),
                )
                tasks_assigned.append({
                    "director": director_id,
                    "task_id": task.id,
                    "action": action.get("action"),
                })
        
        self._log_execution("mission_activated", {
            "mission_id": mission_id,
            "tasks_assigned": len(tasks_assigned),
        })
        
        return {
            "mission_id": mission_id,
            "status": "activated",
            "tasks_assigned": tasks_assigned,
        }
    
    def execute_cycle(self) -> Dict[str, Any]:
        """
        Execute one operational cycle:
        1. Collect KPIs from all directors
        2. Identify at-risk areas
        3. Generate priority actions
        4. Execute pending tasks
        5. Update mission progress
        """
        cycle_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "directors": {},
            "missions": [],
            "actions_taken": [],
            "escalations": [],
        }
        
        # 1. Collect director reports
        for director_id, director in self.directors.items():
            report = director.report_to_commander()
            cycle_report["directors"][director_id] = report
            
            # Update org KPIs based on director data
            self._sync_director_kpis(director_id, report)
        
        # 2. Check organizational health
        health_score = self.org_kpis.calculate_health_score()
        at_risk = self.org_kpis.get_at_risk_areas()
        
        cycle_report["health_score"] = health_score
        cycle_report["at_risk_areas"] = at_risk
        
        # 3. Process pending tasks for each director
        for director_id, director in self.directors.items():
            results = director.process_pending_tasks()
            cycle_report["actions_taken"].extend([
                {"director": director_id, **r} for r in results
            ])
        
        # 4. Update mission progress
        for mission in self.missions:
            if mission.status == MissionStatus.ACTIVE:
                progress = self._calculate_mission_progress(mission)
                mission.progress = progress
                
                if progress >= 100:
                    mission.status = MissionStatus.COMPLETED
                
                cycle_report["missions"].append({
                    "id": mission.id,
                    "title": mission.title,
                    "progress": f"{progress:.1f}%",
                    "status": mission.status.value,
                })
        
        # 5. Generate escalations if needed
        if health_score < 50:
            cycle_report["escalations"].append({
                "type": "low_health_score",
                "score": health_score,
                "recommendation": "Immediate attention required on at-risk areas",
            })
        
        for area in at_risk:
            cycle_report["escalations"].append({
                "type": "kpi_at_risk",
                "area": area,
                "recommendation": f"Prioritize {area} improvement actions",
            })
        
        self._log_execution("cycle_executed", cycle_report)
        
        return cycle_report
    
    def _sync_director_kpis(self, director_id: str, report: Dict[str, Any]):
        """Sync director KPIs to organizational KPIs"""
        kpis = report.get("kpis", {})
        
        if director_id == "commerce":
            if "monthly_revenue" in kpis:
                self.org_kpis.monthly_revenue_actual = kpis["monthly_revenue"].get("current", 0)
        
        elif director_id == "growth":
            if "email_subscribers" in kpis:
                self.org_kpis.email_list_actual = int(kpis["email_subscribers"].get("current", 0))
            if "monthly_visitors" in kpis:
                self.org_kpis.monthly_traffic_actual = int(kpis["monthly_visitors"].get("current", 0))
        
        elif director_id == "brand":
            if "combined_followers" in kpis:
                self.org_kpis.social_followers_actual = int(kpis["combined_followers"].get("current", 0))
            if "communities_joined" in kpis:
                self.org_kpis.communities_actual = int(kpis["communities_joined"].get("current", 0))
        
        elif director_id == "operations":
            if "delivery_success_rate" in kpis:
                self.org_kpis.delivery_success_actual = kpis["delivery_success_rate"].get("current", 0)
            if "automation_coverage" in kpis:
                self.org_kpis.automation_coverage_actual = kpis["automation_coverage"].get("current", 0)
    
    def _calculate_mission_progress(self, mission: Mission) -> float:
        """Calculate mission progress based on KPI achievement"""
        if not mission.kpi_targets:
            return 0.0
        
        achieved = 0
        for kpi, target in mission.kpi_targets.items():
            # Check across all directors for this KPI
            for director in self.directors.values():
                if kpi in director.kpis.metrics:
                    current = director.kpis.metrics[kpi].current
                    if current >= target:
                        achieved += 1
                    break
        
        return (achieved / len(mission.kpi_targets)) * 100
    
    def _get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get mission by ID"""
        return next((m for m in self.missions if m.id == mission_id), None)
    
    def _log_execution(self, action: str, data: Dict[str, Any]):
        """Log execution for audit"""
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "data": data,
        })
    
    # =========================================================================
    # High-Level Commands (Called by external scripts or API)
    # =========================================================================
    
    def launch_revenue_sprint(self, target: float = 500, days: int = 7) -> Dict[str, Any]:
        """Launch a focused revenue generation sprint"""
        mission = self.create_mission(
            title=f"${target} Revenue Sprint",
            objective=f"Generate ${target} in revenue within {days} days",
            priority=MissionPriority.HIGH,
            directors=["commerce", "growth", "brand"],
            kpi_targets={
                "daily_revenue": target / days,
                "weekly_revenue": target,
                "orders_per_week": max(5, int(target / 50)),
            },
            deadline_days=days,
        )
        
        # Activate immediately
        activation = self.activate_mission(mission.id)
        
        # Get immediate actions from commerce director
        commerce = self.directors["commerce"]
        immediate_actions = commerce.get_priority_actions()[:5]
        
        return {
            "mission": mission.id,
            "target": f"${target}",
            "deadline": mission.deadline.isoformat(),
            "status": "launched",
            "immediate_actions": immediate_actions,
            "activation": activation,
        }
    
    def launch_brand_push(self, focus: str = "community") -> Dict[str, Any]:
        """Launch a brand awareness and community building push"""
        if focus == "community":
            kpi_targets = {
                "communities_joined": 5,
                "community_posts": 20,
                "dm_conversations": 15,
            }
        else:
            kpi_targets = {
                "combined_followers": 1000,
                "posts_per_week": 20,
                "engagement_rate": 5.0,
            }
        
        mission = self.create_mission(
            title=f"Brand Push - {focus.title()}",
            objective=f"Expand brand presence through {focus} engagement",
            priority=MissionPriority.MEDIUM,
            directors=["brand", "growth"],
            kpi_targets=kpi_targets,
            deadline_days=14,
        )
        
        self.activate_mission(mission.id)
        
        # Get brand director's plan
        brand = self.directors["brand"]
        content_calendar = brand.get_content_calendar(7)
        priority_actions = brand.get_priority_actions()
        
        return {
            "mission": mission.id,
            "focus": focus,
            "deadline": mission.deadline.isoformat(),
            "content_calendar": content_calendar,
            "priority_actions": priority_actions,
        }
    
    def launch_growth_campaign(self, channel: str = "email") -> Dict[str, Any]:
        """Launch a growth-focused campaign"""
        growth = self.directors["growth"]
        
        if channel == "email":
            kpi_targets = {
                "email_subscribers": 500,
                "new_subscribers_weekly": 100,
                "email_open_rate": 35,
            }
            # Trigger lead magnet creation
            task = growth.receive_task(
                title="Create Lead Magnet",
                description="checklist type lead magnet",
                priority=1,
            )
        else:
            kpi_targets = {
                "monthly_visitors": 2000,
                "weekly_visitors": 500,
                "leads_generated": 100,
            }
        
        mission = self.create_mission(
            title=f"Growth Campaign - {channel.title()}",
            objective=f"Accelerate growth through {channel} channel",
            priority=MissionPriority.MEDIUM,
            directors=["growth", "brand"],
            kpi_targets=kpi_targets,
            deadline_days=30,
        )
        
        self.activate_mission(mission.id)
        
        return {
            "mission": mission.id,
            "channel": channel,
            "kpi_targets": kpi_targets,
            "priority_actions": growth.get_priority_actions(),
        }
    
    def get_executive_dashboard(self) -> Dict[str, Any]:
        """Generate executive dashboard with all key metrics"""
        dashboard = {
            "generated_at": datetime.utcnow().isoformat(),
            "organization": {
                "name": "Propulse-AutonomaX",
                "health_score": self.org_kpis.calculate_health_score(),
                "at_risk_areas": self.org_kpis.get_at_risk_areas(),
            },
            "kpis": {
                "revenue": {
                    "target": self.org_kpis.monthly_revenue_target,
                    "actual": self.org_kpis.monthly_revenue_actual,
                    "progress": f"{(self.org_kpis.monthly_revenue_actual / max(1, self.org_kpis.monthly_revenue_target)) * 100:.1f}%",
                },
                "email_list": {
                    "target": self.org_kpis.email_list_target,
                    "actual": self.org_kpis.email_list_actual,
                },
                "social_followers": {
                    "target": self.org_kpis.social_followers_target,
                    "actual": self.org_kpis.social_followers_actual,
                },
                "operations": {
                    "delivery_success": f"{self.org_kpis.delivery_success_actual}%",
                    "automation_coverage": f"{self.org_kpis.automation_coverage_actual}%",
                },
            },
            "directors": {},
            "active_missions": [],
            "priority_actions": [],
        }
        
        # Collect director summaries
        for director_id, director in self.directors.items():
            report = director.report_to_commander()
            dashboard["directors"][director_id] = {
                "name": director.name,
                "tasks_pending": report["tasks"]["pending"],
                "tasks_in_progress": report["tasks"]["in_progress"],
                "at_risk_kpis": report["at_risk_kpis"],
            }
            
            # Collect priority actions
            for action in report.get("priority_actions", [])[:2]:
                dashboard["priority_actions"].append({
                    "director": director_id,
                    **action,
                })
        
        # Active missions
        for mission in self.missions:
            if mission.status in [MissionStatus.ACTIVE, MissionStatus.IN_PROGRESS]:
                dashboard["active_missions"].append({
                    "id": mission.id,
                    "title": mission.title,
                    "progress": f"{mission.progress:.1f}%",
                    "deadline": mission.deadline.isoformat(),
                    "priority": mission.priority.name,
                })
        
        # Sort priority actions
        dashboard["priority_actions"].sort(key=lambda x: x.get("priority", 5))
        
        return dashboard
    
    def record_sale(self, order_id: str, amount: float, channel: str, products: List[str]):
        """Record a sale across relevant directors"""
        # Update commerce director
        commerce = self.directors["commerce"]
        commerce.record_sale(order_id, amount, channel, products)
        
        # Update operations director for delivery
        operations = self.directors["operations"]
        for product in products:
            operations.deliver_product(order_id, product, "customer@email.com")
        
        # Update org KPIs
        self.org_kpis.monthly_revenue_actual += amount
        
        self._log_execution("sale_recorded", {
            "order_id": order_id,
            "amount": amount,
            "products": products,
        })
        
        return {
            "recorded": True,
            "order_id": order_id,
            "amount": amount,
            "org_revenue": self.org_kpis.monthly_revenue_actual,
        }


# Singleton instance for easy access
_command_center: Optional[CommandCenter] = None


def get_command_center() -> CommandCenter:
    """Get or create the Command Center singleton"""
    global _command_center
    if _command_center is None:
        _command_center = CommandCenter()
    return _command_center
