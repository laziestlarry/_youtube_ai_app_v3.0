import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from autonomax.app.main import SessionLocal, run_missions  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run scheduled AutonomaX work items.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = run_missions(limit=args.limit, dry_run=args.dry_run, db=db)
        print(result)
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
