import argparse
import csv
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ORDER_KEYS = {
    "order_id": [
        "siparisno",
        "siparisid",
        "orderno",
        "orderid",
        "platformorderid",
    ],
    "order_date": [
        "siparistarihi",
        "orderdate",
        "tarih",
        "date",
    ],
    "product_name": [
        "urunadi",
        "productname",
        "title",
        "urun",
    ],
    "status": [
        "durum",
        "status",
    ],
    "email": [
        "eposta",
        "email",
        "mail",
    ],
    "gross": [
        "tutar",
        "toplamtutar",
        "gross",
        "amount",
        "total",
    ],
    "fee": [
        "kesinti",
        "komisyon",
        "commission",
        "fee",
    ],
    "net": [
        "nettutar",
        "net",
        "netbakiye",
    ],
}

PAYOUT_KEYS = {
    "payout_date": [
        "odemetarihi",
        "payoutdate",
        "gonderimtarihi",
        "tarih",
        "date",
    ],
    "reference": [
        "odemeid",
        "referans",
        "reference",
        "batchid",
    ],
    "gross": [
        "tutar",
        "bruttutar",
        "gross",
        "amount",
        "total",
    ],
    "fee": [
        "kesinti",
        "komisyon",
        "commission",
        "fee",
    ],
    "net": [
        "nettutar",
        "net",
        "netbakiye",
    ],
    "status": [
        "durum",
        "status",
    ],
}


def normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(text))
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "", normalized)
    return normalized.lower()


def parse_money(value: Any) -> Tuple[Optional[float], Optional[str]]:
    if value is None:
        return None, None
    text = str(value).strip()
    if not text:
        return None, None
    currency = None
    upper = text.upper()
    if "TL" in upper or "TRY" in upper:
        currency = "TRY"
    elif "USD" in upper or "$" in text:
        currency = "USD"
    elif "EUR" in upper or "€" in text:
        currency = "EUR"

    cleaned = re.sub(r"[^\d,.\-]", "", text)
    if cleaned.count(",") == 1 and cleaned.count(".") >= 1:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif cleaned.count(",") == 1 and cleaned.count(".") == 0:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned), currency
    except ValueError:
        return None, currency


def parse_date(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    patterns = [
        "%d/%m/%Y %H:%M",
        "%d.%m.%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
    ]
    for pattern in patterns:
        try:
            return datetime.strptime(text, pattern).isoformat()
        except ValueError:
            continue
    return None


def detect_mode(headers: Iterable[str]) -> Optional[str]:
    normalized = {normalize(h) for h in headers}
    if any(key in normalized for key in ["siparisno", "siparisid", "orderno", "orderid"]):
        return "orders"
    if any(key in normalized for key in ["payoutdate", "odemetarihi", "netbakiye"]):
        return "payouts"
    return None


def pick_value(row: Dict[str, str], keys: List[str]) -> Optional[str]:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def normalize_row(row: Dict[str, str]) -> Dict[str, str]:
    normalized = {}
    for key, value in row.items():
        normalized[normalize(key)] = value
    return normalized


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def ensure_log_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, rows: List[Dict[str, Any]], dry_run: bool) -> None:
    ensure_log_dir(path)
    if dry_run:
        return
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_earnings(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"total_earnings": 0.0, "daily": 0.0, "history": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_earnings(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def earnings_has_source(data: Dict[str, Any], source: str) -> bool:
    for entry in data.get("history", []):
        if entry.get("source") == source:
            return True
    return False


def try_record_sale(amount: float, source: str, metadata: Dict[str, Any]) -> bool:
    try:
        from modules.ai_agency.fulfillment_engine import fulfillment_engine
    except Exception:
        return False
    try:
        fulfillment_engine.record_sale(amount, source, metadata=metadata)
        return True
    except Exception:
        return False


def ingest_orders(
    rows: List[Dict[str, str]],
    log_path: Path,
    record_mode: str,
    earnings_path: Path,
    currency_default: str,
    dry_run: bool,
) -> int:
    payloads = []
    earnings = load_earnings(earnings_path)
    recorded = 0

    for row in rows:
        normalized = normalize_row(row)
        order_id = pick_value(normalized, ORDER_KEYS["order_id"]) or ""
        order_date = pick_value(normalized, ORDER_KEYS["order_date"])
        product_name = pick_value(normalized, ORDER_KEYS["product_name"]) or ""
        status = pick_value(normalized, ORDER_KEYS["status"]) or ""
        email = pick_value(normalized, ORDER_KEYS["email"]) or ""
        gross_raw = pick_value(normalized, ORDER_KEYS["gross"])
        fee_raw = pick_value(normalized, ORDER_KEYS["fee"])
        net_raw = pick_value(normalized, ORDER_KEYS["net"])

        gross, currency = parse_money(gross_raw)
        fee, _ = parse_money(fee_raw)
        net, _ = parse_money(net_raw)
        currency = currency or currency_default

        payloads.append(
            {
                "event": "order",
                "order_id": order_id,
                "order_date": parse_date(order_date) if order_date else None,
                "product_name": product_name,
                "status": status,
                "email": email,
                "gross": gross,
                "fee": fee,
                "net": net,
                "currency": currency,
                "ingested_at": datetime.utcnow().isoformat(),
            }
        )

        if record_mode != "none":
            amount = net if record_mode == "net" else gross
            if amount is None:
                continue
            source = f"Shopier Order: {order_id or product_name}"
            if earnings_has_source(earnings, source):
                continue
            if not dry_run:
                recorded_db = try_record_sale(
                    float(amount),
                    source,
                    {
                        "order_id": order_id,
                        "product_name": product_name,
                        "email": email,
                        "currency": currency,
                        "status": status,
                        "channel": "shopier",
                        "recorded_from": "csv",
                    },
                )
                if not recorded_db:
                    earnings["history"].append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "amount": float(amount),
                            "source": source,
                        }
                    )
                    earnings["total_earnings"] = float(earnings.get("total_earnings", 0)) + float(amount)
                    earnings["daily"] = float(earnings.get("daily", 0)) + float(amount)
            recorded += 1

    append_jsonl(log_path, payloads, dry_run)
    if record_mode != "none" and not dry_run:
        save_earnings(earnings_path, earnings)
    return recorded


