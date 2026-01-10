import argparse
import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

SHOPIFY_FIELDS = [
    "Handle",
    "Title",
    "Body (HTML)",
    "Vendor",
    "Type",
    "Tags",
    "Published",
    "Variant Price",
    "Image Src",
]

ETSY_FIELDS = [
    "Title",
    "Description",
    "Price",
    "Tags",
    "Materials",
    "Image1",
]

FIVERR_FIELDS = [
    "Title",
    "Description",
    "Search Tags",
    "Price Basic",
    "Price Standard",
    "Price Premium",
    "Delivery Basic",
    "Delivery Standard",
    "Delivery Premium",
]

AMAZON_FIELDS = [
    "sku",
    "item_name",
    "product_description",
    "standard_price",
    "brand_name",
    "main_image_url",
    "keywords",
    "product_type",
]

GUMROAD_FIELDS = [
    "Name",
    "Description",
    "Price",
    "Tags",
    "Cover Image",
    "Product Type",
]

SHOPIER_FIELDS = [
    "SKU",
    "Title",
    "Description",
    "Price",
    "Currency",
    "Image",
    "Checkout URL",
]


def slugify(value: str) -> str:
    return "-".join(
        "".join(ch.lower() if ch.isalnum() else " " for ch in value).split()
    )


def load_catalog(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_optional_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def apply_psych_rounding(amount: Any, enabled: bool) -> Any:
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


def resolve_primary_image(product: Dict[str, Any], backend_url: Optional[str] = None) -> str:
    sku = product.get("sku")
    if sku:
        candidates = [
            Path("static/assets/listings") / sku / "listing.png",
            Path("marketing_assets") / sku / "listing.png",
        ]
        for path in candidates:
            if path.exists():
                if backend_url:
                    return f"{backend_url.rstrip('/')}/{path.as_posix()}"
                return str(path)
    image = product.get("image_url") or product.get("primary_image")
    if image:
        if backend_url and (str(image).startswith("static/") or str(image).startswith("/static/")):
            return f"{backend_url.rstrip('/')}/{str(image).lstrip('/')}"
        return str(image)
    assets = product.get("assets") or []
    if assets:
        asset = str(assets[0])
        if backend_url and (asset.startswith("static/") or asset.startswith("/static/")):
            return f"{backend_url.rstrip('/')}/{asset.lstrip('/')}"
        return asset
    return ""


def build_shopify_rows(catalog: Dict[str, Any], backend_url: Optional[str]) -> List[Dict[str, str]]:
    vendor = catalog.get("brand", "AutonomaX")
    rows = []
    for product in catalog.get("products", []):
        price = product.get("price", {}).get("min", "")
        tags = product.get("tags", [])
        rows.append(
            {
                "Handle": slugify(product.get("sku", product.get("title", "product"))),
                "Title": product.get("title", ""),
                "Body (HTML)": f"<p>{product.get('long_description', '')}</p>",
                "Vendor": vendor,
                "Type": product.get("type", ""),
                "Tags": ", ".join(tags),
                "Published": "TRUE",
                "Variant Price": str(price),
                "Image Src": resolve_primary_image(product, backend_url),
            }
        )
    return rows


def build_etsy_rows(catalog: Dict[str, Any], backend_url: Optional[str]) -> List[Dict[str, str]]:
    rows = []
    for product in catalog.get("products", []):
        price = product.get("price", {}).get("min", "")
        tags = product.get("tags", [])
        rows.append(
            {
                "Title": product.get("title", ""),
                "Description": product.get("long_description", ""),
                "Price": str(price),
                "Tags": ", ".join(tags[:13]),
                "Materials": "digital download" if product.get("type") == "digital" else "service",
                "Image1": resolve_primary_image(product, backend_url),
            }
        )
    return rows


def build_fiverr_rows(catalog: Dict[str, Any]) -> List[Dict[str, str]]:
    rows = []
    for product in catalog.get("products", []):
        tags = product.get("tags", [])
        price = product.get("price", {})
        rows.append(
            {
                "Title": product.get("title", ""),
                "Description": product.get("short_description", ""),
                "Search Tags": ", ".join(tags[:5]),
                "Price Basic": str(price.get("min", "")),
                "Price Standard": str(price.get("max", "")),
                "Price Premium": str(price.get("max", "")),
                "Delivery Basic": "7 days",
                "Delivery Standard": "10 days",
                "Delivery Premium": "14 days",
            }
        )
    return rows


def build_amazon_rows(catalog: Dict[str, Any], backend_url: Optional[str]) -> List[Dict[str, str]]:
    brand = catalog.get("brand", "AutonomaX")
    rows = []
    for product in catalog.get("products", []):
        price = product.get("price", {}).get("min", "")
        tags = product.get("tags", [])
        rows.append(
            {
                "sku": product.get("sku", ""),
                "item_name": product.get("title", ""),
                "product_description": product.get("long_description", ""),
                "standard_price": str(price),
                "brand_name": brand,
                "main_image_url": resolve_primary_image(product, backend_url),
                "keywords": ", ".join(tags[:10]),
                "product_type": product.get("type", ""),
            }
        )
    return rows


def build_gumroad_rows(catalog: Dict[str, Any], backend_url: Optional[str]) -> List[Dict[str, str]]:
    rows = []
    for product in catalog.get("products", []):
        price = product.get("price", {}).get("min", "")
        tags = product.get("tags", [])
        rows.append(
            {
                "Name": product.get("title", ""),
                "Description": product.get("long_description", ""),
                "Price": str(price),
                "Tags": ", ".join(tags[:10]),
                "Cover Image": resolve_primary_image(product, backend_url),
                "Product Type": product.get("type", ""),
            }
        )
    return rows


def build_shopier_rows(
    catalog: Dict[str, Any],
    backend_url: Optional[str],
    shopier_map: Optional[Dict[str, Any]] = None,
    price_map: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    rows = []
    shopier_map = shopier_map or {}
    price_map = price_map or {}
    base_url = backend_url.rstrip("/") if backend_url else ""
    for product in catalog.get("products", []):
        channels = product.get("channels", [])
        if "shopier" not in channels:
            continue
        sku = product.get("sku", "")
        price = product.get("price", {})
        amount = price.get("min", "") or price.get("max", "")
        currency = price.get("currency", "USD")
        override = price_map.get(sku, {})
        if override:
            if override.get("price") is not None:
                amount = override.get("price")
            if override.get("currency"):
                currency = override.get("currency")
        amount = apply_psych_rounding(amount, str(currency).upper() == "TRY")
        title = product.get("title", "")
        order_prefix = sku or "ORDER"
        checkout_url = ""
        mapped = shopier_map.get(sku, {})
        if mapped.get("url"):
            checkout_url = mapped["url"]
        elif base_url and amount:
            checkout_url = (
                f"{base_url}/api/payment/shopier/pay?"
                f"amount={amount}&currency={currency}"
                f"&order_id={order_prefix}-{{timestamp}}"
                f"&product_name={title.replace(' ', '%20')}"
            )
        rows.append(
            {
                "SKU": sku,
                "Title": title,
                "Description": product.get("long_description", ""),
                "Price": str(amount),
                "Currency": currency,
                "Image": resolve_primary_image(product, backend_url),
                "Checkout URL": checkout_url,
            }
        )
    return rows


def write_csv(path: Path, rows: List[Dict[str, str]], fields: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare marketing asset manifests and channel CSVs.")
    parser.add_argument("--catalog", required=True, help="Path to product_catalog.json")
    parser.add_argument("--output", required=True, help="Output directory for manifests")
    parser.add_argument("--backend-url", default=os.getenv("BACKEND_ORIGIN"))
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    catalog = load_catalog(catalog_path)
    shopier_map_path = Path(os.getenv("SHOPIER_PRODUCT_MAP", "docs/commerce/shopier_product_map.json"))
    shopier_price_path = Path(os.getenv("SHOPIER_PRICE_OVERRIDES", "docs/commerce/shopier_price_overrides.json"))
    shopier_map = load_optional_json(shopier_map_path)
    shopier_prices = load_optional_json(shopier_price_path)

    manifest_path = output_dir / "index.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(catalog, handle, indent=2)

    write_csv(output_dir / "channel_shopify.csv", build_shopify_rows(catalog, args.backend_url), SHOPIFY_FIELDS)
    write_csv(output_dir / "channel_etsy.csv", build_etsy_rows(catalog, args.backend_url), ETSY_FIELDS)
    write_csv(output_dir / "channel_fiverr.csv", build_fiverr_rows(catalog), FIVERR_FIELDS)
    write_csv(output_dir / "channel_amazon.csv", build_amazon_rows(catalog, args.backend_url), AMAZON_FIELDS)
    write_csv(output_dir / "channel_gumroad.csv", build_gumroad_rows(catalog, args.backend_url), GUMROAD_FIELDS)
    write_csv(
        output_dir / "channel_shopier.csv",
        build_shopier_rows(catalog, args.backend_url, shopier_map, shopier_prices),
        SHOPIER_FIELDS,
    )

    print(f"Manifest written to {manifest_path}")
    print("Channel CSVs generated: Shopify, Etsy, Fiverr, Amazon, Gumroad, Shopier")


if __name__ == "__main__":
    main()
