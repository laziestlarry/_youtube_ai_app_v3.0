import json
import os
import ssl
import sys
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SHOPIER_MAP = ROOT / "docs/commerce/shopier_product_map.json"


TOP_SKUS = [
    "FIVERR-KIT-01",
    "ZEN-ART-BASE",
    "AX-SAAS-01",
    "YT-AUTO-01",
    "BOP-SAAS-01",
]


def _check_url(url: str, timeout: int = 15) -> int:
    req = Request(url, headers={"User-Agent": "chimera-check/1.0"})
    context = None
    if os.getenv("CHIMERA_SKIP_SSL_VERIFY") == "1":
        context = ssl._create_unverified_context()  # noqa: SLF001
    with urlopen(req, timeout=timeout, context=context) as resp:
        return resp.status


def main() -> int:
    if not SHOPIER_MAP.exists():
        print(f"Missing map: {SHOPIER_MAP}")
        return 1

    shopier_map = json.loads(SHOPIER_MAP.read_text(encoding="utf-8"))
    failures = 0

    storefront = os.getenv(
        "STOREFRONT_URL",
        "https://youtube-ai-backend-lenljbhrqq-uc.a.run.app/",
    )
    try:
        status = _check_url(storefront)
        print(f"[OK] Storefront {storefront} -> {status}")
    except Exception as exc:
        print(f"[FAIL] Storefront {storefront} -> {exc}")
        failures += 1

    for sku in TOP_SKUS:
        url = shopier_map.get(sku, {}).get("url")
        if not url:
            print(f"[FAIL] Missing Shopier URL for {sku}")
            failures += 1
            continue
        try:
            status = _check_url(url)
            if status >= 400:
                print(f"[FAIL] {sku} {url} -> {status}")
                failures += 1
            else:
                print(f"[OK] {sku} {url} -> {status}")
        except Exception as exc:
            print(f"[FAIL] {sku} {url} -> {exc}")
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
