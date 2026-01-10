import os
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.api.deps import get_current_user, get_optional_current_user
from backend.models.user import User
from modules.ai_agency.direction_board import direction_board
from modules.ai_agency.altered_self import get_altered_self
from backend.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()

class ShopierLinkRequest(BaseModel):
    amount: float
    currency: str = "USD"
    product_name: str
    order_id: str

class AgencyExecutionRequest(BaseModel):
    objective: str
    department: str

class SalesOrchestrationRequest(BaseModel):
    operation: str # e.g., 'deploy_storefront', 'audit_inventory'
    details: Dict[str, Any] = {}

class ServiceOrchestrationRequest(BaseModel):
    workflow_id: str # e.g., 'fiverr_gig_automation'
    parameters: Dict[str, Any] = {}

class QuantumOrchestrationRequest(BaseModel):
    intent: str # e.g., 'Maximize Revenue'

class SprintRequest(BaseModel):
    target: float = 2000.0
    duration: int = 2
    intensity: str = "EXTREME"

@router.get("/departments")
async def get_departments(current_user: User = Depends(get_current_user)):
    """List available AI Agency departments."""
    return direction_board.list_departments()

@router.post("/execute")
async def execute_task(
    request: AgencyExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute a task using the AI Agency orchestrator."""
    # Apply Altered Self personalization
    altered_self = get_altered_self(str(current_user.id))
    personalized_objective = altered_self.infuse_context(request.objective)
    
    result = await direction_board.execute_workflow(
        personalized_objective, 
        request.department
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.post("/orchestrate/sales")
async def orchestrate_sales(
    request: SalesOrchestrationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger a Sales Department operation (Storefront, Inventory).
    """
    return await direction_board.execute_sales_operation(request.operation, request.details)

@router.post("/orchestrate/service")
async def orchestrate_service(
    request: ServiceOrchestrationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger a Service Department workflow (Agency Execution).
    """
    # Map workflow_id to an objective for the Operations department
    if request.workflow_id == "fiverr_gig_automation":
        objective = "Execute Fiverr Gig: Auto-Post 'AI Content Services' and monitor for orders."
    elif request.workflow_id == "youtube_automation":
        objective = "Run YouTube Content Engine for channel scaling."
    else:
        objective = f"Execute workflow: {request.workflow_id}"
        
    return await direction_board.execute_workflow(objective, "operations")

@router.post("/orchestrate/quantum")
async def orchestrate_quantum(
    request: QuantumOrchestrationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger a Quantum-Entangled intent (superposition of Sales + Ops).
    """
    return await direction_board.execute_quantum_intent(request.intent)

@router.post("/orchestrate/master")
async def orchestrate_master(
    current_user: User = Depends(get_current_user)
):
    """
    Master Trigger for Scheduled Automation.
    Executes a sequence of Sales Refresh -> Quantum Scaling.
    """
    results = {}
    
    # 1. Refresh Storefront
    results["sales_refresh"] = await direction_board.execute_sales_operation("deploy_storefront")
    
    # 2. Quantum Intent
    intent = "Execute horizontal scaling across high-CPM niches and maximize revenue velocity."
    results["quantum_scaling"] = await direction_board.execute_quantum_intent(intent)
    
    return {
        "status": "master_pulse_complete",
        "timestamp": datetime.now().isoformat(),
        "details": results
    }

@router.post("/orchestrate/skigen")
async def orchestrate_skigen(
    request: SalesOrchestrationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Autonomous SKU Generation & Publication.
    Generates a new AI product bundle and pushes it to Shopify.
    """
    if not request.details:
        # Generate a demo bundle if no details provided
        sku_id = datetime.now().strftime("%y%m%d%H%M")
        request.details = {
            "title": f"AutonomaX Quantum Bundle v{sku_id}",
            "description": "Exclusive AI-generated strategic asset for high-ticket market dominance.",
            "price": 499.0,
            "sku": f"AX-QM-{sku_id}",
            "status": "ACTIVE",
            "images": ["https://images.unsplash.com/photo-1677442136019-21780ecad995"] # Placeholder AI art
        }
    
    return await direction_board.execute_sales_operation("publish_shopify_sku", request.details)

@router.post("/orchestrate/pulse")
async def orchestrate_pulse(
    phase: str = "daily",
    current_user: Optional[User] = Depends(get_optional_current_user),
    secret_key: Optional[str] = None
):
    """
    Master Trigger for Autonomous Ignition Pulse.
    Allows secret_key bypass for Cloud Scheduler.
    """
    if not current_user and secret_key != os.getenv("ADMIN_SECRET_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    results = {}
    
    # 1. Sales Refresh & Inventory Audit
    results["inventory"] = await direction_board.execute_sales_operation("audit_inventory")
    
    # 2. Market Dominance / Asset Preparation
    if phase in ["daily", "weekly"]:
        results["market_prep"] = await direction_board.execute_sales_operation("prepare_marketing_assets")
    
    # 3. Quantum Intent for Revenue Realization
    intent = f"Execute phase: {phase}. Maximize income through autonomous SKU publication and UTM link generation."
    results["quantum_intent"] = await direction_board.execute_quantum_intent(intent)
    
    return {
        "status": "ignition_pulse_emitted",
        "phase": phase,
        "timestamp": datetime.now().isoformat(),
        "performance_metrics": results
    }

@router.post("/orchestrate/sprint")
async def orchestrate_sprint(
    request: SprintRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Quantum Sprint: High-velocity revenue generation protocol.
    Targets a specific amount within a tight window.
    """
    intent = (
        f"QUANTUM SPRINT ACTIVE: Generate ${request.target} in {request.duration} hours. "
        f"Velocity: {request.intensity}. Priority: High-Ticket Ignition Assets. "
        "Engage Core AI Commanders for aggressive market penetration."
    )
    
    # Use execute_quantum_intent which collapses multiple tasks
    result = await direction_board.execute_quantum_intent(intent)
    
    # Also trigger a fulfillment event directly for the sprint seed
    from modules.ai_agency.fulfillment_engine import fulfillment_engine
    payout = await fulfillment_engine.simulate_work(
        f"Quantum Sprint Execution: {request.target}",
        f"Mission: {intent}",
        protocol_tier="launch_event"
    )
    
    return {
        "status": "quantum_sprint_ignited",
        "objective": f"${request.target} / {request.duration}hr",
        "orchestration": result,
        "immediate_payout": payout,
        "timestamp": datetime.now().isoformat()
    }

from backend.api.deps import get_current_user, get_async_db as get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.analytics_service import analytics_service

@router.get("/revenue-stats")
async def get_revenue_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get 'Land Ignite' revenue statistics from actual data.
    """
    stats = await analytics_service.get_channel_stats(current_user.id, db)
    forecast = await analytics_service.forecast_revenue(current_user.id, db)
    history = await analytics_service.get_revenue_history(current_user.id, 30, db)
    
    # Calculate daily average from history
    daily_avg = 0.0
    if history:
        daily_avg = sum(h["revenue"] for h in history) / len(history)
    
    return {
        "monthly_estimate": forecast.get("projected_revenue", 0.0),
        "daily_average": round(daily_avg, 2),
        "active_campaigns": len(history), # Using history points as 'activity' metric for now
        "projected_yearly": forecast.get("projected_revenue", 0.0) * 12,
        "currency": "USD"
    }

@router.post("/monetize/shopier-link")
async def generate_shopier_link(
    request: ShopierLinkRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a Shopier payment link for a product/service."""
    link = await payment_service.create_shopier_payment(
        amount=request.amount,
        currency=request.currency,
        order_id=request.order_id,
        product_name=request.product_name
    )
    return {"payment_link": link, "order_id": request.order_id}
