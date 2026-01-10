from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from modules.ai_agency.shopier_service import shopier_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/shopier/pay")
async def shopier_payment_redirect(
    amount: float = Query(..., description="The amount to charge"),
    currency: str = Query("USD", description="Currency code (USD, EUR, etc)"),
    order_id: str = Query(..., description="Unique platform order ID"),
    product_name: str = Query(..., description="Name of the product/service")
):
    """
    Generates and returns the auto-submitting Shopier payment form.
    This is the 'Real' gateway bridge for the storefront.
    """
    try:
        logger.info(f"Initiating Real Payment: {product_name} - ${amount} {currency} (Order: {order_id})")
        
        # This returns the full auto-submitting HTML page
        html_content = shopier_service.generate_payment_link(
            amount=amount,
            currency_code=currency,
            order_id=order_id,
            product_name=product_name
        )
        
        # If the service returned a mock link (keys missing), we should probably fail or handle it
        if html_content.startswith("http"):
            # It's a mock link, return a redirect or just the link text
             logger.warning("Shopier in Mock Mode - Returning Redirect to Mock Link")
             # In a real activation, we want this to be obvious
             return HTMLResponse(content=f'<html><body><p>Keys missing. <a href="{html_content}">Click here for mock payment</a></p></body></html>')

        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Shopier Redirect Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Payment Error")

@router.post("/shopier/callback")
async def shopier_callback(data: dict, request: Request):
    """
    Handle POST callback from Shopier after a payment attempt.
    """
    try:
        logger.info(f"Received Shopier Callback: {data}")
        
        if shopier_service.verify_callback(data):
            status = data.get("status")
            order_id = data.get("platform_order_id")
            
            if status == "success":
                logger.info(f"✅ Payment SUCCESS for Order {order_id}")
                
                # Trigger real fulfillment via the engine
                from modules.ai_agency.fulfillment_engine import fulfillment_engine
                from backend.services.delivery_service import delivery_service

                amount_raw = data.get("total_order_value") or data.get("amount") or 0
                amount = delivery_service.parse_amount(amount_raw) or 0.0

                fulfillment_context = f"Shopier Order: {order_id}"
                base_url = str(request.base_url).rstrip("/")
                delivery_result = delivery_service.deliver_digital(data, base_url)
                if amount > 0 and delivery_result.status != "skipped":
                    fulfillment_engine.record_sale(
                        amount,
                        fulfillment_context,
                        metadata={
                            "order_id": delivery_result.order_id,
                            "sku": delivery_result.sku,
                            "currency": delivery_result.currency,
                            "channel": "shopier",
                        },
                    )
                try:
                    from backend.services.autonomax_api_service import autonomax_api_service

                    autonomax_api_service.emit_order_event(
                        order_id=order_id or "",
                        sku=delivery_result.sku,
                        amount=amount,
                        currency=delivery_result.currency or "TRY",
                        email=data.get("email") or data.get("buyer_email"),
                        status=status or "success",
                    )
                except Exception:
                    logger.warning("AutonomaX event dispatch skipped.")

                return {
                    "status": "success",
                    "message": "Payment verified and fulfillment triggered",
                    "delivery": delivery_result.__dict__,
                }
            else:
                logger.warning(f"❌ Payment FAILED for Order {order_id}")
                return {"status": "failed", "message": "Payment status not success"}
        else:
            logger.error("🛑 Shopier Callback Signature Verification FAILED")
            raise HTTPException(status_code=400, detail="Invalid signature")
            
    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing callback")
