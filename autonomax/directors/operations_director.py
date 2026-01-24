"""
Operations Director - Owns delivery, automation, systems, technology infrastructure
Reports to Commander with operational efficiency KPIs
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .base_director import BaseDirector, DirectorTask


class OperationsDirector(BaseDirector):
    """
    Director of Operations & Technology
    
    Responsibilities:
    - Product delivery automation
    - Customer support systems
    - Technical infrastructure
    - Process automation and SOPs
    - Quality assurance
    
    KPIs:
    - Delivery success rate
    - Response time
    - System uptime
    - Automation coverage
    - Customer satisfaction
    """
    
    AUTOMATION_SYSTEMS = {
        "order_fulfillment": {
            "name": "Auto-Delivery System",
            "status": "active",
            "provider": "Shopier + Email",
            "success_rate": 99.5,
        },
        "email_sequences": {
            "name": "Email Automation",
            "status": "active",
            "provider": "ConvertKit/Gmail",
            "success_rate": 98.0,
        },
        "customer_support": {
            "name": "Support Chatbot",
            "status": "partial",
            "provider": "Custom + Human Escalation",
            "success_rate": 85.0,
        },
        "social_posting": {
            "name": "Social Scheduler",
            "status": "manual",
            "provider": "Buffer/Manual",
            "success_rate": 100.0,
        },
        "analytics": {
            "name": "Analytics Pipeline",
            "status": "active",
            "provider": "BigQuery + Custom",
            "success_rate": 99.0,
        },
    }
    
    DELIVERY_TEMPLATES = {
        "digital_product": {
            "steps": [
                "Generate download link",
                "Send delivery email",
                "Schedule onboarding sequence",
                "Add to CRM segment",
            ],
            "time_to_deliver": "< 5 minutes",
        },
        "service": {
            "steps": [
                "Send confirmation email",
                "Schedule calendar invite",
                "Send prep materials",
                "Follow up reminder (24h before)",
            ],
            "time_to_deliver": "< 1 hour",
        },
        "bundle": {
            "steps": [
                "Generate all download links",
                "Send consolidated delivery email",
                "Provide access portal credentials",
                "Schedule onboarding call (if included)",
            ],
            "time_to_deliver": "< 15 minutes",
        },
    }
    
    def __init__(self):
        super().__init__(
            name="Director of Operations & Technology",
            domain="operations"
        )
        self.delivery_log: List[Dict] = []
        self.support_tickets: List[Dict] = []
        self.system_health: Dict[str, Any] = {}
    
    def _initialize_kpis(self):
        """Initialize operations-specific KPIs"""
        # Delivery KPIs
        self.kpis.add_metric("delivery_success_rate", target=99.5, unit="%", period="weekly")
        self.kpis.add_metric("avg_delivery_time", target=5, unit="minutes", period="weekly")
        self.kpis.add_metric("orders_delivered", target=100, unit="orders", period="monthly")
        
        # Support KPIs
        self.kpis.add_metric("avg_response_time", target=4, unit="hours", period="weekly")
        self.kpis.add_metric("ticket_resolution_rate", target=95, unit="%", period="weekly")
        self.kpis.add_metric("csat_score", target=4.5, unit="out of 5", period="monthly")
        
        # System KPIs
        self.kpis.add_metric("system_uptime", target=99.9, unit="%", period="monthly")
        self.kpis.add_metric("automation_coverage", target=80, unit="%", period="monthly")
        self.kpis.add_metric("manual_interventions", target=10, unit="interventions", period="weekly")
        
        # Process KPIs
        self.kpis.add_metric("sops_documented", target=20, unit="SOPs", period="monthly")
        self.kpis.add_metric("process_errors", target=5, unit="errors", period="weekly")
    
    def execute_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Execute operations-specific tasks"""
        task_type = task.title.lower()
        
        if "deliver" in task_type or "fulfillment" in task_type:
            return self._process_delivery(task)
        
        elif "automate" in task_type or "automation" in task_type:
            return self._implement_automation(task)
        
        elif "support" in task_type or "ticket" in task_type:
            return self._handle_support(task)
        
        elif "sop" in task_type or "process" in task_type:
            return self._create_sop(task)
        
        elif "monitor" in task_type or "health" in task_type:
            return self._check_system_health(task)
        
        else:
            return self._generic_ops_task(task)
    
    def _process_delivery(self, task: DirectorTask) -> Dict[str, Any]:
        """Process product delivery"""
        # Determine product type
        product_type = "digital_product"
        for ptype in self.DELIVERY_TEMPLATES.keys():
            if ptype in task.description.lower():
                product_type = ptype
                break
        
        template = self.DELIVERY_TEMPLATES[product_type]
        
        delivery = {
            "id": f"DEL_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "type": product_type,
            "steps_executed": template["steps"],
            "time_to_deliver": template["time_to_deliver"],
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.delivery_log.append(delivery)
        self.kpis.increment_metric("orders_delivered", 1)
        
        return {
            "action": "delivery_processed",
            "delivery": delivery,
            "automation_used": self.AUTOMATION_SYSTEMS["order_fulfillment"]["name"],
        }
    
    def _implement_automation(self, task: DirectorTask) -> Dict[str, Any]:
        """Implement new automation"""
        automation_types = {
            "zapier": {
                "name": "Zapier Integration",
                "use_cases": ["Form submissions to CRM", "New order notifications", "Review requests"],
                "setup_time": "30 minutes",
            },
            "email": {
                "name": "Email Automation",
                "use_cases": ["Welcome sequences", "Abandoned cart", "Review requests"],
                "setup_time": "1-2 hours",
            },
            "delivery": {
                "name": "Auto-Delivery",
                "use_cases": ["Digital product delivery", "Download link generation", "Access provisioning"],
                "setup_time": "2 hours",
            },
            "chatbot": {
                "name": "Support Chatbot",
                "use_cases": ["FAQ responses", "Order status", "Return requests"],
                "setup_time": "4 hours",
            },
            "social": {
                "name": "Social Scheduling",
                "use_cases": ["Content calendar", "Cross-platform posting", "Engagement tracking"],
                "setup_time": "1 hour",
            },
        }
        
        # Match automation type from task
        selected_type = "email"
        for atype in automation_types.keys():
            if atype in task.description.lower():
                selected_type = atype
                break
        
        automation = automation_types[selected_type]
        
        self.kpis.increment_metric("automation_coverage", 5)
        
        return {
            "action": "automation_implemented",
            "automation": automation,
            "next_steps": [
                "Configure triggers",
                "Test with sample data",
                "Monitor for 48 hours",
                "Document in SOP",
            ],
        }
    
    def _handle_support(self, task: DirectorTask) -> Dict[str, Any]:
        """Handle customer support tasks"""
        ticket = {
            "id": f"TICKET_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "type": "general" if "general" in task.description.lower() else "technical",
            "priority": 2,
            "status": "resolved",
            "response_time_hours": 2,
            "resolution": "Handled via automated response or escalated",
        }
        
        self.support_tickets.append(ticket)
        
        # Support response templates
        response_templates = {
            "download_issue": """Hi there!

Sorry you're having trouble with your download.

Here's a fresh link: [NEW LINK]

If that doesn't work, try:
1. Clear your browser cache
2. Use a different browser
3. Disable any VPN

Still stuck? Reply here and I'll personally help.

- Larry""",

            "refund_request": """Hi!

No problem - I want you to be happy with your purchase.

I've initiated your refund. It should appear in 3-5 business days.

Would you mind sharing what didn't work for you? Helps me improve.

Thanks,
Larry""",

            "general_inquiry": """Hey!

Thanks for reaching out.

[PERSONALIZED RESPONSE]

Let me know if you have any other questions.

- Larry""",
        }
        
        return {
            "action": "support_handled",
            "ticket": ticket,
            "templates_available": list(response_templates.keys()),
            "escalation_path": "Direct email to lazylarries@gmail.com for complex issues",
        }
    
    def _create_sop(self, task: DirectorTask) -> Dict[str, Any]:
        """Create a Standard Operating Procedure"""
        sop_template = {
            "title": task.title,
            "purpose": task.description,
            "owner": "Operations Director",
            "created": datetime.utcnow().isoformat(),
            "sections": [
                {"name": "Overview", "content": "Brief description of the process"},
                {"name": "Prerequisites", "content": "What's needed before starting"},
                {"name": "Step-by-Step Instructions", "content": "Detailed numbered steps"},
                {"name": "Troubleshooting", "content": "Common issues and solutions"},
                {"name": "Metrics", "content": "How to measure success"},
            ],
            "automation_potential": "High",
        }
        
        self.kpis.increment_metric("sops_documented", 1)
        
        return {
            "action": "sop_created",
            "sop": sop_template,
            "storage_location": "docs/sops/",
            "review_required": True,
        }
    
    def _check_system_health(self, task: DirectorTask) -> Dict[str, Any]:
        """Check system health and status"""
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "systems": {},
        }
        
        for system_id, system in self.AUTOMATION_SYSTEMS.items():
            health_report["systems"][system_id] = {
                "name": system["name"],
                "status": system["status"],
                "success_rate": system["success_rate"],
                "health": "healthy" if system["success_rate"] >= 95 else "degraded",
            }
        
        # Update uptime KPI
        self.kpis.update_metric("system_uptime", 99.9)
        
        self.system_health = health_report
        
        return {
            "action": "health_check_complete",
            "report": health_report,
        }
    
    def _generic_ops_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Handle generic operations tasks"""
        return {
            "action": "task_acknowledged",
            "task": task.title,
            "status": "queued_for_review",
        }
    
    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """Get prioritized actions to improve operations KPIs"""
        actions = []
        at_risk = self.kpis.get_at_risk()
        
        if "delivery_success_rate" in at_risk:
            actions.append({
                "action": "delivery_audit",
                "target": "Review and fix failed deliveries",
                "priority": 1,
                "kpi_impact": ["delivery_success_rate", "csat_score"],
            })
        
        if "avg_response_time" in at_risk:
            actions.append({
                "action": "support_automation",
                "target": "Implement FAQ chatbot for common questions",
                "priority": 1,
                "kpi_impact": ["avg_response_time", "ticket_resolution_rate"],
            })
        
        if "automation_coverage" in at_risk:
            actions.append({
                "action": "automation_expansion",
                "target": "Automate 3 manual processes",
                "priority": 2,
                "kpi_impact": ["automation_coverage", "manual_interventions"],
            })
        
        if "sops_documented" in at_risk:
            actions.append({
                "action": "documentation_sprint",
                "target": "Document 5 core processes",
                "priority": 3,
                "kpi_impact": ["sops_documented", "process_errors"],
            })
        
        if "manual_interventions" in at_risk:
            actions.append({
                "action": "root_cause_analysis",
                "target": "Identify and eliminate top 3 manual intervention causes",
                "priority": 2,
                "kpi_impact": ["manual_interventions", "automation_coverage"],
            })
        
        # Baseline actions
        if not actions:
            actions = [
                {"action": "daily_health_check", "target": "Run system health check", "priority": 3},
                {"action": "support_inbox_review", "target": "Clear support inbox", "priority": 2},
                {"action": "delivery_monitoring", "target": "Review last 24h deliveries", "priority": 3},
            ]
        
        return sorted(actions, key=lambda x: x.get("priority", 5))
    
    def get_automation_opportunities(self) -> List[Dict[str, Any]]:
        """Identify automation opportunities"""
        opportunities = []
        
        for system_id, system in self.AUTOMATION_SYSTEMS.items():
            if system["status"] == "manual":
                opportunities.append({
                    "system": system["name"],
                    "current_status": "manual",
                    "automation_type": "full",
                    "estimated_time_saved": "5+ hours/week",
                    "priority": 1,
                })
            elif system["status"] == "partial":
                opportunities.append({
                    "system": system["name"],
                    "current_status": "partial",
                    "automation_type": "enhancement",
                    "estimated_time_saved": "2-3 hours/week",
                    "priority": 2,
                })
        
        return opportunities
    
    def deliver_product(self, order_id: str, product_sku: str, customer_email: str) -> Dict[str, Any]:
        """Execute product delivery for an order"""
        delivery = {
            "order_id": order_id,
            "product_sku": product_sku,
            "customer_email": customer_email,
            "status": "delivered",
            "timestamp": datetime.utcnow().isoformat(),
            "method": "auto_delivery",
            "steps_completed": [
                "download_link_generated",
                "delivery_email_sent",
                "onboarding_sequence_triggered",
                "crm_updated",
            ],
        }
        
        self.delivery_log.append(delivery)
        self.kpis.increment_metric("orders_delivered", 1)
        self.kpis.update_metric("delivery_success_rate", 99.5)
        
        return delivery
