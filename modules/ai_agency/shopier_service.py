import logging
import hashlib
import hmac
import base64
import json
import random
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config.enhanced_settings import get_settings

logger = logging.getLogger(__name__)

class ShopierService:
    """
    Native Python implementation of Shopier Payment Gateway.
    Ported from official PHP library (shopier-master).
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.payment.shopier_api_key
        self.api_secret = self.settings.payment.shopier_api_secret
        self.access_token = self.settings.payment.shopier_personal_access_token
        self.payment_url = "https://www.shopier.com/ShowProduct/api_pay4.php"
        self.shopier_map_file = Path("docs/commerce/shopier_product_map.json")
        
        if self.access_token:
            logger.info("Shopier Networking: SECURE JWT TOKEN DETECTED. Real networking enabled.")

    def _resolve_credentials(self) -> tuple[Optional[str], Optional[str], bool]:
        if self.api_key and self.api_secret:
            return self.api_key, self.api_secret, False
        if self.access_token:
            return None, None, True
        return None, None, False

    def _resolve_shopier_url(self, order_id: str, product_name: str) -> Optional[str]:
        if not self.shopier_map_file.exists():
            return None
        try:
            data = json.loads(self.shopier_map_file.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Failed to load Shopier product map: %s", exc)
            return None
        sku = (order_id or "").split("-", 1)[0].strip()
        if sku:
            entry = data.get(sku, {})
            if entry.get("url"):
                return entry["url"]
        if product_name:
            for entry in data.values():
                if entry.get("title") == product_name and entry.get("url"):
                    return entry["url"]
        return None

    def _generate_signature(
        self,
        random_nr: str,
        order_id: str,
        amount: str,
        currency: int,
        api_secret: Optional[str] = None
    ) -> str:
        """
        Generates HMAC-SHA256 signature.
        Formula: base64(hmac_sha256(secret, random_nr + order_id + total + currency))
        """
        secret = api_secret or self.api_secret
        if not secret:
            return "MOCK_SIGNATURE"
            
        data = f"{random_nr}{order_id}{amount}{currency}"
        key = secret.encode('utf-8')
        msg = data.encode('utf-8')
        
        signature = hmac.new(key, msg, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    def generate_payment_link(self, amount: float, currency_code: str, order_id: str, product_name: str) -> str:
        """
        Generates the payment page HTML (Auto-submitting Form).
        Returns a data URI or a mock link if keys are missing.
        """
        api_key, api_secret, used_pat = self._resolve_credentials()

        if not api_key or not api_secret:
            if used_pat:
                shopier_url = self._resolve_shopier_url(order_id, product_name)
                if shopier_url:
                    return f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Redirecting to Shopier...</title></head>
                    <body>
                        <center><h2>Redirecting to Shopier Checkout...</h2></center>
                        <script>window.location.href = "{shopier_url}";</script>
                    </body>
                    </html>
                    """
                logger.warning("Shopier PAT detected but product URL missing. Set Shopier URLs or API key/secret.")
                return "<html><body><p>Shopier product URL missing. Please use a mapped Shopier product URL.</p></body></html>"
            logger.warning("Shopier keys not found. returning mock payment link.")
            return f"https://www.shopier.com/payment/mock?order_id={order_id}&amount={amount}"

        # Masked logging for verification
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
        logger.info(f"Generating Shopier Form for Order {order_id} (API Key: {masked_key})")

        # 0=TL, 1=USD, 2=EUR
        currency_val = 1 if currency_code.upper() == "USD" else 0
        if currency_code.upper() == "EUR": currency_val = 2
        
        random_nr = str(random.randint(100000, 999999))
        
        # Shopier expects strings for some values in hashing
        amount_str = str(amount)
        
        callback_url = f"{self.settings.backend_origin}/api/payment/shopier/callback"
        signature = self._generate_signature(random_nr, order_id, amount_str, currency_val, api_secret=api_secret)
        
        # Expanded params to include ALL mandatory fields from official PHP library
        params = {
            "API_key": api_key,
            "website_index": 1,
            "platform_order_id": order_id,
            "product_name": product_name,
            "product_type": 2, # 1=Standard, 2=Downloadable/Virtual (Better for AI services)
            "buyer_name": "Valued",
            "buyer_surname": "Customer",
            "buyer_email": "customer@example.com",
            "buyer_account_age": 0,
            "buyer_id_nr": "12345678901", # Mandatory placeholder
            "buyer_phone": "05555555555", # Mandatory placeholder
            "billing_address": "Digital Delivery", # Mandatory
            "billing_city": "Istanbul", # Mandatory
            "billing_country": "Turkey", # Mandatory
            "billing_postcode": "34000", # Mandatory
            "shipping_address": "Digital Delivery", # Mandatory
            "shipping_city": "Istanbul",
            "shipping_country": "Turkey",
            "shipping_postcode": "34000",
            "total_order_value": amount_str,
            "currency": currency_val,
            "platform": 0,
            "is_in_frame": 0,
            "current_language": 0, # 0=TR, 1=EN
            "modul_version": "1.0.4",
            "random_nr": random_nr,
            "signature": signature,
            "callback": callback_url,
        }
        
        form_inputs = "\n".join([f'<input type="hidden" name="{k}" value="{v}">' for k, v in params.items()])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Redirecting to Payment...</title></head>
        <body>
            <center><h2>Redirecting to Secure Shopier Payment...</h2></center>
            <form id="shopier_payment_form" method="post" action="{self.payment_url}">
                {form_inputs}
            </form>
            <script>document.getElementById("shopier_payment_form").submit();</script>
        </body>
        </html>
        """
        return html

    def verify_callback(self, data: Dict[str, Any]) -> bool:
        """
        Verifies the signature from Shopier callback.
        Formula: base64(hmac_sha256(token or secret, random_nr + platform_order_id))
        """
        res_signature = data.get("signature")
        
        # 🧪 DEBUG BYPASS: Enable manual signal triggering for testing
        if res_signature == "MOCK_MODE_BYPASS":
            allow_mock = os.getenv("SHOPIER_ALLOW_MOCK", "").lower() in ("1", "true", "yes")
            environment = str(getattr(self.settings, "environment", "")).lower()
            if environment != "production" or allow_mock:
                logger.info("🧪 [DEBUG] Shopier Callback Bypass Triggered: MOCK_MODE_BYPASS detected.")
                return True
            logger.warning("Shopier mock bypass blocked in production.")
            return False

        # Shopier Webhooks often use a dedicated Webhook Token for the HMAC key
        verification_key = (
            self.settings.payment.shopier_webhook_token
            or self.api_secret
            or self.access_token
        )
        
        if not verification_key:
            logger.warning("Shopier verification skipped: Verification Key (Token/Secret) missing.")
            return False
            
        res_random_nr = data.get("random_nr")
        res_order_id = data.get("platform_order_id")
        
        if not all([res_signature, res_random_nr, res_order_id]):
            return False
            
        # Standard Shopier Signature verification for callbacks
        expected_data = f"{res_random_nr}{res_order_id}"
        key = verification_key.encode('utf-8')
        msg = expected_data.encode('utf-8')
        
        signature = hmac.new(key, msg, hashlib.sha256).digest()
        expected_signature = base64.b64encode(signature).decode('utf-8')
        
        return res_signature == expected_signature

shopier_service = ShopierService()
