import os
import json
import logging
import time
from typing import Any, Dict, Optional

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
            except requests.RequestException as exc:
                last_exc = exc
                logger.error("Shopier API request failed: %s %s (%s)", method, url, exc)
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
        raise last_exc

    def list_products(self, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", "/products", params=params)

    def get_product(self, product_id: str) -> Any:
        return self._request("GET", f"/products/{product_id}")

    def create_product(self, payload: Dict[str, Any]) -> Any:
        return self._request("POST", "/products", payload=payload)

    def update_product(self, product_id: str, payload: Dict[str, Any]) -> Any:
        return self._request("PUT", f"/products/{product_id}", payload=payload)

    def delete_product(self, product_id: str) -> Any:
        return self._request("DELETE", f"/products/{product_id}")
