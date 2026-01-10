import csv
import json
import os
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl


ROOT = Path(__file__).resolve().parents[1]
SHOPIER_MAP = ROOT / "docs/commerce/shopier_product_map.json"
CATALOG = ROOT / "docs/commerce/product_catalog.json"
OUT_FILE = ROOT / "marketing_assets/utm_links.csv"
ENV_SHOPIFY = ROOT / ".env2"


def _append_params(url: str, params: dict) -> str:
    parsed = urlparse(url)
    existing = dict(parse_qsl(parsed.query))
    existing.update(params)
    new_query = urlencode(existing)
    return urlunparse(parsed._replace(query=new_query))


def _load_shopify_domain() -> str:
    if not ENV_SHOPIFY.exists():
        return ""
    for line in ENV_SHOPIFY.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("SHOPIFY_SHOP_DOMAIN="):
            return line.split("=", 1)[1].strip()
    return ""


def main() -> None:
    shopier_map = json.loads(SHOPIER_MAP.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8")).get("products", [])
    catalog_by_sku = {p.get("sku"): p for p in catalog}

    shopify_domain = _load_shopify_domain()
    rows = []

    for sku, payload in shopier_map.items():
        title = payload.get("title", sku)
        url = payload.get("url")
        if not url:
            continue
        utm = {
            "utm_source": "chimera",
            "utm_medium": "shopier",
            "utm_campaign": "week1_launch",
        }
        rows.append(
            {
                "channel": "shopier",
                "sku": sku,
                "title": title,
                "url": _append_params(url, utm),
            }
        )

    if shopify_domain:
        for sku, product in catalog_by_sku.items():
            if "shopify" not in (product.get("channels") or []):
                continue
            title = product.get("title", sku)
            base_url = f"https://{shopify_domain}"
            utm = {
                "utm_source": "chimera",
                "utm_medium": "shopify",
                "utm_campaign": "week1_launch",
            }
            rows.append(
                {
                    "channel": "shopify",
                    "sku": sku,
                    "title": title,
                    "url": _append_params(base_url, utm),
                }
            )

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["channel", "sku", "title", "url"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"UTM links written to {OUT_FILE}")


if __name__ == "__main__":
    main()