def ingest_payouts(
    rows: List[Dict[str, str]],
    log_path: Path,
    record_mode: str,
    earnings_path: Path,
    currency_default: str,
    dry_run: bool,
) -> int:
    payloads = []
    earnings = load_earnings(earnings_path)
    recorded = 0

    for row in rows:
        normalized = normalize_row(row)
        payout_date = pick_value(normalized, PAYOUT_KEYS["payout_date"])
        reference = pick_value(normalized, PAYOUT_KEYS["reference"]) or ""
        status = pick_value(normalized, PAYOUT_KEYS["status"]) or ""
        gross_raw = pick_value(normalized, PAYOUT_KEYS["gross"])
        fee_raw = pick_value(normalized, PAYOUT_KEYS["fee"])
        net_raw = pick_value(normalized, PAYOUT_KEYS["net"])

        gross, currency = parse_money(gross_raw)
        fee, _ = parse_money(fee_raw)
        net, _ = parse_money(net_raw)
        currency = currency or currency_default

        payloads.append(
            {
                "event": "payout",
                "payout_date": parse_date(payout_date) if payout_date else None,
                "reference": reference,
                "status": status,
                "gross": gross,
                "fee": fee,
                "net": net,
                "currency": currency,
                "ingested_at": datetime.utcnow().isoformat(),
            }
        )

        if record_mode != "none":
            amount = net if record_mode == "net" else gross
            if amount is None:
                continue
            source = f"Shopier Payout: {reference or payout_date or 'batch'}"
            if earnings_has_source(earnings, source):
                continue
            if not dry_run:
                recorded_db = try_record_sale(
                    float(amount),
                    source,
                    {
                        "reference": reference,
                        "currency": currency,
                        "status": status,
                        "channel": "shopier",
                        "recorded_from": "csv",
                    },
                )
                if not recorded_db:
                    earnings["history"].append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "amount": float(amount),
                            "source": source,
                        }
                    )
                    earnings["total_earnings"] = float(earnings.get("total_earnings", 0)) + float(amount)
                    earnings["daily"] = float(earnings.get("daily", 0)) + float(amount)
            recorded += 1

    append_jsonl(log_path, payloads, dry_run)
    if record_mode != "none" and not dry_run:
        save_earnings(earnings_path, earnings)
    return recorded


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Shopier CSV exports into logs and earnings.")
    parser.add_argument("--csv", required=True, help="Path to Shopier CSV export.")
    parser.add_argument("--mode", choices=["auto", "orders", "payouts"], default="auto")
    parser.add_argument("--record", choices=["none", "gross", "net"], default="none")
    parser.add_argument("--earnings", default="earnings.json")
    parser.add_argument("--currency", default="TRY")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"Missing CSV file: {csv_path}")

    rows = load_csv(csv_path)
    if not rows:
        raise SystemExit("CSV has no rows.")

    headers = rows[0].keys()
    mode = args.mode
    if mode == "auto":
        mode = detect_mode(headers)
    if mode not in {"orders", "payouts"}:
        raise SystemExit("Unable to detect mode. Use --mode orders or --mode payouts.")

    earnings_path = Path(args.earnings)
    if mode == "orders":
        log_path = Path("logs/shopier_orders_ingested.jsonl")
        recorded = ingest_orders(rows, log_path, args.record, earnings_path, args.currency, args.dry_run)
    else:
        log_path = Path("logs/shopier_payouts.jsonl")
        recorded = ingest_payouts(rows, log_path, args.record, earnings_path, args.currency, args.dry_run)

    print(f"Ingested {len(rows)} rows as {mode}. Recorded {recorded} earnings entries.")


if __name__ == "__main__":
    main()
