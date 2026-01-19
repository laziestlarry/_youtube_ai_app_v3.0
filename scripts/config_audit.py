import json

from backend.services.config_audit import run_config_audit


def main() -> None:
    report = run_config_audit()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
