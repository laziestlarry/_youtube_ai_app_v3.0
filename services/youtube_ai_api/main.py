"""YouTube AI API entrypoint (shared backend)."""
import os

os.environ.setdefault("APP_TARGET", "youtube")

from backend.main import app  # noqa: E402

__all__ = ["app"]
