import json
import os
import time
import requests


def _check(url: str, method: str = "GET", payload: dict | None = None) -> dict:
    start = time.time()
    try:
        if method == "POST":
            response = requests.post(url, json=payload, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        elapsed = round(time.time() - start, 3)
        return {
            "url": url,
            "status_code": response.status_code,
            "latency_s": elapsed,
        }
    except Exception as exc:
        elapsed = round(time.time() - start, 3)
        return {
            "url": url,
            "status_code": None,
            "latency_s": elapsed,
            "error": str(exc),
        }


def main() -> None:
    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    report = {
        "base_url": base_url,
        "checks": [],
    }

    report["checks"].append(_check(f"{base_url}/api/health"))
    report["checks"].append(
        _check(
            f"{base_url}/api/payment/shopier/pay?amount=1.00&currency=USD&order_id=HEALTH-001&product_name=Health+Check"
        )
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
