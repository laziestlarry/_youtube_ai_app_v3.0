from datetime import datetime
import base64
import hashlib
import hmac
import json
import os
from fastapi import APIRouter, HTTPException, Query, Request, Depends, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.ai_agency.shopier_service import shopier_service
import logging

from backend.core.database import get_async_db
from backend.models.user import User
from backend.services.commerce_service import commerce_service
from backend.services.delivery_service import delivery_service, DeliveryResult

router = APIRouter()
logger = logging.getLogger(__name__)


def verify_shopier_osb(res: str, received_hash: str) -> bool:
    """
    Verify Shopier OSB (Otomatik Sipariş Bildirimi) signature.
    
    Formula: hash_hmac('sha256', res + username, key)
    Where:
    - res: base64-encoded JSON payload
    - username: Shopier API username (SHOPIER_OSB_USERNAME)
    - key: Shopier API key (SHOPIER_OSB_KEY)
    """
    username = os.getenv("SHOPIER_OSB_USERNAME") or os.getenv("SHOPIER_API_KEY", "")
    key = os.getenv("SHOPIER_OSB_KEY") or os.getenv("SHOPIER_API_SECRET", "")
    
    if not username or not key:
        logger.warning("Shopier OSB credentials not configured (SHOPIER_OSB_USERNAME, SHOPIER_OSB_KEY)")
        return False
    
    # Calculate expected hash: hash_hmac('sha256', res + username, key)
    data = (res + username).encode('utf-8')
    expected_hash = hmac.new(
        key.encode('utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hash, received_hash)


def parse_shopier_osb(res: str) -> dict:
    """
    Parse Shopier OSB payload from base64-encoded JSON.
    
    Returns dict with keys:
    - email: Customer email
    - orderid: Shopier order ID
    - currency: 0=TL, 1=USD, 2=EUR
    - price: Order total
    - buyername, buyersurname: Customer name
    - productcount: Number of products
    - productid: Primary product ID
    - productlist: List of products
    - chartdetails: Cart details
    - customernote: Customer note
    - istest: 0=live, 1=test
    """
    try:
        json_result = base64.b64decode(res).decode('utf-8')
        return json.loads(json_result)
    except Exception as e:
        logger.error(f"Failed to parse Shopier OSB payload: {e}")
        return {}


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

@router.post("/shopier/osb")
async def shopier_osb_callback(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    res: str = Form(None),
    hash: str = Form(None),
):
    """
    Handle Shopier OSB (Otomatik Sipariş Bildirimi) - Official callback format.
    
    Shopier sends POST with form data:
    - res: base64-encoded JSON with order details
    - hash: HMAC-SHA256 signature
    
    Must return "success" text to confirm receipt.
    """
    # Also try to get from request body if not in form
    if not res or not hash:
        try:
            form_data = await request.form()
            res = res or form_data.get("res")
            hash = hash or form_data.get("hash")
        except Exception:
            pass
    
    if not res or not hash:
        logger.error("Shopier OSB: Missing 'res' or 'hash' parameter")
        return PlainTextResponse("missing parameter", status_code=400)
    
    logger.info(f"Received Shopier OSB callback (res length: {len(res)}, hash: {hash[:16]}...)")
    
    # Verify signature
    if not verify_shopier_osb(res, hash):
        logger.error("Shopier OSB: Signature verification FAILED")
        return PlainTextResponse("invalid signature", status_code=400)
    
    # Parse payload
    order_data = parse_shopier_osb(res)
    if not order_data:
        logger.error("Shopier OSB: Failed to parse payload")
        return PlainTextResponse("invalid payload", status_code=400)
    
    logger.info(f"Shopier OSB parsed: orderid={order_data.get('orderid')}, email={order_data.get('email')}, price={order_data.get('price')}")
    
    # Extract order details
    order_id = str(order_data.get("orderid", ""))
    buyer_email = order_data.get("email", "")
    price = float(order_data.get("price", 0))
    currency_code = order_data.get("currency", 0)  # 0=TL, 1=USD, 2=EUR
    currency_map = {0: "TRY", 1: "USD", 2: "EUR"}
    currency = currency_map.get(currency_code, "TRY")
    buyer_name = f"{order_data.get('buyername', '')} {order_data.get('buyersurname', '')}".strip()
    product_id = order_data.get("productid", "")
    product_list = order_data.get("productlist", [])
    is_test = order_data.get("istest", 0) == 1
    
    if is_test:
        logger.info(f"Shopier OSB: TEST order {order_id} - processing but marking as test")
    
    try:
        # Process the order
        from modules.ai_agency.fulfillment_engine import fulfillment_engine
        
        base_url = os.getenv("BACKEND_ORIGIN") or str(request.base_url).rstrip("/")
        
        # Build delivery data in standard format
        delivery_data = {
            "order_id": order_id,
            "platform_order_id": order_id,
            "buyer_email": buyer_email,
            "email": buyer_email,
            "amount": price,
            "total_order_value": price,
            "currency": currency,
            "currency_code": currency,
            "product_id": product_id,
            "buyer_name": buyer_name,
            "status": "success",
        }
        
        # Try to resolve SKU from product list or product ID
        if product_list and len(product_list) > 0:
            first_product = product_list[0] if isinstance(product_list, list) else product_list
            if isinstance(first_product, dict):
                delivery_data["product_name"] = first_product.get("title") or first_product.get("name", "")
                delivery_data["sku"] = first_product.get("sku", "")
        
        # Trigger digital delivery
        delivery_result = delivery_service.deliver_digital(delivery_data, base_url)
        
        # Record revenue
        if price > 0 and delivery_result.status != "skipped":
            fulfillment_engine.record_sale(
                amount=price,
                source=f"Shopier OSB: {order_id}",
                metadata={
                    "order_id": order_id,
                    "sku": delivery_result.sku,
                    "currency": currency,
                    "channel": "shopier",
                    "kind": "test" if is_test else "real",
                    "buyer_email": buyer_email,
                    "buyer_name": buyer_name,
                },
            )
        
        # Record customer journey event
        user_id = None
        if buyer_email:
            result = await db.execute(select(User).where(User.email == buyer_email))
            user = result.scalars().first()
            if user:
                user_id = user.id
        
        try:
            await commerce_service.record_journey_event(
                db,
                user_id=user_id,
                stage="checkout_success",
                channel="shopier_osb",
                sku=delivery_result.sku,
                metadata={
                    "order_id": order_id,
                    "amount": price,
                    "currency": currency,
                    "email": buyer_email,
                    "is_test": is_test,
                },
            )
            
            if user_id and price > 0 and not is_test:
                await commerce_service.award_loyalty_points(
                    db,
                    user_id=user_id,
                    points=int(price),
                    reason="shopier_osb_purchase",
                    reference=order_id,
                )
        except Exception as e:
            logger.warning(f"Commerce journey/loyalty update skipped: {e}")
        
        logger.info(f"✅ Shopier OSB processed: order={order_id}, delivery={delivery_result.status}")
        
        # Return "success" to confirm receipt (required by Shopier)
        return PlainTextResponse("success")
        
    except Exception as e:
        logger.error(f"Shopier OSB processing error: {e}", exc_info=True)
        # Still return success to prevent Shopier from retrying indefinitely
        # But log the error for investigation
        return PlainTextResponse("success")


@router.post("/shopier/callback")
async def shopier_callback(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Handle POST callback from Shopier after a payment attempt.
    Supports both legacy JSON format and OSB form format.
    """
    # Check if this is OSB format (form data with res/hash)
    content_type = request.headers.get("content-type", "")
    
    if "form" in content_type.lower():
        try:
            form_data = await request.form()
            if "res" in form_data and "hash" in form_data:
                # Redirect to OSB handler
                return await shopier_osb_callback(
                    request=request,
                    db=db,
                    res=form_data.get("res"),
                    hash=form_data.get("hash"),
                )
        except Exception:
            pass
    
    # Legacy JSON format
    try:
        data = await request.json()
    except Exception:
        logger.error("Shopier callback: Failed to parse request body")
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    try:
        logger.info(f"Received Shopier Callback (legacy): {data}")
        
        if shopier_service.verify_callback(data):
            status = data.get("status")
            order_id = data.get("platform_order_id") or data.get("order_id")
            
            if status == "success":
                logger.info(f"✅ Payment SUCCESS for Order {order_id}")
                
                # Trigger real fulfillment via the engine
                from modules.ai_agency.fulfillment_engine import fulfillment_engine

                amount_raw = data.get("total_order_value") or data.get("amount") or 0
                amount = delivery_service.parse_amount(amount_raw) or 0.0
                currency = data.get("currency") or data.get("currency_code")
                buyer_email = data.get("email") or data.get("buyer_email")

                fulfillment_context = f"Shopier Order: {order_id}"
                base_url = str(request.base_url).rstrip("/")
                delivery_result = None

                commerce_order = None
                if order_id:
                    commerce_order = await commerce_service.get_order_by_order_id(db, order_id)

                if commerce_order:
                    if buyer_email and not commerce_order.customer_email:
                        commerce_order.customer_email = buyer_email
                        await db.commit()
                    offer = None
                    asset = None
                    if commerce_order.offer_id:
                        offer = await commerce_service.get_offer(db, commerce_order.offer_id)
                        if offer and offer.asset_id:
                            asset = await commerce_service.get_asset(db, offer.asset_id)

                    await commerce_service.mark_order_paid(
                        db,
                        commerce_order,
                        amount if amount > 0 else commerce_order.amount,
                        currency,
                    )
                    if amount <= 0 and commerce_order.amount:
                        amount = commerce_order.amount

                    if asset:
                        delivery = await commerce_service.create_delivery(db, commerce_order, asset, base_url)
                        email_target = commerce_order.customer_email or buyer_email
                        if email_target:
                            title = offer.title if offer else "Download Ready"
                            subject, body = delivery_service.build_zen_art_delivery_message(
                                title=title,
                                download_url=delivery.download_url,
                                ttl_hours=commerce_service.delivery_ttl_hours(),
                                order_id=commerce_order.order_id,
                            )
                            delivery_service.send_email(email_target, subject, body)
                            delivery.status = "sent"
                            delivery.delivered_at = datetime.utcnow()
                            commerce_order.status = "delivered"
                            await db.commit()

                        delivery_result = DeliveryResult(
                            status=delivery.status,
                            message="Delivery prepared",
                            download_url=delivery.download_url,
                            order_id=commerce_order.order_id,
                            sku=offer.sku if offer else None,
                            amount=commerce_order.amount,
                            currency=commerce_order.currency,
                        )

                if not delivery_result:
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
                user_id = None
                if buyer_email:
                    result = await db.execute(select(User).where(User.email == buyer_email))
                    user = result.scalars().first()
                    if user:
                        user_id = user.id
                try:
                    await commerce_service.record_journey_event(
                        db,
                        user_id=user_id,
                        stage="checkout_success",
                        channel="shopier",
                        sku=delivery_result.sku,
                        metadata={
                            "order_id": order_id,
                            "amount": amount,
                            "currency": delivery_result.currency,
                            "email": buyer_email,
                        },
                    )
                    if user_id and amount > 0:
                        await commerce_service.award_loyalty_points(
                            db,
                            user_id=user_id,
                            points=int(amount),
                            reason="shopier_purchase",
                            reference=order_id,
                        )
                except Exception:
                    logger.warning("Commerce journey/loyalty update skipped.")
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
