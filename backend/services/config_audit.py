import os
from datetime import datetime, timezone
from typing import Dict, List

from backend.config.enhanced_settings import settings


def _truthy(value: str) -> bool:
    return str(value or "").strip().lower() in ("1", "true", "yes", "on")


def run_config_audit() -> Dict[str, object]:
    issues: Dict[str, List[str]] = settings.validate_configuration()
    critical: List[str] = []
    warnings: List[str] = []

    admin_key = settings.security.admin_secret_key or os.getenv("ADMIN_SECRET_KEY")
    if not admin_key:
        critical.append("ADMIN_SECRET_KEY is required for ops endpoints")

    backend_origin = os.getenv("BACKEND_ORIGIN")
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if not backend_origin:
        warnings.append("BACKEND_ORIGIN is not set")
    if not frontend_origin:
        warnings.append("FRONTEND_ORIGIN is not set")

    if settings.environment == "production" and not os.getenv("DEFAULT_ADMIN_PASSWORD"):
        warnings.append("DEFAULT_ADMIN_PASSWORD not set; admin seed will be skipped")

    if settings.environment == "production" and _truthy(os.getenv("SHOPIER_ALLOW_MOCK")):
        critical.append("SHOPIER_ALLOW_MOCK must be false in production")

    if _truthy(os.getenv("SHOPIER_APP_MODE", "false")):
        has_shopier = bool(
            os.getenv("SHOPIER_PERSONAL_ACCESS_TOKEN")
            or (
                os.getenv("PAYMENT_SHOPIER_API_KEY")
                and os.getenv("PAYMENT_SHOPIER_API_SECRET")
            )
        )
        if not has_shopier:
            warnings.append("Shopier keys missing while SHOPIER_APP_MODE is enabled")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.environment,
        "app_target": settings.app_target,
        "critical": critical,
        "warnings": warnings,
        "issues": issues,
    }
