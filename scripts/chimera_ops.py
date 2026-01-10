import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def _backend_url() -> str:
    return (
        os.getenv("CHIMERA_BACKEND_URL")
        or os.getenv("BACKEND_URL")
        or "https://youtube-ai-backend-lenljbhrqq-uc.a.run.app"
    )


def _run(cmd: list[str], dry_run: bool = False) -> None:
    command_str = " ".join(cmd)
    print(f"\n▶ {command_str}")
    if dry_run:
        return
    subprocess.run(cmd, check=True)


def _env_file(name: str, default: str) -> str:
    return os.getenv(name, default)


def _ingest_shopier_exports(dry_run: bool = False) -> None:
    record_mode = os.getenv("SHOPIER_RECORD_MODE", "none")
    orders_csv = os.getenv("SHOPIER_ORDERS_CSV")
    payouts_csv = os.getenv("SHOPIER_PAYOUTS_CSV")
    if orders_csv:
        _run(
            [
                PYTHON,
                "scripts/ingest_shopier_csv.py",
                "--csv",
                orders_csv,
                "--mode",
                "orders",
                "--record",
                record_mode,
            ],
            dry_run=dry_run,
        )
    if payouts_csv:
        _run(
            [
                PYTHON,
                "scripts/ingest_shopier_csv.py",
                "--csv",
                payouts_csv,
                "--mode",
                "payouts",
                "--record",
                record_mode,
            ],
            dry_run=dry_run,
        )


def run_daily(dry_run: bool = False) -> None:
    backend_url = _backend_url()
    _run([PYTHON, "scripts/verify_shopier_checkout.py"], dry_run=dry_run)
    _run(
        [
            PYTHON,
            "scripts/shopier_catalog_import.py",
            "--env-file",
            _env_file("SHOPIER_ENV_FILE", ".env.shopier"),
            "--media-base-url",
            backend_url,
            "--update-existing",
        ],
        dry_run=dry_run,
    )
    _run(
        [
            PYTHON,
            "scripts/prepare_marketing_assets.py",
            "--catalog",
            "docs/commerce/product_catalog.json",
            "--output",
            "marketing_assets",
            "--backend-url",
            backend_url,
        ],
        dry_run=dry_run,
    )
    _run([PYTHON, "scripts/generate_utm_links.py"], dry_run=dry_run)
    if os.getenv("CHIMERA_LOOKER_TEST") == "1":
        _run([PYTHON, "scripts/looker_action_trigger.py"], dry_run=dry_run)


def run_weekly(dry_run: bool = False) -> None:
    backend_url = _backend_url()
    _run(
        [
            PYTHON,
            "scripts/publish_shopify_catalog.py",
            "--env-file",
            _env_file("SHOPIFY_ENV_FILE", ".env2"),
            "--backend-url",
            backend_url,
            "--update-existing",
            "--update-images",
        ],
        dry_run=dry_run,
    )
    _run(
        [
            PYTHON,
            "scripts/prepare_marketing_assets.py",
            "--catalog",
            "docs/commerce/product_catalog.json",
            "--output",
            "marketing_assets",
            "--backend-url",
            backend_url,
        ],
        dry_run=dry_run,
    )
    _ingest_shopier_exports(dry_run=dry_run)


def run_monthly(dry_run: bool = False) -> None:
    print("\n▶ Monthly review: pricing bands, refund rate, and SKU pruning.")
    if dry_run:
        return
    # Placeholder for future monthly automation (pricing + portfolio pruning).


def main() -> None:
    parser = argparse.ArgumentParser(description="Chimera ops scheduler runner.")
    parser.add_argument("phase", choices=["daily", "weekly", "monthly", "all"], help="Ops phase.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running.")
    args = parser.parse_args()

    if args.phase in {"daily", "all"}:
        run_daily(dry_run=args.dry_run)
    if args.phase in {"weekly", "all"}:
        run_weekly(dry_run=args.dry_run)
    if args.phase in {"monthly", "all"}:
        run_monthly(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
