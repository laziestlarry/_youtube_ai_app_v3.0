"""
AutonomaX Central Registry
==========================

Single source of truth for all autonomous systems:
- Directors (KPI-driven execution)
- Engines (Task processing)  
- Workflows (Automated sequences)
- Real Executors (External API integrations)

This registry enables the Command Center to orchestrate all components
toward organizational KPI targets.
"""

import logging
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Import Directors
from .directors import (
    BaseDirector,
    BrandDirector,
    CommerceDirector,
    GrowthDirector,
    OperationsDirector,
)

# Import Engines
from .engines import (
    BaseEngine,
    CommanderEngine,
    RevenueEngine,
    DeliveryEngine,
    GrowthEngine,
)

# Import Workflows
from .workflows.registry import WORKFLOW_REGISTRY, get_workflow, list_workflows

# Import Real Executors
from .real_execution import (
    ShopierExecutor,
    SocialMediaExecutor,
    BrowserAgent,
)

logger = logging.getLogger("autonomax.registry")


class ComponentType(Enum):
    DIRECTOR = "director"
    ENGINE = "engine"
    WORKFLOW = "workflow"
    EXECUTOR = "executor"


@dataclass
class ComponentInfo:
    """Metadata about a registered component"""
    id: str
    name: str
    component_type: ComponentType
    instance: Any
    kpis: List[str] = field(default_factory=list)
    status: str = "active"
    last_executed: Optional[datetime] = None
    execution_count: int = 0


