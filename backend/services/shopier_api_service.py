import os
import json
import logging
import time
from typing import Any, Dict, Optional, List

import requests

logger = logging.getLogger(__name__)


class ShopierApiService:
    """
    Shopier REST API client (PAT-only).
    Base URL: https://api.shopier.com/v1/
    """

    def __init__(self):
        self.base_url = os.getenv("SHOPIER_API_BASE_URL", "https://api.shopier.com/v1").rstrip("/")
        self.access_token = os.getenv("SHOPIER_PERSONAL_ACCESS_TOKEN")

        if not self.access_token:
            logger.warning("Shopier API access token missing. Set SHOPIER_PERSONAL_ACCESS_TOKEN.")

    def _headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise RuntimeError("SHOPIER_PERSONAL_ACCESS_TOKEN not configured")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_exc = None
        for attempt in range(3):
            try:
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=self._headers(),
                    params=params,
                    data=json.dumps(payload) if payload is not None else None,
                    timeout=30,
                )
                response.raise_for_status()
                if response.text:
                    return response.json()
                return None
            except requests.exceptions.HTTPError as e:
                logger.error(f"Shopier API error response: {e.response.text}")
                last_exc = e
                logger.error("Shopier API request failed: %s %s (%s)", method, url, e)
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
            except requests.RequestException as exc:
                last_exc = exc
                logger.error("Shopier API request failed: %s %s (%s)", method, url, exc)
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
        raise last_exc

    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product on Shopier.
        """
        # Map internal product schema to Shopier API schema
        payload = {
            "title": product_data.get("title"),
            "description": product_data.get("description"),
            "priceData": {
                "price": str(product_data.get("price")),
                "currency": product_data.get("currency", "USD"),
            },
            "type": product_data.get("type", "digital"),
            "stock": product_data.get("stock", 9999), 
            "category_id": product_data.get("category_id", 1),
            "is_active": product_data.get("is_active", True),
            "shippingPayer": product_data.get("shippingPayer", "sellerPays"),
            "media": product_data.get("media", [])
        }
        
        return self._request("POST", "/products", payload=payload)
    
    def get_orders(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get orders from Shopier.
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = self._request("GET", "/orders", params=params)
        return result.get("data", []) if isinstance(result, dict) else []
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Shopier webhook signature.
        """
        import hmac
        import hashlib
        
        webhook_secret = os.getenv("SHOPIER_WEBHOOK_TOKEN")
        if not webhook_secret:
            logger.warning("SHOPIER_WEBHOOK_TOKEN not configured")
            return False
        
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)

    def list_products(self, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", "/products", params=params)

    def get_product(self, product_id: str) -> Any:
        return self._request("GET", f"/products/{product_id}")

    def update_product(self, product_id: str, payload: Dict[str, Any]) -> Any:
        return self._request("PUT", f"/products/{product_id}", payload=payload)

    def delete_product(self, product_id: str) -> Any:
        return self._request("DELETE", f"/products/{product_id}")
