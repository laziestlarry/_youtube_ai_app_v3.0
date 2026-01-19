import argparse
import json

from backend.services.delivery_service import delivery_service


def main() -> None:
    parser = argparse.ArgumentParser(description="Retry queued digital deliveries.")
    parser.add_argument("--base-url", dest="base_url", default=None)
    parser.add_argument("--max-items", dest="max_items", type=int, default=50)
    args = parser.parse_args()

    result = delivery_service.retry_queued_deliveries(
        base_url=args.base_url,
        max_items=args.max_items,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