class AutonomaXRegistry:
    """
    Central Registry for all AutonomaX components.
    
    Provides:
    - Single point of access to all directors, engines, workflows, executors
    - Component health monitoring
    - Cross-component communication
    - KPI mapping to responsible components
    """
    
    _instance: Optional["AutonomaXRegistry"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.components: Dict[str, ComponentInfo] = {}
        self.kpi_ownership: Dict[str, str] = {}  # KPI -> component_id
        
        # Initialize all components
        self._register_directors()
        self._register_engines()
        self._register_workflows()
        self._register_executors()
        self._map_kpi_ownership()
        
        logger.info(f"Registry initialized with {len(self.components)} components")
    
    def _register_directors(self):
        """Register all director instances"""
        directors = [
            ("brand_director", "Brand Director", BrandDirector()),
            ("commerce_director", "Commerce Director", CommerceDirector()),
            ("growth_director", "Growth Director", GrowthDirector()),
            ("operations_director", "Operations Director", OperationsDirector()),
        ]
        
        for comp_id, name, instance in directors:
            kpis = list(instance.kpis.metrics.keys()) if hasattr(instance, 'kpis') else []
            self.components[comp_id] = ComponentInfo(
                id=comp_id,
                name=name,
                component_type=ComponentType.DIRECTOR,
                instance=instance,
                kpis=kpis,
            )
    
    def _register_engines(self):
        """Register all engine instances"""
        engines = [
            ("commander_engine", "Commander Engine", CommanderEngine()),
            ("revenue_engine", "Revenue Engine", RevenueEngine()),
            ("delivery_engine", "Delivery Engine", DeliveryEngine()),
            ("growth_engine", "Growth Engine", GrowthEngine()),
        ]
        
        for comp_id, name, instance in engines:
            self.components[comp_id] = ComponentInfo(
                id=comp_id,
                name=name,
                component_type=ComponentType.ENGINE,
                instance=instance,
            )
    
    def _register_workflows(self):
        """Register all workflows from workflow registry"""
        for workflow_id, workflow in WORKFLOW_REGISTRY.items():
            self.components[f"workflow_{workflow_id}"] = ComponentInfo(
                id=f"workflow_{workflow_id}",
                name=workflow.name if hasattr(workflow, 'name') else workflow_id,
                component_type=ComponentType.WORKFLOW,
                instance=workflow,
            )
    
    def _register_executors(self):
        """Register real execution components"""
        executors = [
            ("shopier_executor", "Shopier Executor", ShopierExecutor()),
            ("social_executor", "Social Media Executor", SocialMediaExecutor()),
            ("browser_agent", "Browser Agent", BrowserAgent()),
        ]
        
        for comp_id, name, instance in executors:
            self.components[comp_id] = ComponentInfo(
                id=comp_id,
                name=name,
                component_type=ComponentType.EXECUTOR,
                instance=instance,
            )
    
    def _map_kpi_ownership(self):
        """Map each KPI to its owning component"""
        # Brand Director KPIs
        brand_kpis = [
            "linkedin_connections", "twitter_followers", "combined_followers",
            "engagement_rate", "posts_per_week", "replies_per_week",
            "communities_joined", "community_posts", "brand_mentions",
            "dm_conversations", "leads_from_social",
        ]
        for kpi in brand_kpis:
            self.kpi_ownership[kpi] = "brand_director"
        
        # Commerce Director KPIs
        commerce_kpis = [
            "monthly_revenue", "weekly_revenue", "daily_revenue",
            "orders_per_week", "aov", "conversion_rate",
            "products_live", "channels_active", "new_customers",
            "repeat_purchase_rate",
        ]
        for kpi in commerce_kpis:
            self.kpi_ownership[kpi] = "commerce_director"
        
        # Growth Director KPIs
        growth_kpis = [
            "monthly_visitors", "weekly_visitors", "email_subscribers",
            "email_open_rate", "email_click_rate", "new_subscribers_weekly",
            "leads_generated", "lead_conversion_rate", "active_partnerships",
            "referral_revenue", "content_pieces_published", "seo_keywords_ranking",
        ]
        for kpi in growth_kpis:
            self.kpi_ownership[kpi] = "growth_director"
        
        # Operations Director KPIs
        ops_kpis = [
            "delivery_success_rate", "avg_delivery_time", "orders_delivered",
            "avg_response_time", "ticket_resolution_rate", "csat_score",
            "system_uptime", "automation_coverage", "manual_interventions",
            "sops_documented", "process_errors",
        ]
        for kpi in ops_kpis:
            self.kpi_ownership[kpi] = "operations_director"
    
    # =========================================================================
    # Component Access Methods
    # =========================================================================
    
    def get_component(self, component_id: str) -> Optional[ComponentInfo]:
        """Get a component by ID"""
        return self.components.get(component_id)
    
    def get_director(self, director_id: str) -> Optional[BaseDirector]:
        """Get a director instance"""
        comp = self.components.get(director_id)
        if comp and comp.component_type == ComponentType.DIRECTOR:
            return comp.instance
        return None
    
    def get_engine(self, engine_id: str) -> Optional[BaseEngine]:
        """Get an engine instance"""
        comp = self.components.get(engine_id)
        if comp and comp.component_type == ComponentType.ENGINE:
            return comp.instance
        return None
    
    def get_executor(self, executor_id: str) -> Any:
        """Get an executor instance"""
        comp = self.components.get(executor_id)
        if comp and comp.component_type == ComponentType.EXECUTOR:
            return comp.instance
        return None
    
    def get_components_by_type(self, comp_type: ComponentType) -> Dict[str, ComponentInfo]:
        """Get all components of a specific type"""
        return {
            k: v for k, v in self.components.items()
            if v.component_type == comp_type
        }
    
    def get_kpi_owner(self, kpi: str) -> Optional[str]:
        """Get the component responsible for a KPI"""
        return self.kpi_ownership.get(kpi)
    
    # =========================================================================
    # Director Operations
    # =========================================================================
    
    def get_all_directors(self) -> Dict[str, BaseDirector]:
        """Get all director instances"""
        return {
            comp_id: comp.instance
            for comp_id, comp in self.components.items()
            if comp.component_type == ComponentType.DIRECTOR
        }
    
    def collect_director_reports(self) -> Dict[str, Dict]:
        """Collect status reports from all directors"""
        reports = {}
        for comp_id, director in self.get_all_directors().items():
            reports[comp_id] = director.report_to_commander()
        return reports
    
    def get_all_at_risk_kpis(self) -> Dict[str, List[str]]:
        """Get all at-risk KPIs across all directors"""
        at_risk = {}
        for comp_id, director in self.get_all_directors().items():
            director_at_risk = director.kpis.get_at_risk()
            if director_at_risk:
                at_risk[comp_id] = director_at_risk
        return at_risk
    
    def get_all_priority_actions(self, limit: int = 10) -> List[Dict]:
        """Get prioritized actions from all directors"""
        actions = []
        for comp_id, director in self.get_all_directors().items():
            for action in director.get_priority_actions():
                actions.append({
                    "director": comp_id,
                    **action,
                })
        
        # Sort by priority
        actions.sort(key=lambda x: x.get("priority", 5))
        return actions[:limit]
    
    # =========================================================================
    # Executor Operations
    # =========================================================================
    
    def execute_shopier_deployment(self, dry_run: bool = False) -> Dict:
        """Execute Shopier product deployment"""
        executor = self.get_executor("shopier_executor")
        if not executor:
            return {"error": "Shopier executor not found"}
        
        if dry_run:
            return {"status": "dry_run", "products": len(executor.PRODUCT_CATALOG)}
        
        return executor.deploy_all_products()
    
    def execute_social_posting(self, content: str, platforms: List[str] = None) -> Dict:
        """Execute social media posting"""
        executor = self.get_executor("social_executor")
        if not executor:
            return {"error": "Social executor not found"}
        
        return executor.post_to_platforms(content, platforms or ["twitter", "linkedin"])
    
    # =========================================================================
    # Status and Health
    # =========================================================================
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get complete registry status"""
        directors = self.get_components_by_type(ComponentType.DIRECTOR)
        engines = self.get_components_by_type(ComponentType.ENGINE)
        workflows = self.get_components_by_type(ComponentType.WORKFLOW)
        executors = self.get_components_by_type(ComponentType.EXECUTOR)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_components": len(self.components),
            "breakdown": {
                "directors": len(directors),
                "engines": len(engines),
                "workflows": len(workflows),
                "executors": len(executors),
            },
            "directors": {k: {"name": v.name, "kpis": len(v.kpis)} for k, v in directors.items()},
            "engines": {k: v.name for k, v in engines.items()},
            "workflows": list(workflows.keys()),
            "executors": {k: v.name for k, v in executors.items()},
            "kpi_coverage": len(self.kpi_ownership),
        }
    
    def get_health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall": "healthy",
            "components": {},
        }
        
        issues = []
        
        for comp_id, comp in self.components.items():
            comp_health = "healthy"
            
            # Check directors for at-risk KPIs
            if comp.component_type == ComponentType.DIRECTOR:
                at_risk = comp.instance.kpis.get_at_risk()
                if len(at_risk) > len(comp.kpis) * 0.5:
                    comp_health = "degraded"
                    issues.append(f"{comp_id}: {len(at_risk)} KPIs at risk")
            
            health["components"][comp_id] = {
                "name": comp.name,
                "type": comp.component_type.value,
                "status": comp_health,
            }
        
        if issues:
            health["overall"] = "degraded"
            health["issues"] = issues
        
        return health


# Singleton accessor
_registry: Optional[AutonomaXRegistry] = None


def get_registry() -> AutonomaXRegistry:
    """Get the singleton registry instance"""
    global _registry
    if _registry is None:
        _registry = AutonomaXRegistry()
    return _registry


# =========================================================================
# Convenience Functions
# =========================================================================

def list_all_components() -> Dict[str, List[str]]:
    """List all registered components by type"""
    registry = get_registry()
    status = registry.get_registry_status()
    return {
        "directors": list(status["directors"].keys()),
        "engines": list(status["engines"].keys()),
        "workflows": status["workflows"],
        "executors": list(status["executors"].keys()),
    }


def get_director(director_id: str) -> Optional[BaseDirector]:
    """Get a director by ID"""
    return get_registry().get_director(director_id)


def get_priority_actions(limit: int = 10) -> List[Dict]:
    """Get top priority actions across all directors"""
    return get_registry().get_all_priority_actions(limit)


def get_at_risk_kpis() -> Dict[str, List[str]]:
    """Get all at-risk KPIs"""
    return get_registry().get_all_at_risk_kpis()
