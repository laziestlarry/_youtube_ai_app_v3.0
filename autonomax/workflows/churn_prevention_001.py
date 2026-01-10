from .base import BaseWorkflow, WorkflowContext, WorkflowResult

class ChurnPrevention001Workflow(BaseWorkflow):
    id = "churn_prevention_001"

    async def execute(self, ctx: WorkflowContext) -> WorkflowResult:
        predicted_churn = int(ctx.conditions_met.get("predicted_churn", 0))
        customer_value = str(ctx.conditions_met.get("customer_value", "")).lower()
        customer_id = str(ctx.payload.get("customer_id", ""))
        reason_code = str(ctx.payload.get("reason_code", "unknown"))
        action = str(ctx.payload.get("action", "assign_success_manager"))

        if not customer_id:
            return WorkflowResult(status="rejected", reason="missing_customer_id", workflow_id=self.id)

        if predicted_churn != 1:
            return WorkflowResult(status="ignored", reason="predicted_churn_not_met", workflow_id=self.id, customer_id=customer_id)

        escalation = "high_touch" if customer_value in {"high", "vip", "enterprise"} else "standard"

        tasks = [
            {
                "type": "create_ticket",
                "system": "support",
                "priority": "p1" if escalation == "high_touch" else "p2",
                "title": f"Churn risk: {customer_id}",
                "details": {
                    "customer_id": customer_id,
                    "reason_code": reason_code,
                    "customer_value": customer_value,
                    "trigger_source": ctx.trigger_source,
                },
            }
        ]

        if action == "assign_success_manager":
            tasks.append({
                "type": "assign_owner",
                "system": "crm",
                "role": "success_manager",
                "customer_id": customer_id,
                "mode": escalation,
            })

        if escalation == "high_touch":
            tasks.append({
                "type": "send_offer",
                "system": "email",
                "template": "retention_high_value_v1",
                "customer_id": customer_id,
                "offer": "personal_outreach + 15% loyalty credit",
            })
        else:
            tasks.append({
                "type": "add_to_campaign",
                "system": "marketing",
                "campaign_id": "retention_standard_v1",
                "customer_id": customer_id,
            })

        return WorkflowResult(
            status="executed",
            workflow_id=self.id,
            customer_id=customer_id,
            escalation_level=escalation,
            tasks=tasks,
        )
