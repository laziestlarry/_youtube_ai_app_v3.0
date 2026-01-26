"""
AutonomaX Orchestrator - Central Command and Control System
Implements the Network Bus Hierarchy and Protocol Sequence from knowledge base

This is the "set and forget" business execution system that coordinates
all engines and manages the organizational structure.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .engines import (
    CommanderEngine,
    RevenueEngine,
    DeliveryEngine,
    GrowthEngine,
)
from .engines.base_engine import BaseEngine, Job, JobStatus


class BusLevel(Enum):
    """Network Bus Hierarchy from knowledge base"""
    L0_CONTROL = "control"      # Orchestrator coordination, gating, approvals
    L1_DOMAIN = "domain"        # Data, BI, Process, Product, BizDev, Governance
    L2_EXECUTION = "execution"  # Task pipelines, extraction, scoring, synthesis
    L3_DELIVERY = "delivery"    # Pack assembly, manifests, final outputs
    L4_FEEDBACK = "feedback"    # Metrics, adoption signals, iteration cues


@dataclass
class BusMessage:
    """Message passed through the operation bus"""
    id: str
    bus_level: BusLevel
    source: str
    destination: str
    payload: Dict[str, Any]
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed: bool = False


@dataclass
class ExecutionCycle:
    """Represents one execution cycle of the orchestrator"""
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    jobs_processed: int = 0
    revenue_generated: float = 0.0
    errors: List[str] = field(default_factory=list)
    status: str = "running"


class AutonomaXOrchestrator:
    """
    Central orchestration system for autonomous business execution.
    
    Implements:
    - Network Bus Hierarchy (L0-L4)
    - Protocol Sequence (Alexandria → BizOp → AutonomaX OS → etc.)
    - Multi-Engine Coordination
    - Set-and-Forget Automation
    
    Cadence:
    - Continuous: Job queue processing
    - Hourly: Health checks, metric updates
    - Daily: Data health, pipeline status, risk scan
    - Weekly: KPI review, backlog grooming, delivery check
    - Monthly: Product evolution, BizOp refresh, roadmap update
    """
    
    def __init__(self, auto_start: bool = False):
        self.logger = logging.getLogger("orchestrator")
        
        # Initialize all engines
        self.commander = CommanderEngine()
        self.revenue = RevenueEngine()
        self.delivery = DeliveryEngine()
        self.growth = GrowthEngine()
        
        # Engine registry
        self.engines: Dict[str, BaseEngine] = {
            "commander": self.commander,
            "revenue": self.revenue,
            "delivery": self.delivery,
            "growth": self.growth,
        }
        
        # Message bus
        self.bus: List[BusMessage] = []
        
        # Execution tracking
        self.cycles: List[ExecutionCycle] = []
        self.current_cycle: Optional[ExecutionCycle] = None
        
        # Automation state
        self.running = False
        self.mode = "manual"  # manual, semi-auto, full-auto
        
        # Wire up engine communication
        self._setup_engine_subscriptions()
        
        if auto_start:
            self.start()
    
    def _setup_engine_subscriptions(self):
        """Set up inter-engine communication"""
        # Revenue engine notifies delivery engine on sales
        self.revenue.subscribe(lambda name, results: self._on_revenue_event(results))
        
        # Commander coordinates all engines
        self.commander.subscribe(lambda name, results: self._on_commander_event(results))
    
    def _on_revenue_event(self, results: List[Dict]):
        """Handle revenue engine events"""
        for result in results:
            if result.get("status") == "success":
                # If a sale was recorded, trigger delivery
                if "sale_id" in result.get("result", {}):
                    self.send_message(
                        bus_level=BusLevel.L3_DELIVERY,
                        source="revenue",
                        destination="delivery",
                        payload=result["result"],
                        priority=9,
                    )
    
    def _on_commander_event(self, results: List[Dict]):
        """Handle commander engine events"""
        for result in results:
            # Distribute work to appropriate engines
            if "assignments" in result.get("result", {}):
                for assignment in result["result"]["assignments"]:
                    director = assignment.get("director")
                    action = assignment.get("action")
                    
                    # Route to appropriate engine
                    if director == "commerce":
                        self.revenue.enqueue("process_action", {"action": action})
                    elif director == "growth":
                        self.growth.enqueue("process_action", {"action": action})
                    elif director == "technology":
                        self.delivery.enqueue("process_action", {"action": action})
    
    def send_message(
        self,
        bus_level: BusLevel,
        source: str,
        destination: str,
        payload: Dict[str, Any],
        priority: int = 5,
    ) -> BusMessage:
        """Send a message through the operation bus"""
        message = BusMessage(
            id=f"MSG_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            bus_level=bus_level,
            source=source,
            destination=destination,
            payload=payload,
            priority=priority,
        )
        
        self.bus.append(message)
        self.bus.sort(key=lambda m: (-m.priority, m.created_at))
        
        self.logger.debug(f"Message queued: {message.id} ({source} → {destination})")
        return message
    
    def process_bus(self) -> List[Dict[str, Any]]:
        """Process all messages in the bus"""
        results = []
        
        while self.bus:
            message = self.bus.pop(0)
            
            if message.processed:
                continue
            
            try:
                result = self._route_message(message)
                message.processed = True
                results.append({
                    "message_id": message.id,
                    "status": "processed",
                    "result": result,
                })
            except Exception as e:
                self.logger.error(f"Failed to process message {message.id}: {e}")
                results.append({
                    "message_id": message.id,
                    "status": "failed",
                    "error": str(e),
                })
        
        return results
    
    def _route_message(self, message: BusMessage) -> Dict[str, Any]:
        """Route a message to the appropriate engine"""
        destination = message.destination
        
        if destination in self.engines:
            engine = self.engines[destination]
            
            # Convert message to job
            job_type = message.payload.get("job_type", "process_message")
            engine.enqueue(job_type, message.payload, message.priority)
            
            return {"routed_to": destination, "job_type": job_type}
        
        raise ValueError(f"Unknown destination: {destination}")
    
    def start_cycle(self) -> ExecutionCycle:
        """Start a new execution cycle"""
        cycle = ExecutionCycle(
            id=f"CYCLE_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            started_at=datetime.utcnow(),
        )
        
        self.current_cycle = cycle
        self.cycles.append(cycle)
        
        self.logger.info(f"Started execution cycle: {cycle.id}")
        return cycle
    
    def run_cycle(self) -> Dict[str, Any]:
        """Execute one complete cycle of all engines"""
        if not self.current_cycle:
            self.start_cycle()
        
        cycle = self.current_cycle
        all_results = {}
        
        try:
            # 1. Process commander first (sets strategy)
            self.logger.info("Running Commander Engine")
            all_results["commander"] = self.commander.run()
            
            # 2. Process bus messages
            self.logger.info("Processing message bus")
            bus_results = self.process_bus()
            all_results["bus"] = bus_results
            
            # 3. Run domain engines
            self.logger.info("Running Revenue Engine")
            all_results["revenue"] = self.revenue.run()
            
            self.logger.info("Running Delivery Engine")
            all_results["delivery"] = self.delivery.run()
            
            self.logger.info("Running Growth Engine")
            all_results["growth"] = self.growth.run()
            
            # 4. Aggregate metrics
            cycle.jobs_processed = sum(
                r.get("jobs_processed", 0)
                for r in all_results.values()
                if isinstance(r, dict)
            )
            cycle.revenue_generated = self.revenue.metrics.revenue_generated
            cycle.status = "completed"
            
        except Exception as e:
            cycle.errors.append(str(e))
            cycle.status = "failed"
            self.logger.error(f"Cycle failed: {e}")
        
        finally:
            cycle.completed_at = datetime.utcnow()
        
        return {
            "cycle_id": cycle.id,
            "status": cycle.status,
            "jobs_processed": cycle.jobs_processed,
            "revenue_generated": cycle.revenue_generated,
            "errors": cycle.errors,
            "engine_results": all_results,
        }
    
    def launch_mission(
        self,
        title: str,
        objective: str,
        income_streams: List[str],
        time_horizon: str = "NOW",
    ) -> Dict[str, Any]:
        """
        Launch a new business mission.
        This is the main entry point for "set and forget" execution.
        """
        self.logger.info(f"Launching mission: {title}")
        
        # 1. Create mission through commander
        mission = self.commander.create_mission(
            title=title,
            objective=objective,
            income_streams=income_streams,
            time_horizon=time_horizon,
        )
        
        # 2. If time_horizon is NOW, trigger immediate revenue actions
        if time_horizon == "NOW":
            # Flash sale - import enums from growth engine
            from .engines.growth_engine import CampaignType, Channel
            self.growth.create_campaign(
                campaign_type=CampaignType.FLASH_SALE,
                name=f"Launch Campaign - {title}",
                channels=[Channel.TWITTER],
                duration_days=2,
            )
            
            # Income acceleration
            self.revenue.enqueue("accelerate_income", {"urgency": "high"}, priority=10)
            
            # DM outreach
            self.growth.enqueue("dm_outreach", {
                "platform": "twitter",
                "count": 25,
            }, priority=8)
        
        # 3. Run the cycle
        cycle_result = self.run_cycle()
        
        return {
            "mission_id": mission.id,
            "title": mission.title,
            "status": "launched",
            "tier1_actions": mission.tier1_actions,
            "kpis": mission.kpis,
            "cycle_result": cycle_result,
        }
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get unified dashboard data from all engines"""
        return {
            "orchestrator": {
                "running": self.running,
                "mode": self.mode,
                "cycles_completed": len([c for c in self.cycles if c.status == "completed"]),
                "bus_queue_length": len(self.bus),
            },
            "commander": self.commander.get_organizational_status(),
            "revenue": self.revenue.get_revenue_dashboard(),
            "delivery": self.delivery.get_delivery_dashboard(),
            "growth": self.growth.get_growth_dashboard(),
            "totals": {
                "total_revenue": self.revenue.metrics.revenue_generated,
                "total_jobs_processed": sum(
                    e.metrics.jobs_processed for e in self.engines.values()
                ),
                "overall_success_rate": sum(
                    e.metrics.success_rate for e in self.engines.values()
                ) / len(self.engines),
            },
        }
    
    def set_mode(self, mode: str):
        """Set orchestration mode: manual, semi-auto, full-auto"""
        if mode not in ["manual", "semi-auto", "full-auto"]:
            raise ValueError("Mode must be: manual, semi-auto, or full-auto")
        
        self.mode = mode
        self.logger.info(f"Orchestrator mode set to: {mode}")
        
        if mode == "full-auto":
            self.start()
    
    def start(self):
        """Start autonomous execution"""
        self.running = True
        self.logger.info("AutonomaX Orchestrator started")
    
    def stop(self):
        """Stop autonomous execution"""
        self.running = False
        self.logger.info("AutonomaX Orchestrator stopped")
    
    def save_state(self, filepath: str):
        """Save orchestrator state to file"""
        state = {
            "mode": self.mode,
            "running": self.running,
            "cycles": [
                {
                    "id": c.id,
                    "started_at": c.started_at.isoformat(),
                    "completed_at": c.completed_at.isoformat() if c.completed_at else None,
                    "jobs_processed": c.jobs_processed,
                    "revenue_generated": c.revenue_generated,
                    "status": c.status,
                }
                for c in self.cycles[-10:]  # Keep last 10 cycles
            ],
            "engine_states": {
                name: engine.get_status()
                for name, engine in self.engines.items()
            },
            "saved_at": datetime.utcnow().isoformat(),
        }
        
        Path(filepath).write_text(json.dumps(state, indent=2, default=str))
        self.logger.info(f"State saved to {filepath}")
    
    def execute_quick_win(self, action: str) -> Dict[str, Any]:
        """Execute a single quick win action"""
        actions = {
            "flash_sale": lambda: self.revenue.enqueue("accelerate_income", {"urgency": "high"}),
            "dm_outreach": lambda: self.growth.enqueue("dm_outreach", {"count": 25}),
            "content_burst": lambda: self.growth.enqueue("generate_campaign_content", {
                "campaign_type": "content_series",
                "channels": ["twitter", "linkedin"],
                "duration_days": 7,
            }),
            "review_push": lambda: self.delivery.enqueue("schedule_sequence", {
                "sequence_type": "review_request",
            }),
        }
        
        if action not in actions:
            raise ValueError(f"Unknown quick win action: {action}")
        
        actions[action]()
        result = self.run_cycle()
        
        return {
            "action": action,
            "status": "executed",
            "cycle_result": result,
        }


# Global orchestrator instance
_orchestrator: Optional[AutonomaXOrchestrator] = None


def get_orchestrator() -> AutonomaXOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AutonomaXOrchestrator()
    return _orchestrator


def launch_business_mission(
    title: str,
    objective: str,
    income_streams: List[str] = None,
    time_horizon: str = "NOW",
) -> Dict[str, Any]:
    """
    Main entry point for launching autonomous business execution.
    
    Usage:
        from autonomax.orchestrator import launch_business_mission
        
        result = launch_business_mission(
            title="First $500 Sprint",
            objective="Generate first $500 in revenue within 48 hours",
            income_streams=["shopify", "fiverr"],
            time_horizon="NOW"
        )
    """
    if income_streams is None:
        income_streams = ["digital_products", "services"]
    
    orchestrator = get_orchestrator()
    return orchestrator.launch_mission(
        title=title,
        objective=objective,
        income_streams=income_streams,
        time_horizon=time_horizon,
    )
