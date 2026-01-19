import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from autonomax.app.main import (  # noqa: E402
    SessionLocal,
    import_blueprints,
    import_affiliates,
    register_influencer,
    bind_protocol,
)


def run() -> None:
    db = SessionLocal()
    try:
        print(import_blueprints(db=db))
        print(import_affiliates(db=db))
        print(
            register_influencer(
                {
                    "name": "Justin (Real Money Strategies)",
                    "channel_url": "https://www.youtube.com/@realmoneystrategies",
                    "contact_email": "justin@realmstrategist.com",
                    "notes": "Extract workflows for automated income generation and upgrade loops.",
                },
                db=db,
            )
        )
        print(
            bind_protocol(
                {
                    "target_path": "/Users/pq/_project_",
                    "protocol_name": "united",
                },
                db=db,
            )
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
