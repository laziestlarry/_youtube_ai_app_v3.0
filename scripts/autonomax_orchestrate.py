import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


def load_catalog(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_product_summaries(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    summaries = []
    for product in catalog.get("products", []):
        summaries.append(
            {
                "sku": product.get("sku"),
                "title": product.get("title"),
                "type": product.get("type"),
                "short_description": product.get("short_description"),
                "long_description": product.get("long_description"),
                "price": product.get("price"),
                "channels": product.get("channels"),
                "tags": product.get("tags"),
            }
        )
    return summaries


def request_json(
    base_url: str,
    path: str,
    payload: Optional[Dict[str, Any]],
    api_key: Optional[str],
    dry_run: bool,
) -> Optional[Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if dry_run:
        print(f"[DRY-RUN] POST {url}")
        print(json.dumps(payload, indent=2))
        return None
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    if response.text:
        return response.json()
    return {}


def run_portfolio(base_url: str, api_key: Optional[str], catalog: Dict[str, Any], dry_run: bool) -> None:
    payload = build_product_summaries(catalog)
    request_json(base_url, "/portfolio/score", payload={"items": payload}, api_key=api_key, dry_run=dry_run)


def run_pricing(
    base_url: str,
    api_key: Optional[str],
    catalog: Dict[str, Any],
    currency: str,
    dry_run: bool,
) -> None:
    payload = {
        "currency": currency,
        "products": build_product_summaries(catalog),
        "objective": "psychological pricing + margin alignment",
    }
    request_json(base_url, "/monetization/price_suggest", payload=payload, api_key=api_key, dry_run=dry_run)


def run_campaigns(
    base_url: str,
    api_key: Optional[str],
    catalog: Dict[str, Any],
    channels: List[str],
    goal: str,
    dry_run: bool,
) -> None:
    payload = {
        "goal": goal,
        "channels": channels,
        "products": build_product_summaries(catalog),
    }
    request_json(base_url, "/marketing/campaigns/suggest", payload=payload, api_key=api_key, dry_run=dry_run)


def run_ops(base_url: str, api_key: Optional[str], dry_run: bool) -> None:
    payload = {
        "events": [
            {"event": "catalog_sync", "source": "autonomax_orchestrate"},
            {"event": "utm_refresh", "source": "autonomax_orchestrate"},
            {"event": "pricing_audit", "source": "autonomax_orchestrate"},
        ]
    }
    request_json(base_url, "/ops/lifecycle/batch", payload=payload, api_key=api_key, dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Orchestrate AutonomaX API flows.")
    parser.add_argument("--api-url", default=os.getenv("AUTONOMAX_API_URL"))
    parser.add_argument("--api-key", default=os.getenv("AUTONOMAX_API_KEY"))
    parser.add_argument("--catalog", default="docs/commerce/product_catalog.json")
    parser.add_argument("--mode", choices=["portfolio", "pricing", "campaigns", "ops", "all"], default="all")
    parser.add_argument("--currency", default="TRY")
    parser.add_argument("--channels", default="shopier,shopify,etsy")
    parser.add_argument("--goal", default="first income proof + repeatable conversion")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.api_url:
        raise SystemExit("AUTONOMAX_API_URL not set.")

    catalog = load_catalog(Path(args.catalog))
    channels = [item.strip() for item in args.channels.split(",") if item.strip()]

    if args.mode in {"portfolio", "all"}:
        run_portfolio(args.api_url, args.api_key, catalog, args.dry_run)
    if args.mode in {"pricing", "all"}:
        run_pricing(args.api_url, args.api_key, catalog, args.currency, args.dry_run)
    if args.mode in {"campaigns", "all"}:
        run_campaigns(args.api_url, args.api_key, catalog, channels, args.goal, args.dry_run)
    if args.mode in {"ops", "all"}:
        run_ops(args.api_url, args.api_key, args.dry_run)


if __name__ == "__main__":
    main()
