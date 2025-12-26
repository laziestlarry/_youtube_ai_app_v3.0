"""
Centralized configuration settings.
This file now acts as a proxy for the unified enhanced_settings.
"""
from backend.config.enhanced_settings import settings as enhanced_settings
import os

# Create a settings proxy that maintains compatibility with the old core.config.settings
class SettingsProxy:
    def __getattr__(self, name):
        # Map old top-level names to new nested names if necessary
        mapping = {
            "database_url": ("database", "url"),
            "openai_api_key": ("ai", "openai_api_key"),
            "secret_key": ("security", "secret_key"),
            "jwt_algorithm": ("security", "jwt_algorithm"),
            "jwt_expiration": ("security", "jwt_expiration"),
            "youtube_api_key": ("youtube", "api_key"),
            "youtube_client_id": ("youtube", "client_id"),
            "youtube_client_secret": ("youtube", "client_secret"),
            "version": ("app_version", None), # Special case for top-level
            "environment": ("environment", None),
            "cors_origins": ("security", "cors_origins"),
            "frontend_origin": ("security", "cors_origins"), # Note: types may differ
        }
        
        if name in mapping:
            section, key = mapping[name]
            if key is None:
                return getattr(enhanced_settings, section)
            section_obj = getattr(enhanced_settings, section)
            return getattr(section_obj, key)
            
        # Fallback to top-level attributes
        if hasattr(enhanced_settings, name):
            return getattr(enhanced_settings, name)
            
        # Special case for frontend_origin which was a string but now usually a list
        if name == "frontend_origin":
            return os.getenv("FRONTEND_ORIGIN", "http://localhost:3001")
            
        raise AttributeError(f"'SettingsProxy' object has no attribute '{name}'")

settings = SettingsProxy()