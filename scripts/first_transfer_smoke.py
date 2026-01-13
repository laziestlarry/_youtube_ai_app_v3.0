import os
import sys
import time
import json
import requests


def _read_log_tail(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = [line.strip() for line in handle.readlines() if line.strip()]
        return lines[-1] if lines else ""
    except FileNotFoundError:
        return ""


def main() -> int:
    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    sku = os.getenv("SMOKE_SKU", "ZEN-ART-BASE")
    title = os.getenv("SMOKE_TITLE", "Zen Sanat Baski Paketi")
    amount = float(os.getenv("SMOKE_AMOUNT", "19.99"))
    currency = os.getenv("SMOKE_CURRENCY", "USD")
    buyer_email = os.getenv("SMOKE_EMAIL", "test@example.com")

    order_id = f"{sku}-{int(time.time())}"
    params = {
        "amount": f"{amount:.2f}",
        "currency": currency,
        "order_id": order_id,
        "product_name": title,
    }

    print("== Step 1: Generate Shopier payment payload ==")
    pay_url = f"{base_url}/api/payment/shopier/pay"
    response = requests.get(pay_url, params=params, timeout=30)
    if response.status_code != 200:
        print(f"Payment endpoint failed: {response.status_code}")
        return 1
    if "mock" in response.text.lower() or "keys missing" in response.text.lower():
        print("WARNING: Shopier mock response detected. Set API keys for real flow.")
    else:
        print("Payment form generated.")

    print("== Step 2: Trigger callback (mock bypass) ==")
    callback_payload = {
        "signature": "MOCK_MODE_BYPASS",
        "platform_order_id": order_id,
        "status": "success",
        "total_order_value": f"{amount:.2f}",
        "currency": currency,
        "buyer_email": buyer_email,
        "product_name": title,
        "sku": sku,
        "random_nr": "123456",
    }

    callback_url = f"{base_url}/api/payment/shopier/callback"
    callback_response = requests.post(
        callback_url,
        json=callback_payload,
        timeout=30,
    )
    if callback_response.status_code != 200:
        print(f"Callback failed: {callback_response.status_code}")
        print(callback_response.text)
        return 1
    print("Callback accepted.")
    print(json.dumps(callback_response.json(), indent=2))

    print("== Step 3: Inspect delivery logs ==")
    data_dir = os.getenv("DATA_DIR", ".")
    orders_log = os.path.join(data_dir, "logs", "shopier_orders.jsonl")
    queue_log = os.path.join(data_dir, "logs", "delivery_queue.jsonl")

    orders_tail = _read_log_tail(orders_log)
    queue_tail = _read_log_tail(queue_log)

    if orders_tail:
        print("shopier_orders.jsonl tail:")
        print(orders_tail)
    else:
        print("shopier_orders.jsonl not found or empty.")

    if queue_tail:
        print("delivery_queue.jsonl tail:")
        print(queue_tail)
    else:
        print("delivery_queue.jsonl not found or empty.")

    print("Smoke test complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
