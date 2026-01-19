import json
import logging
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, Optional, List


logger = logging.getLogger(__name__)


CATALOG_FILE = Path("docs/commerce/product_catalog.json")
SHOPIER_MAP_FILE = Path("docs/commerce/shopier_product_map.json")
DELIVERY_MAP_FILE = Path("docs/commerce/digital_delivery_map.json")

# Data Persistence (Cloud Run GCS Volume Support)
# Use DATA_DIR env var to point to mounted volume (e.g. /app/persistent)
DATA_DIR = Path(os.getenv("DATA_DIR", "."))
DELIVERY_QUEUE_FILE = DATA_DIR / "logs/delivery_queue.jsonl"
ORDER_LOG_FILE = DATA_DIR / "logs/shopier_orders.jsonl"


@dataclass
class DeliveryResult:
    status: str
    message: str
    download_url: Optional[str] = None
    queued: bool = False
    order_id: Optional[str] = None
    sku: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None


class DeliveryService:
    def __init__(self) -> None:
        self._title_to_sku = self._load_title_map()
        self._sku_to_delivery = self._load_delivery_map()

    def _load_title_map(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        if CATALOG_FILE.exists():
            try:
                data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
                for product in data.get("products", []):
                    title = str(product.get("title") or "").strip()
                    sku = str(product.get("sku") or "").strip()
                    if title and sku:
                        mapping[title.lower()] = sku
            except Exception as exc:
                logger.warning("Failed to load product catalog: %s", exc)
        if SHOPIER_MAP_FILE.exists():
            try:
                data = json.loads(SHOPIER_MAP_FILE.read_text(encoding="utf-8"))
                for sku, info in data.items():
                    title = str(info.get("title") or "").strip()
                    if title:
                        mapping[title.lower()] = sku
            except Exception as exc:
                logger.warning("Failed to load Shopier map: %s", exc)
        return mapping

    def _load_delivery_map(self) -> Dict[str, Dict[str, str]]:
        if not DELIVERY_MAP_FILE.exists():
            return {}
        try:
            return json.loads(DELIVERY_MAP_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Failed to load delivery map: %s", exc)
            return {}

    @staticmethod
    def _get_field(data: Dict[str, Any], keys: list[str]) -> Optional[str]:
        lower = {str(k).lower(): v for k, v in data.items()}
        for key in keys:
            value = lower.get(key.lower())
            if value is not None:
                return str(value)
        return None

    def _resolve_sku(self, data: Dict[str, Any]) -> Optional[str]:
        sku = self._get_field(data, ["sku", "product_sku"])
        if sku:
            return sku
        title = self._get_field(data, ["product_name", "product", "title", "product_title"])
        if not title:
            return None
        return self._title_to_sku.get(title.lower())

    def _resolve_delivery_file(self, sku: Optional[str]) -> Optional[Dict[str, str]]:
        if not sku:
            return None
        return self._sku_to_delivery.get(sku)

    @staticmethod
    def parse_amount(value: Any) -> Optional[float]:
        if value is None:
            return None
        raw = str(value).strip().replace(" ", "")
        if not raw:
            return None
        if "," in raw and "." in raw:
            if raw.rfind(",") > raw.rfind("."):
                raw = raw.replace(".", "").replace(",", ".")
            else:
                raw = raw.replace(",", "")
        elif "," in raw:
            tail = raw.split(",")[-1]
            if len(tail) == 2:
                raw = raw.replace(",", ".")
            else:
                raw = raw.replace(",", "")
        try:
            return float(raw)
        except ValueError:
            return None

    def _build_download_url(self, base_url: str, file_path: str) -> str:
        base = base_url.rstrip("/")
        if file_path.startswith("/"):
            return f"{base}{file_path}"
        return f"{base}/{file_path}"

    def _send_email(self, to_email: str, subject: str, body: str) -> None:
        enabled = os.getenv("EMAIL_ENABLED") or os.getenv("NOTIFICATIONS_EMAIL_ENABLED") or "false"
        enabled = enabled.lower() in ("1", "true", "yes")
        if not enabled:
            logger.info("Email delivery NOT ENABLED (Logging content for dev):")
            logger.info("TO: %s", to_email)
            logger.info("SUBJECT: %s", subject)
            logger.info("BODY: %s", body)
            return

        smtp_host = os.getenv("SMTP_HOST") or os.getenv("NOTIFICATIONS_SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT") or os.getenv("NOTIFICATIONS_SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USERNAME") or os.getenv("NOTIFICATIONS_SMTP_USERNAME")
        smtp_pass = (
            os.getenv("SMTP_PASSWORD")
            or os.getenv("SMTP_APP_PASSWORD")
            or os.getenv("NOTIFICATIONS_SMTP_PASSWORD")
        )
        if not smtp_host or not smtp_user or not smtp_pass:
            raise RuntimeError("SMTP settings incomplete")

        sender = os.getenv("DELIVERY_FROM_EMAIL") or os.getenv("NOTIFICATIONS_FROM_EMAIL") or smtp_user
        message = EmailMessage()
        message["From"] = sender
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(message)

    def _queue_delivery(self, payload: Dict[str, Any]) -> None:
        DELIVERY_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DELIVERY_QUEUE_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True))
            handle.write("\n")

    def _log_order(self, payload: Dict[str, Any]) -> None:
        ORDER_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with ORDER_LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True))
            handle.write("\n")

    def _order_already_processed(self, order_id: Optional[str]) -> bool:
        if not order_id or not ORDER_LOG_FILE.exists():
            return False
        try:
            for line in ORDER_LOG_FILE.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("order_id") == order_id and data.get("status") == "delivered":
                    return True
        except Exception:
            return False
        return False

    @staticmethod
    def _mask_email(email: Optional[str]) -> Optional[str]:
        if not email or "@" not in email:
            return email
        name, domain = email.split("@", 1)
        prefix = name[:2] if len(name) > 2 else name[:1]
        return f"{prefix}***@{domain}"

    @staticmethod
    def _truthy(value: Optional[str]) -> bool:
        return str(value or "").strip().lower() in ("1", "true", "yes", "on")

    def _queue_payload(self, payload: Dict[str, Any], data: Dict[str, Any], buyer_email: Optional[str]) -> Dict[str, Any]:
        if self._truthy(os.getenv("DELIVERY_QUEUE_STORE_PAYLOAD")):
            payload["raw"] = data
        if self._truthy(os.getenv("DELIVERY_QUEUE_STORE_EMAIL")) and buyer_email:
            payload["buyer_email"] = buyer_email
        return payload

    def deliver_digital(self, data: Dict[str, Any], base_url: str, allow_queue: bool = True) -> DeliveryResult:
        order_id = self._get_field(data, ["platform_order_id", "order_id", "order"])
        if self._order_already_processed(order_id):
            return DeliveryResult(
                status="skipped",
                message="Order already delivered",
                queued=False,
                order_id=order_id,
            )

        amount_raw = self._get_field(data, ["total_order_value", "amount"])
        currency_raw = self._get_field(data, ["currency", "currency_code"])
        amount_value = self.parse_amount(amount_raw)
        buyer_email = self._get_field(data, ["buyer_email", "email", "customer_email"])

        sku = self._resolve_sku(data)
        delivery = self._resolve_delivery_file(sku)
        if not delivery:
            payload = {
                "status": "missing_delivery",
                "order_id": order_id,
                "sku": sku,
                "received_at": datetime.utcnow().isoformat(),
            }
            payload = self._queue_payload(payload, data, buyer_email)
            if allow_queue:
                self._queue_delivery(payload)
            self._log_order(payload)
            return DeliveryResult(
                status="queued",
                message="Delivery asset missing",
                queued=True,
                order_id=order_id,
                sku=sku,
                amount=amount_value,
                currency=currency_raw,
            )

        download_url = self._build_download_url(base_url, delivery["file"])
        
        # --- Over-Expectation (Surprise & Delight) Logic ---
        subject = f"🚀 [VIP DELIVERY] Your AutonomaX Ignition Access: {delivery.get('label') or sku}"
        
        # Check for Ignition Bonus
        ignition_bonus = self._sku_to_delivery.get("IGNITION-BONUS-01")
        bonus_link = ""
        if ignition_bonus:
            bonus_url = self._build_download_url(base_url, ignition_bonus["file"])
            bonus_link = f"\n🎁 IGNITION BONUS: We've included the 'Autonomy Success Blueprint' as a free gift!\nDownload here: {bonus_url}\n"

        body = (
            "Merhaba,\n\n"
            "Thank you for being part of the AutonomaX Ignition event. Your digital assets are ready for immediate deployment.\n\n"
            f"📥 PRIMARY ACCESS: {download_url}\n"
            f"{bonus_link}"
            "\n"
            "--- PREMIUM SUPPORT ---\n"
            "As an early adopter, you have priority support. If you have any questions, simply reply to this email.\n\n"
            "Welcome to the Era of Autonomous Growth.\n"
            "The AutonomaX Team"
        )

        payload = {
            "status": "delivered",
            "order_id": order_id,
            "sku": sku,
            "download_url": download_url,
            "delivered_at": datetime.utcnow().isoformat(),
            "email": self._mask_email(buyer_email),
            "amount": amount_value,
            "currency": currency_raw,
        }

        try:
            if buyer_email:
                self._send_email(buyer_email, subject, body)
                self._log_order(payload)
                return DeliveryResult(
                    status="delivered",
                    message="Email sent",
                    download_url=download_url,
                    order_id=order_id,
                    sku=sku,
                    amount=amount_value,
                    currency=currency_raw,
                )
        except Exception as exc:
            payload["status"] = "queued"
            payload["error"] = str(exc)
            payload = self._queue_payload(payload, data, buyer_email)
            if allow_queue:
                self._queue_delivery(payload)
            self._log_order(payload)
            return DeliveryResult(
                status="queued",
                message="Email queued",
                download_url=download_url,
                queued=True,
                order_id=order_id,
                sku=sku,
                amount=amount_value,
                currency=currency_raw,
            )

        payload = self._queue_payload(payload, data, buyer_email)
        if allow_queue:
            self._queue_delivery(payload)
        self._log_order(payload)
        return DeliveryResult(
            status="queued",
            message="No email provided",
            download_url=download_url,
            queued=True,
            order_id=order_id,
            sku=sku,
            amount=amount_value,
            currency=currency_raw,
        )

    def retry_queued_deliveries(self, base_url: Optional[str] = None, max_items: int = 50) -> Dict[str, int]:
        if not DELIVERY_QUEUE_FILE.exists():
            return {"attempted": 0, "delivered": 0, "remaining": 0}

        base_url = base_url or os.getenv("BACKEND_ORIGIN") or ""
        if not base_url:
            return {"attempted": 0, "delivered": 0, "remaining": 0, "error": "BASE_URL missing"}

        attempted = 0
        delivered = 0
        remaining: List[Dict[str, Any]] = []
        now = datetime.utcnow().isoformat()

        for line in DELIVERY_QUEUE_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue

            if attempted >= max_items:
                remaining.append(entry)
                continue

            payload = entry.get("raw")
            buyer_email = entry.get("buyer_email")
            sku = entry.get("sku")
            order_id = entry.get("order_id")

            if payload:
                attempted += 1
                result = self.deliver_digital(payload, base_url, allow_queue=False)
                if result.status == "delivered":
                    delivered += 1
                    continue
                entry["status"] = result.status
                entry["last_attempt_at"] = now
                entry["attempts"] = int(entry.get("attempts", 0)) + 1
                remaining.append(entry)
                continue

            if buyer_email and sku:
                attempted += 1
                payload = {"sku": sku, "buyer_email": buyer_email, "order_id": order_id}
                result = self.deliver_digital(payload, base_url, allow_queue=False)
                if result.status == "delivered":
                    delivered += 1
                    continue
                entry["status"] = result.status
                entry["last_attempt_at"] = now
                entry["attempts"] = int(entry.get("attempts", 0)) + 1

            remaining.append(entry)

        DELIVERY_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DELIVERY_QUEUE_FILE.open("w", encoding="utf-8") as handle:
            for entry in remaining:
                handle.write(json.dumps(entry, ensure_ascii=True))
                handle.write("\n")

        return {"attempted": attempted, "delivered": delivered, "remaining": len(remaining)}


delivery_service = DeliveryService()
