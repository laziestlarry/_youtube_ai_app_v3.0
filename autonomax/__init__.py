"""
AutonomaX - Autonomous Business Execution System
================================================

A multi-agent AI-powered business orchestration platform that transforms
strategic intelligence into executable revenue streams.

ORGANIZATIONAL HIERARCHY:
    Propulse-AutonomaX (Holding)
    └── Command Center
        ├── Brand Director      → Social, Communities, Lazy Larry
        ├── Commerce Director   → Revenue, Pricing, Channels
        ├── Growth Director     → Traffic, Email, Partnerships
        └── Operations Director → Delivery, Automation, Support

Core Components:
- Command Center: KPI-driven orchestration of all directors
- Directors: Specialized agents with domain accountability
- Engines: Task processing and execution
- Executors: Real API integrations (Shopier, Social, etc.)
- Workflows: Automated multi-step sequences

Quick Start:
    from autonomax import get_command_center
    
    # Launch revenue sprint
    cc = get_command_center()
    result = cc.launch_revenue_sprint(target=500, days=7)
    
    # Get executive dashboard
    dashboard = cc.get_executive_dashboard()
    
    # Execute operational cycle
    cycle_result = cc.execute_cycle()

Architecture:
- Protocol Sequence: Alexandria → BizOp → AutonomaX OS → Delivery
- Network Bus: L0 Control → L1 Domain → L2 Execution → L3 Delivery → L4 Feedback
- Operating Cadence: Daily, Weekly, Monthly cycles

"""

__version__ = "2.0.0"
__author__ = "Propulse-AutonomaX"

# Command Center (Primary Interface)
from .command_center import (
    CommandCenter,
    get_command_center,
    Mission,
    MissionPriority,
    MissionStatus,
)

# Registry (Component Access)
from .registry import (
    get_registry,
    list_all_components,
    get_director,
    get_priority_actions,
    get_at_risk_kpis,
)

# Directors
from .directors import (
    BaseDirector,
    BrandDirector,
    CommerceDirector,
    GrowthDirector,
    OperationsDirector,
)

# Orchestrator (Legacy Interface)
from .orchestrator import (
    AutonomaXOrchestrator,
    get_orchestrator,
    launch_business_mission,
)

# Engines
from .engines import (
    BaseEngine,
    CommanderEngine,
    RevenueEngine,
    DeliveryEngine,
    GrowthEngine,
)

__all__ = [
    # Command Center (Primary)
    "CommandCenter",
    "get_command_center",
    "Mission",
    "MissionPriority",
    "MissionStatus",
    
    # Registry
    "get_registry",
    "list_all_components",
    "get_director",
    "get_priority_actions",
    "get_at_risk_kpis",
    
    # Directors
    "BaseDirector",
    "BrandDirector",
    "CommerceDirector",
    "GrowthDirector",
    "OperationsDirector",
    
    # Orchestrator (Legacy)
    "AutonomaXOrchestrator",
    "get_orchestrator",
    "launch_business_mission",
    
    # Engines
    "BaseEngine",
    "CommanderEngine",
    "RevenueEngine",
    "DeliveryEngine",
    "GrowthEngine",
]
