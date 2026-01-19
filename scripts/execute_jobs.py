import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from autonomax.workflows.executor import run_job_queue  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute queued AutonomaX jobs.")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    result = run_job_queue(limit=args.limit)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
