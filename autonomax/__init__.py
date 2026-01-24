"""
AutonomaX - Autonomous Business Execution System
================================================

A multi-agent AI-powered business orchestration platform that transforms
strategic intelligence into executable revenue streams.

Core Components:
- Commander Engine: Central control and director coordination
- Revenue Engine: Autonomous revenue generation and optimization
- Delivery Engine: Automated product fulfillment
- Growth Engine: Marketing automation and customer acquisition
- Orchestrator: Network bus coordination and cycle management

Quick Start:
    from autonomax import launch_business_mission
    
    result = launch_business_mission(
        title="Revenue Sprint",
        objective="Generate $500 in 48 hours",
        income_streams=["digital_products", "services"],
        time_horizon="NOW"
    )

Architecture:
- Protocol Sequence: Alexandria → BizOp → AutonomaX OS → Delivery
- Network Bus: L0 Control → L1 Domain → L2 Execution → L3 Delivery → L4 Feedback
- Operating Cadence: Daily, Weekly, Monthly cycles

"""

__version__ = "1.0.0"
__author__ = "AutonomaX Team"

from .orchestrator import (
    AutonomaXOrchestrator,
    get_orchestrator,
    launch_business_mission,
)

from .engines import (
    BaseEngine,
    CommanderEngine,
    RevenueEngine,
    DeliveryEngine,
    GrowthEngine,
)

__all__ = [
    # Main entry points
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
