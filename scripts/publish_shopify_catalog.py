import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.append(os.getcwd())


def _load_catalog(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


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


def _resolve_image_url(image_url: Optional[str], backend_url: Optional[str]) -> Optional[str]:
    if not image_url:
        return None
    if image_url.startswith("static/") or image_url.startswith("/static/"):
        if not backend_url:
            return None
        return f"{backend_url.rstrip('/')}/{image_url.lstrip('/')}"
    return image_url


def _build_payload(
    product: Dict[str, Any],
    backend_url: Optional[str],
    status: str,
    vendor: Optional[str]
) -> Dict[str, Any]:
    price = product.get("price", {})
    amount = price.get("min") or price.get("max") or 0

    image_url = _resolve_image_url(product.get("image_url"), backend_url)
    images = [image_url] if image_url else []

    description = product.get("long_description") or product.get("short_description") or ""

    return {
        "title": product.get("title"),
        "description": description,
        "price": amount,
        "sku": product.get("sku"),
        "status": status,
        "images": images,
        "type": product.get("type"),
        "tags": product.get("tags") or [],
        "vendor": vendor,
    }


async def _publish_products(
    shopify_service,
    products: List[Dict[str, Any]],
    backend_url: Optional[str],
    status: str,
    vendor: Optional[str],
    limit: Optional[int],
    skus: Optional[List[str]],
    dry_run: bool,
    skip_existing: bool,
    update_existing: bool,
    update_images: bool
) -> None:
    created = 0
    for product in products:
        channels = product.get("channels", [])
        if "shopify" not in channels:
            continue
        if skus and product.get("sku") not in skus:
            continue
        payload = _build_payload(product, backend_url, status, vendor)
        title = payload.get("title") or "Untitled"
        existing = None
        if (skip_existing or update_existing) and payload.get("sku"):
            existing = await shopify_service.find_product_by_sku(payload["sku"])
        if skip_existing and existing:
            print(f"[SKIP] {title} ({payload.get('sku')}) already exists")
            continue
        if dry_run:
            action = "UPDATE" if existing and update_existing else "CREATE"
            print(f"[DRY-RUN:{action}] {title} ({payload.get('sku')})")
            created += 1
        else:
            if update_existing:
                result = await shopify_service.upsert_product(payload, update_images=update_images)
            else:
                result = await shopify_service.create_product(payload)
            if "errors" in result:
                print(f"[ERROR] {title}: {result['errors']}")
            else:
                created += 1
                online_url = result.get("onlineStoreUrl") or ""
                if existing and update_existing:
                    print(f"[UPDATED] {title} -> {online_url}")
                else:
                    print(f"[OK] {title} -> {online_url}")
        if limit and created >= limit:
            break

    print(f"Shopify publication complete. Items processed: {created}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish Shopify listings from the product catalog.")
    parser.add_argument("--catalog", default="docs/commerce/product_catalog.json")
    parser.add_argument("--backend-url", default=os.getenv("BACKEND_ORIGIN"))
    parser.add_argument("--env-file", default=".env", help="Env file with Shopify credentials")
    parser.add_argument("--status", default="ACTIVE")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sku", action="append", dest="skus")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-existing", action="store_true", help="Skip SKUs already present in Shopify")
    parser.add_argument("--update-existing", action="store_true", help="Update existing products by SKU instead of skipping")
    parser.add_argument("--update-images", action="store_true", help="Add listing images when updating existing products")
    args = parser.parse_args()

    _load_env_file(args.env_file)

    from backend.services.shopify_service import ShopifyService
    shopify_service = ShopifyService()
    if not shopify_service.admin_endpoint:
        print("Shopify Admin API not configured. Set SHOPIFY_ADMIN_TOKEN and SHOPIFY_SHOP_DOMAIN.")
        sys.exit(1)

    catalog = _load_catalog(args.catalog)
    products = catalog.get("products", [])
    vendor = catalog.get("brand")
    asyncio.run(
        _publish_products(
            shopify_service,
            products,
            args.backend_url,
            args.status,
            vendor,
            args.limit,
            args.skus,
            args.dry_run,
            args.skip_existing,
            args.update_existing,
            args.update_images
        )
    )


if __name__ == "__main__":
    main()
