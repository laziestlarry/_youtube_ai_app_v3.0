import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import sys

sys.path.append(os.getcwd())

from backend.services.shopier_api_service import ShopierApiService


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


def _load_catalog(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_map(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_map(path: Path, data: Dict[str, Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def _load_price_map(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_media_url(image_url: str, base_url: Optional[str]) -> Optional[str]:
    if not image_url:
        return None
    if image_url.startswith("http://") or image_url.startswith("https://"):
        return image_url
    if not base_url:
        return None
    return f"{base_url.rstrip('/')}/{image_url.lstrip('/')}"


def _resolve_primary_image(product: Dict[str, Any], base_url: Optional[str]) -> Optional[str]:
    image_url = product.get("image_url") or ""
    resolved = _resolve_media_url(image_url, base_url)
    if resolved:
        return resolved
    fallback = os.getenv("SHOPIER_FALLBACK_IMAGE_URL", "")
    return _resolve_media_url(fallback, base_url)


def _shopier_product_type(product_type: str) -> str:
    if product_type in {"physical"}:
        return "physical"
    return "digital"


def _apply_psych_rounding(amount: Any, enabled: bool) -> Any:
    if not enabled:
        return amount
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return amount
    if value < 1000:
        return amount
    thousands = int(value) // 1000
    remainder = int(round(value)) % 1000
    candidate = int(round(remainder / 100.0)) * 100
    if candidate < 500:
        candidate = 500
    elif candidate > 900:
        candidate = 900
    return thousands * 1000 + candidate - 1


def _build_payload(
    product: Dict[str, Any],
    base_url: Optional[str],
    price_override: Optional[Dict[str, Any]],
    currency_override: Optional[str],
    fx_rate: Optional[float],
    psych_round: bool,
    default_stock: int,
) -> Dict[str, Any]:
    price_info = product.get("price", {}) or {}
    amount = price_info.get("min") or price_info.get("max") or 0
    currency = price_info.get("currency", "USD")
    if price_override:
        if price_override.get("price") is not None:
            amount = price_override.get("price")
        if price_override.get("currency"):
            currency = price_override.get("currency")
    if currency_override:
        if currency_override != currency and fx_rate:
            amount = round(float(amount) * fx_rate, 2)
        currency = currency_override
    amount = _apply_psych_rounding(amount, psych_round and str(currency).upper() == "TRY")
    product_type = _shopier_product_type(str(product.get("type", "digital")).lower())
    stock_quantity = product.get("stock_quantity")
    if stock_quantity is None:
        stock_quantity = product.get("stock")
    if stock_quantity is None and product_type == "digital":
        stock_quantity = default_stock

    media_url = _resolve_primary_image(product, base_url)
    media = []
    if media_url:
        media.append(
            {
                "type": "image",
                "url": media_url,
                "placement": 1,
            }
        )

    payload = {
        "title": product.get("title", ""),
        "description": product.get("long_description") or product.get("short_description") or "",
        "type": product_type,
        "media": media,
        "priceData": {
            "currency": currency,
            "price": str(amount),
            "shippingPrice": "0",
        },
        "shippingPayer": "sellerPays",
        "dispatchDuration": 1,
        "customListing": False,
    }
    if stock_quantity is not None:
        payload["stockQuantity"] = int(stock_quantity)

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Import product catalog to Shopier (PAT-only).")
    parser.add_argument("--env-file", default=".env.shopier")
    parser.add_argument("--catalog", default="docs/commerce/product_catalog.json")
    parser.add_argument("--map-file", default="docs/commerce/shopier_product_map.json")
    parser.add_argument("--price-map", default="docs/commerce/shopier_price_overrides.json")
    parser.add_argument("--media-base-url", default=os.getenv("SHOPIER_MEDIA_BASE_URL") or os.getenv("BACKEND_ORIGIN"))
    parser.add_argument("--currency", default=None, help="Override currency (e.g., TRY)")
    parser.add_argument("--fx-rate", type=float, default=None, help="Multiply price when overriding currency")
    parser.add_argument(
        "--no-psych-round",
        action="store_true",
        help="Disable TRY psychological rounding (default: enabled for TRY >= 1000).",
    )
    parser.add_argument(
        "--default-stock",
        type=int,
        default=9999,
        help="Default stock quantity for digital products when stock is not specified.",
    )
    parser.add_argument("--update-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sku", action="append", dest="skus")
    args = parser.parse_args()

    _load_env_file(args.env_file)

    catalog = _load_catalog(Path(args.catalog))
    mapping = _load_map(Path(args.map_file))
    price_map = _load_price_map(Path(args.price_map)) if args.price_map else {}
    service = ShopierApiService()

    processed = 0
    for product in catalog.get("products", []):
        if "shopier" not in (product.get("channels") or []):
            continue
        sku = product.get("sku")
        if args.skus and sku not in args.skus:
            continue

        price_override = price_map.get(sku or "")
        payload = _build_payload(
            product,
            args.media_base_url,
            price_override,
            args.currency,
            args.fx_rate,
            not args.no_psych_round,
            args.default_stock,
        )
        if not payload.get("media"):
            print(f"[SKIP] {sku} missing media URL. Set image_url or SHOPIER_FALLBACK_IMAGE_URL.")
            continue
        if args.currency and args.currency != (product.get("price", {}) or {}).get("currency"):
            if not args.fx_rate:
                print(f"[WARN] {sku} currency overridden without fx-rate; price left as-is.")
        existing = mapping.get(sku or "")

        if args.dry_run:
            action = "update" if existing and args.update_existing else "create"
            print(f"[DRY-RUN:{action}] {sku} -> {payload.get('title')}")
            processed += 1
            if args.limit and processed >= args.limit:
                break
            continue

        if existing and args.update_existing:
            result = service.update_product(existing["id"], payload)
        else:
            result = service.create_product(payload)

        if not result:
            print(f"[ERROR] {sku} returned empty response")
            continue

        mapping[sku] = {
            "id": result.get("id"),
            "url": result.get("url"),
            "title": result.get("title"),
        }
        print(f"[OK] {sku} -> {result.get('url')}")
        processed += 1
        if args.limit and processed >= args.limit:
            break

    _save_map(Path(args.map_file), mapping)
    print(f"Processed {processed} products. Map updated at {args.map_file}.")


if __name__ == "__main__":
    main()
