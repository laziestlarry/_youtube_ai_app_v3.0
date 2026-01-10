from typing import Dict, Any

class WebhookAdapter:
    """
    Transforms external webhook payloads into Growth Engine 'Ingest Request' format.
    Standardizes on:
    - external_id (str)
    - total_price (float)
    - currency (str)
    - status (str)
    - email (for PII hashing)
    """

    @staticmethod
    def transform_shopier(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapts Shopier webhook payload.
        Shopier typically sends: payment_id, status, price, currency, buyer_email...
        """
        # Note: Adjust field names based on actual Shopier docs/payload verification
        return {
            "data": {
                "id": payload.get("payment_id") or payload.get("id"),
                "email": payload.get("buyer_email") or payload.get("email"),
                "total_price": float(payload.get("price") or 0),
                "currency": payload.get("currency", "USD"),
                "status": "paid" if payload.get("status") == "success" else payload.get("status", "unknown"),
                "line_items": [
                    {"sku": "SHOPIER_DIGITAL", "qty": 1, "name": payload.get("product_name")}
                ]
            },
            "provenance": {
                "origin_name": "Shopier Webhook",
                "origin_type": "payment_gateway",
                "quality_score": 1.0
            }
        }

    @staticmethod
    def transform_shopify(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapts Shopify 'Order Created' webhook.
        """
        return {
            "data": {
                "id": str(payload.get("id")),
                "email": payload.get("email") or payload.get("contact_email"),
                "total_price": float(payload.get("total_price") or 0),
                "currency": payload.get("currency"),
                "status": "paid" if payload.get("financial_status") == "paid" else "pending",
                "line_items": [
                    {
                        "sku": item.get("sku"),
                        "qty": item.get("quantity"),
                        "name": item.get("name")
                    } for item in payload.get("line_items", [])
                ]
            },
            "provenance": {
                "origin_name": "Shopify Webhook",
                "origin_type": "ecommerce",
                "quality_score": 1.0
            }
        }

    @staticmethod
    def transform(source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if source == "shopier":
            return WebhookAdapter.transform_shopier(payload)
        elif source == "shopify":
            return WebhookAdapter.transform_shopify(payload)
        else:
            raise ValueError(f"Unknown webhook source: {source}")
