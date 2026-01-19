import argparse
import os
from pathlib import Path

from backend.services.alexandria_genesis import (
    GenesisConfig,
    build_genesis_log,
    resolve_genesis_output,
    write_genesis_log,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Alexandria Genesis Log.")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root to scan.",
    )
    parser.add_argument("--max-files", type=int, default=2000)
    parser.add_argument("--include-dir", action="append", default=[])
    parser.add_argument("--exclude-dir", action="append", default=[])
    args = parser.parse_args()

    root = Path(args.root).resolve()
    config = GenesisConfig(
        root=root,
        max_files=args.max_files,
        include_dirs=args.include_dir,
        exclude_dirs=args.exclude_dir,
    )
    payload = build_genesis_log(config)
    output_path = resolve_genesis_output(root)
    write_genesis_log(payload, output_path)
    print(f"Genesis log written to {output_path}")


if __name__ == "__main__":
    main()
