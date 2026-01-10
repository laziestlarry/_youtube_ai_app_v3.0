from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .models import GrowthLedgerEntry

class AnomalyService:
    """
    Watchdog for the Growth Engine.
    Detects:
    - DNA Crashes (>20% drop vs yesterday)
    - Zero Signal (No events in 24h)
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_dnr_for_date(self, date_obj) -> float:
        val = self.db.query(func.sum(GrowthLedgerEntry.amount_cents))\
            .filter(GrowthLedgerEntry.status == "CLEARED")\
            .filter(func.date(GrowthLedgerEntry.created_at) == date_obj)\
            .scalar()
        return float(val or 0) / 100.0

    def check_anomalies(self) -> list:
        alerts = []
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        dnr_today = self.get_dnr_for_date(today)
        dnr_yesterday = self.get_dnr_for_date(yesterday)
        
        # 1. DNR Crash Check (only if yesterday had revenue)
        if dnr_yesterday > 10.0:
            drop_pct = (dnr_yesterday - dnr_today) / dnr_yesterday
            if drop_pct > 0.20:
                alerts.append({
                    "level": "CRITICAL",
                    "type": "REVENUE_DIP",
                    "message": f"DNR is down {int(drop_pct*100)}% vs yesterday.",
                    "action": "Check ad spend & site uptime."
                })
        
        # 2. Silence Check (No events today?)
        count = self.db.query(GrowthLedgerEntry)\
            .filter(func.date(GrowthLedgerEntry.created_at) == today)\
            .count()
            
        if count == 0:
             alerts.append({
                "level": "WARNING",
                "type": "NO_SIGNAL",
                "message": "Zero revenue events recorded today.",
                "action": "Verify webhook connections."
            })
            
        return alerts

class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def list_workflows(self):
        from .models import BusinessWorkflow
        return self.db.query(BusinessWorkflow).all()

    def create_workflow(self, name: str, trigger: str, steps: list, autonomous: bool = True):
        from .models import BusinessWorkflow
        wf = BusinessWorkflow(
            name=name, 
            trigger_event=trigger, 
            logic_steps=steps, 
            is_autonomous=1 if autonomous else 0
        )
        self.db.add(wf)
        self.db.commit()
        self.db.refresh(wf)
        return wf

    def trigger_workflow(self, trigger_event: str, context: Dict[str, Any]):
        from .models import BusinessWorkflow
        workflows = self.db.query(BusinessWorkflow).filter(BusinessWorkflow.trigger_event == trigger_event).all()
        
        results = []
        for wf in workflows:
            if wf.is_autonomous:
                # In a real system, this would trigger an async task runner
                # For V1, we log the execution intent
                execution_log = {
                    "workflow": wf.name,
                    "status": "triggered",
                    "steps": wf.logic_steps,
                    "context": context,
                    "timestamp": datetime.utcnow().isoformat()
                }
                results.append(execution_log)
                print(f"Workflow Triggered: {wf.name} on event {trigger_event}")
        
        return results
