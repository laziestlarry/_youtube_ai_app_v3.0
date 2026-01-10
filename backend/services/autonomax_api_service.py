import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class AutonomaXApiService:
    """Lightweight client for the external AutonomaX API."""

    def __init__(self) -> None:
        self.base_url = os.getenv("AUTONOMAX_API_URL", "").rstrip("/")
        self.api_key = os.getenv("AUTONOMAX_API_KEY")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
    ) -> Optional[Dict[str, Any]]:
        if not self.base_url:
            logger.info("AUTONOMAX_API_URL not set; skipping AutonomaX call.")
            return None
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=self._headers(),
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            if response.text:
                return response.json()
            return {}
        except requests.RequestException as exc:
            logger.warning("AutonomaX API request failed: %s %s (%s)", method, url, exc)
            return None

    def emit_order_event(
        self,
        order_id: str,
        sku: Optional[str],
        amount: float,
        currency: str,
        email: Optional[str],
        status: str = "paid",
    ) -> None:
        payload = {
            "event": "order",
            "order_id": order_id,
            "sku": sku,
            "amount": amount,
            "currency": currency,
            "email": email,
            "status": status,
            "source": "shopier",
        }
        self._request("POST", "/growth/lifecycle", payload=payload)
        self._request("POST", "/ops/lifecycle/batch", payload={"events": [payload]})


autonomax_api_service = AutonomaXApiService()
