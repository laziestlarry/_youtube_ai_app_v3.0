import os
from pathlib import Path
from typing import Dict, List


def _truthy(value: str) -> bool:
    return str(value or "").strip().lower() in ("1", "true", "yes", "on")


def _has_any(keys: List[str]) -> bool:
    return any(os.getenv(key) for key in keys)


def _missing(keys: List[str]) -> List[str]:
    return [key for key in keys if not os.getenv(key)]


def _ai_provider_status() -> Dict[str, object]:
    if os.getenv("OLLAMA_URL"):
        return {"ready": True, "missing": []}
    if _has_any(["OPENAI_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"]):
        return {"ready": True, "missing": []}
    return {
        "ready": False,
        "missing": ["OLLAMA_URL or OPENAI_API_KEY or GEMINI_API_KEY or GROQ_API_KEY"],
    }


def _youtube_status() -> Dict[str, object]:
    if os.getenv("YOUTUBE_API_KEY"):
        return {"ready": True, "missing": []}
    required = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    missing = _missing(required)
    return {"ready": not missing, "missing": missing}


def _shopier_status() -> Dict[str, object]:
    if os.getenv("SHOPIER_PERSONAL_ACCESS_TOKEN"):
        return {"ready": True, "missing": []}
    required = ["PAYMENT_SHOPIER_API_KEY", "PAYMENT_SHOPIER_API_SECRET"]
    missing = _missing(required)
    return {"ready": not missing, "missing": missing}


def _delivery_status() -> Dict[str, object]:
    delivery_map = Path("docs/commerce/digital_delivery_map.json")
    if delivery_map.exists():
        return {"ready": True, "missing": []}
    return {"ready": False, "missing": ["docs/commerce/digital_delivery_map.json"]}


def _alexandria_status() -> Dict[str, object]:
    root = Path("docs/alexandria_protocol")
    required = [
        root / "THE_ALEXANDRIA_PROTOCOL.md",
        root / "knowledge_graph.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    return {"ready": not missing, "missing": missing}


def _analytics_status() -> Dict[str, object]:
    missing = _missing(["DATABASE_URL"])
    return {"ready": not missing, "missing": missing}


def _ops_status() -> Dict[str, object]:
    missing = _missing(["ADMIN_SECRET_KEY"])
    return {"ready": not missing, "missing": missing}


def get_skills_report() -> Dict[str, object]:
    skills = [
        {
            "id": "ai-generation",
            "label": "AI Generation",
            **_ai_provider_status(),
        },
        {
            "id": "youtube-automation",
            "label": "YouTube Automation",
            **_youtube_status(),
        },
        {
            "id": "shopier-payments",
            "label": "Shopier Payments",
            **_shopier_status(),
        },
        {
            "id": "digital-delivery",
            "label": "Digital Delivery",
            **_delivery_status(),
        },
        {
            "id": "alexandria-knowledge",
            "label": "Alexandria Knowledge",
            **_alexandria_status(),
        },
        {
            "id": "analytics-core",
            "label": "Analytics Core",
            **_analytics_status(),
        },
        {
            "id": "ops-automation",
            "label": "Ops Automation",
            **_ops_status(),
        },
    ]

    ready_count = sum(1 for skill in skills if skill["ready"])
    return {
        "summary": {
            "ready": ready_count,
            "total": len(skills),
            "degraded": len(skills) - ready_count,
        },
        "skills": skills,
        "shopier_app_mode": _truthy(os.getenv("SHOPIER_APP_MODE", "false")),
    }
