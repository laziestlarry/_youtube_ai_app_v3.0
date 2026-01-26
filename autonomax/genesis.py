"""
AutonomaX Genesis Module
========================

The Genesis module is the foundational layer that unifies:
- Alexandria Protocol (Asset indexing and value extraction)
- Chimera Engine (AI-powered business intelligence)
- AutonomaX OS (Autonomous execution system)
- Command Center (KPI-driven director hierarchy)

This creates a complete, self-sustaining business operating system.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("autonomax.genesis")


@dataclass
class GenesisState:
    """Current state of the Genesis system"""
    initialized: bool = False
    last_genesis_run: Optional[str] = None
    files_indexed: int = 0
    knowledge_nodes: int = 0
    knowledge_edges: int = 0
    value_propositions: int = 0
    revenue_streams: int = 0
    target_mrr: float = 0.0
    sellable_assets: int = 0
    service_assets: int = 0
    automation_assets: int = 0


@dataclass 
class RevenueStream:
    """Revenue stream configuration"""
    id: str
    name: str
    stream_type: str  # transactional, recurring, project, high-ticket, cohort
    products: List[str]
    channels: List[str]
    target_monthly: float
    automation_level: str  # high, medium, low


class AlexandriaChimeraGenesis:
    """
    Unified Genesis System
    
    Combines:
    - Alexandria Protocol: Asset classification and value extraction
    - Chimera Engine: AI business intelligence
    - AutonomaX: Autonomous execution
    - Command Center: KPI-driven operations
    
    Creates a complete autonomous business system.
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.data_dir = self.project_root / "data" / "alexandria"
        self.docs_dir = self.project_root / "docs" / "alexandria_protocol"
        self.state = GenesisState()
        
        # Load existing state if available
        self._load_state()
    
    def _load_state(self):
        """Load existing genesis state from files"""
        try:
            # Load genesis log
            genesis_path = self.data_dir / "genesis_log.json"
            if genesis_path.exists():
                data = json.loads(genesis_path.read_text())
                self.state.files_indexed = len(data.get("genesis_log", []))
                self.state.last_genesis_run = data.get("created")
            
            # Load knowledge graph
            kg_path = self.data_dir / "knowledge_graph.json"
            if kg_path.exists():
                data = json.loads(kg_path.read_text())
                self.state.knowledge_nodes = len(data.get("nodes", []))
                self.state.knowledge_edges = len(data.get("edges", []))
            
            # Load value propositions
            vp_path = self.data_dir / "value_propositions.json"
            if vp_path.exists():
                data = json.loads(vp_path.read_text())
                self.state.value_propositions = len(data.get("propositions", []))
                summary = data.get("summary", {})
                self.state.sellable_assets = summary.get("total_sellable_assets", 0)
                self.state.service_assets = summary.get("total_service_assets", 0)
                self.state.automation_assets = summary.get("total_automation_assets", 0)
            
            # Load revenue map
            rm_path = self.data_dir / "revenue_map.json"
            if rm_path.exists():
                data = json.loads(rm_path.read_text())
                self.state.revenue_streams = len(data.get("streams", []))
                self.state.target_mrr = data.get("summary", {}).get("target_monthly_revenue", 0)
            
            self.state.initialized = True
            
        except Exception as e:
            logger.warning(f"Could not load genesis state: {e}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current genesis state"""
        return {
            "initialized": self.state.initialized,
            "last_run": self.state.last_genesis_run,
            "assets": {
                "files_indexed": self.state.files_indexed,
                "knowledge_nodes": self.state.knowledge_nodes,
                "knowledge_edges": self.state.knowledge_edges,
            },
            "value": {
                "propositions": self.state.value_propositions,
                "sellable_assets": self.state.sellable_assets,
                "service_assets": self.state.service_assets,
                "automation_assets": self.state.automation_assets,
            },
            "revenue": {
                "streams": self.state.revenue_streams,
                "target_mrr": self.state.target_mrr,
            },
        }
    
    def get_revenue_streams(self) -> List[RevenueStream]:
        """Get configured revenue streams"""
        rm_path = self.data_dir / "revenue_map.json"
        if not rm_path.exists():
            return []
        
        data = json.loads(rm_path.read_text())
        streams = []
        
        for s in data.get("streams", []):
            streams.append(RevenueStream(
                id=s["id"],
                name=s["name"],
                stream_type=s["type"],
                products=s.get("products", []),
                channels=s.get("channels", []),
                target_monthly=s.get("metrics", {}).get("target_monthly_revenue", 0),
                automation_level=s.get("automation", {}).get("fulfillment", "manual"),
            ))
        
        return streams
    
    def get_value_propositions(self) -> List[Dict[str, Any]]:
        """Get value propositions"""
        vp_path = self.data_dir / "value_propositions.json"
        if not vp_path.exists():
            return []
        
        data = json.loads(vp_path.read_text())
        return data.get("propositions", [])
    
    def get_sellable_assets(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get sellable assets from genesis log"""
        gl_path = self.data_dir / "genesis_log.json"
        if not gl_path.exists():
            return []
        
        data = json.loads(gl_path.read_text())
        entries = data.get("genesis_log", [])
        
        sellable = [
            e for e in entries
            if e.get("value_signals", {}).get("sellable")
        ]
        
        return sellable[:limit]
    
    def get_service_capabilities(self) -> List[Dict[str, Any]]:
        """Get service-ready capabilities"""
        kg_path = self.data_dir / "knowledge_graph.json"
        if not kg_path.exists():
            return []
        
        data = json.loads(kg_path.read_text())
        nodes = data.get("nodes", [])
        
        capabilities = [n for n in nodes if n.get("type") == "capability"]
        return capabilities
    
    def generate_execution_plan(self) -> Dict[str, Any]:
        """Generate execution plan based on current state"""
        streams = self.get_revenue_streams()
        propositions = self.get_value_propositions()
        
        # Prioritize by automation level and target revenue
        prioritized_streams = sorted(
            streams,
            key=lambda s: (
                0 if s.automation_level == "automatic" else 1 if s.automation_level == "semi-automatic" else 2,
                -s.target_monthly
            )
        )
        
        plan = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "phases": [],
        }
        
        # Phase 1: Immediate Revenue (0-48h)
        plan["phases"].append({
            "name": "Immediate Revenue",
            "timeframe": "0-48 hours",
            "focus": "Digital product sales via existing channels",
            "actions": [
                "Activate flash sale on Shopier (LAZY20 code)",
                "Post launch content to LinkedIn, Twitter, Facebook",
                "Join Indie Hackers and post introduction",
                "Monitor for first orders",
            ],
            "target_revenue": 500,
            "streams": ["STREAM-DIGITAL"],
        })
        
        # Phase 2: Community Momentum (Week 1)
        plan["phases"].append({
            "name": "Community Momentum",
            "timeframe": "Days 3-7",
            "focus": "Build social proof and community presence",
            "actions": [
                "Engage in 5 communities daily",
                "Publish 2 value posts per day",
                "Collect and share testimonials",
                "Create lead magnet landing page",
            ],
            "target_revenue": 1000,
            "streams": ["STREAM-DIGITAL", "STREAM-TRAINING"],
        })
        
        # Phase 3: Service Activation (Week 2-3)
        plan["phases"].append({
            "name": "Service Activation",
            "timeframe": "Days 8-21",
            "focus": "Launch service offerings on Fiverr",
            "actions": [
                "Create 3 Fiverr gigs from service capabilities",
                "Optimize gig SEO and descriptions",
                "Launch outreach campaign",
                "Set up client onboarding automation",
            ],
            "target_revenue": 3000,
            "streams": ["STREAM-SERVICES"],
        })
        
        # Phase 4: Recurring Revenue (Month 2)
        plan["phases"].append({
            "name": "Recurring Revenue",
            "timeframe": "Days 22-60",
            "focus": "Establish subscription and retainer models",
            "actions": [
                "Launch subscription tier on Shopier",
                "Create membership benefits package",
                "Implement retention automation",
                "Target first 20 subscribers",
            ],
            "target_revenue": 5000,
            "streams": ["STREAM-SUBSCRIPTION"],
        })
        
        # Phase 5: Scale & Consulting (Month 3)
        plan["phases"].append({
            "name": "Scale & Consulting",
            "timeframe": "Days 61-90",
            "focus": "High-ticket consulting and partnerships",
            "actions": [
                "Launch consulting offering via LinkedIn",
                "Create case studies from early clients",
                "Establish partnership pipeline",
                "Target first enterprise engagement",
            ],
            "target_revenue": 15000,
            "streams": ["STREAM-CONSULTING"],
        })
        
        # Calculate totals
        plan["summary"] = {
            "total_phases": len(plan["phases"]),
            "target_90_day_revenue": sum(p["target_revenue"] for p in plan["phases"]),
            "primary_streams": [s.id for s in prioritized_streams[:3]],
        }
        
        return plan
    
    def sync_with_command_center(self) -> Dict[str, Any]:
        """Sync genesis data with Command Center"""
        from .command_center import get_command_center
        
        cc = get_command_center()
        streams = self.get_revenue_streams()
        
        # Update commerce director with revenue targets
        commerce = cc.directors["commerce"]
        total_digital_target = sum(
            s.target_monthly for s in streams 
            if s.stream_type == "transactional"
        )
        commerce.kpis.metrics["monthly_revenue"].target = total_digital_target
        
        # Update growth director with channel targets
        growth = cc.directors["growth"]
        # Email list target based on conversion math
        growth.kpis.metrics["email_subscribers"].target = int(total_digital_target / 5)  # $5 per subscriber
        
        # Update org KPIs
        cc.org_kpis.monthly_revenue_target = self.state.target_mrr
        
        return {
            "synced": True,
            "revenue_target_updated": self.state.target_mrr,
            "streams_configured": len(streams),
        }


# Singleton instance
_genesis: Optional[AlexandriaChimeraGenesis] = None


def get_genesis() -> AlexandriaChimeraGenesis:
    """Get the Genesis singleton"""
    global _genesis
    if _genesis is None:
        _genesis = AlexandriaChimeraGenesis()
    return _genesis


def run_genesis_completion() -> Dict[str, Any]:
    """Run complete genesis initialization and return status"""
    import subprocess
    import sys
    
    project_root = Path(__file__).parent.parent
    script_path = project_root / "scripts" / "run_alexandria_chimera_genesis.py"
    
    # Run the genesis script
    result = subprocess.run(
        [sys.executable, str(script_path), "--full"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    
    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr,
        }
    
    # Reload genesis state
    genesis = get_genesis()
    genesis._load_state()
    
    # Sync with command center
    sync_result = genesis.sync_with_command_center()
    
    return {
        "success": True,
        "state": genesis.get_state(),
        "sync": sync_result,
        "execution_plan": genesis.generate_execution_plan(),
    }
