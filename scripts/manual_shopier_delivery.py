import argparse
import os

from backend.services.delivery_service import delivery_service
from modules.ai_agency.fulfillment_engine import fulfillment_engine


def main() -> None:
    parser = argparse.ArgumentParser(description="Manually enqueue digital delivery.")
    parser.add_argument("--order-id", required=True)
    parser.add_argument("--sku", required=True)
    parser.add_argument("--email")
    parser.add_argument("--amount", type=float, default=0.0)
    parser.add_argument("--currency", default="TRY")
    parser.add_argument("--base-url", default=os.getenv("BACKEND_ORIGIN", "https://youtube-ai-backend-lenljbhrqq-uc.a.run.app"))
    args = parser.parse_args()

    payload = {
        "platform_order_id": args.order_id,
        "product_sku": args.sku,
        "buyer_email": args.email,
        "total_order_value": args.amount,
        "currency": args.currency,
    }

    if args.amount > 0:
        fulfillment_engine.record_sale(
            args.amount,
            f"Manual Shopier Order: {args.order_id}",
            metadata={
                "order_id": args.order_id,
                "sku": args.sku,
                "currency": args.currency,
                "channel": "shopier",
            },
        )

    result = delivery_service.deliver_digital(payload, args.base_url)
    print(result)


if __name__ == "__main__":
    main()
