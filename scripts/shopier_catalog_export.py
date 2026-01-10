import argparse
import csv
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

import sys

sys.path.append(os.getcwd())

from backend.services.shopier_api_service import ShopierApiService


EXPORT_FIELDS = [
    "id",
    "title",
    "type",
    "price",
    "currency",
    "url",
    "dateCreated",
    "dateUpdated",
]


def _load_env_file(path: Optional[str]) -> None:
    if not path:
        return
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ[key.strip()] = value


def _extract_price(product: Dict[str, Any]) -> tuple[str, str]:
    price_data = product.get("priceData") or {}
    price = str(price_data.get("price", ""))
    currency = str(price_data.get("currency", ""))
    return price, currency


def _flatten_product(product: Dict[str, Any]) -> Dict[str, str]:
    price, currency = _extract_price(product)
    return {
        "id": str(product.get("id", "")),
        "title": str(product.get("title", "")),
        "type": str(product.get("type", "")),
        "price": price,
        "currency": currency,
        "url": str(product.get("url", "")),
        "dateCreated": str(product.get("dateCreated", "")),
        "dateUpdated": str(product.get("dateUpdated", "")),
    }


def export_products(
    output_path: Path,
    limit: int,
    max_pages: int,
) -> int:
    service = ShopierApiService()
    rows: List[Dict[str, str]] = []
    page = 1
    while True:
        if max_pages and page > max_pages:
            break
        params = {"limit": limit, "page": page}
        items = service.list_products(params=params) or []
        if not items:
            break
        rows.extend(_flatten_product(item) for item in items)
        if len(items) < limit:
            break
        page += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Shopier products to CSV using PAT.")
    parser.add_argument("--env-file", default=".env.shopier")
    parser.add_argument("--output", default="marketing_assets/shopier_products_export.csv")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-pages", type=int, default=0, help="0 means no limit")
    args = parser.parse_args()

    _load_env_file(args.env_file)
    count = export_products(Path(args.output), args.limit, args.max_pages)
    print(f"Exported {count} products to {args.output}")


if __name__ == "__main__":
    main()
