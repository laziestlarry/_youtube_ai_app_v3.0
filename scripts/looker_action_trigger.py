import argparse
import json
import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD = ROOT / "profit_os_execution_pack/autonomax/api_trigger.json"


def load_payload(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    if raw.startswith("POST"):
        raw = raw.split("\n", 1)[-1].strip()
    return json.loads(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="Trigger Looker Action webhook.")
    parser.add_argument("--payload", default=str(DEFAULT_PAYLOAD), help="Path to payload JSON.")
    parser.add_argument(
        "--endpoint",
        default=os.getenv("LOOKER_ACTION_ENDPOINT", "https://youtube-ai-backend-lenljbhrqq-uc.a.run.app/api/looker/trigger"),
        help="Webhook endpoint URL.",
    )
    parser.add_argument("--token", default=os.getenv("LOOKER_ACTION_TOKEN"), help="Optional token.")
    args = parser.parse_args()

    payload = load_payload(Path(args.payload))
    headers = {"Content-Type": "application/json"}
    if args.token:
        headers["X-Looker-Token"] = args.token

    response = requests.post(args.endpoint, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    print(response.text)


if __name__ == "__main__":
    main()
