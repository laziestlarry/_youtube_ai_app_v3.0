from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, List, Optional, Any
import json
import os
from pathlib import Path
import secrets
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class AISettings(BaseSettings):
    """AI-related configuration settings."""
    provider: str = Field("deepseek")  # openai, deepseek, llama3, mistral, etc.
    openai_api_key: Optional[str] = Field(None)
    model_name: str = Field("deepseek-llm")
    max_tokens: int = Field(4000)
    temperature: float = Field(0.7)
    auto_generation_enabled: bool = Field(True)
    batch_processing_enabled: bool = Field(True)
    quality_threshold: float = Field(0.8)
    content_moderation_enabled: bool = Field(True)
    
    model_config = SettingsConfigDict(
        env_prefix="AI_",
        protected_namespaces=()
    )

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    url: str = Field("sqlite:///./youtube_ai.db")
    pool_size: int = Field(10)
    max_overflow: int = Field(20)
    pool_timeout: int = Field(30)
    pool_recycle: int = Field(3600)
    echo: bool = Field(False)
    backup_enabled: bool = Field(True)
    backup_interval: int = Field(24)
    
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        from_attributes=True,
        protected_namespaces=()
    )

class CacheSettings(BaseSettings):
    """Cache configuration settings."""
    enabled: bool = Field(True)
    redis_url: str = Field("redis://localhost:6379")
    default_ttl: int = Field(3600)
    max_connections: int = Field(10)
    
    model_config = SettingsConfigDict(
        env_prefix="CACHE_",
        protected_namespaces=()
    )

class AnalyticsSettings(BaseSettings):
    """Analytics configuration settings."""
    enabled: bool = Field(True)
    realtime_enabled: bool = Field(True)
    export_enabled: bool = Field(True)
    retention_days: int = Field(90)
    aggregation_interval: int = Field(300)
    
    model_config = SettingsConfigDict(
        env_prefix="ANALYTICS_",
        protected_namespaces=()
    )

class SchedulingSettings(BaseSettings):
    """Scheduling configuration settings."""
    enabled: bool = Field(True)
    max_concurrent_tasks: int = Field(5)
    task_timeout: int = Field(3600)
    retry_attempts: int = Field(3)
    retry_delay: int = Field(300)
    max_local_concurrent_tasks: int = Field(2, description="Max concurrent local (CPU/GPU) tasks")
    max_cloud_concurrent_tasks: int = Field(20, description="Max concurrent cloud (IO) tasks")
    
    model_config = SettingsConfigDict(
        env_prefix="SCHEDULING_",
        protected_namespaces=()
    )

class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    secret_key: Optional[str] = Field(None)
    jwt_algorithm: str = Field("HS256")
    jwt_expiration: int = Field(86400)
    cors_origins: List[str] = Field(["*"])
    rate_limit_enabled: bool = Field(True)
    rate_limit_requests: int = Field(100)
    rate_limit_window: int = Field(3600)
    
    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        protected_namespaces=()
    )

class StorageSettings(BaseSettings):
    """Storage configuration settings."""
    provider: str = Field("local")  # local, gcs, s3
    local_path: str = Field("./storage")
    gcs_bucket: Optional[str] = Field(None)
    gcs_credentials: Optional[str] = Field(None)
    s3_bucket: Optional[str] = Field(None)
    s3_region: Optional[str] = Field(None)
    max_file_size: int = Field(100 * 1024 * 1024)  # 100MB
    
    model_config = SettingsConfigDict(
        env_prefix="STORAGE_",
        protected_namespaces=()
    )

class NotificationSettings(BaseSettings):
    """Notification configuration settings."""
    enabled: bool = Field(True)
    email_enabled: bool = Field(False)
    webhook_enabled: bool = Field(False)
    smtp_server: Optional[str] = Field(None)
    smtp_port: int = Field(587)
    smtp_username: Optional[str] = Field(None)
    smtp_password: Optional[str] = Field(None)
    webhook_url: Optional[str] = Field(None)
    
    model_config = SettingsConfigDict(
        env_prefix="NOTIFICATIONS_",
        protected_namespaces=()
    )

class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration."""
    log_level: str = Field("INFO")
    log_format: str = Field("json")  # json, text
    metrics_enabled: bool = Field(True)
    health_check_interval: int = Field(30)
    performance_monitoring: bool = Field(True)
    
    model_config = SettingsConfigDict(
        env_prefix="MONITORING_",
        protected_namespaces=()
    )

class QualityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ContentType(str, Enum):
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    TUTORIAL = "tutorial"

class YouTubeSettings(BaseSettings):
    """YouTube API configuration settings."""
    api_key: Optional[str] = Field(None)
    client_id: Optional[str] = Field(None)
    client_secret: Optional[str] = Field(None)
    redirect_uri: str = Field("http://localhost:8000/oauth/callback")
    
    model_config = SettingsConfigDict(
        env_prefix="YOUTUBE_",
        protected_namespaces=()
    )

class PaymentSettings(BaseSettings):
    """Payment configuration settings."""
    stripe_secret_key: Optional[str] = Field(None)
    stripe_publishable_key: Optional[str] = Field(None)
    payoneer_api_key: Optional[str] = Field(None)
    payoneer_secret_key: Optional[str] = Field(None)
    payoneer_program_id: Optional[str] = Field(None)
    shopier_api_key: Optional[str] = Field(None, description="Shopier API Key")
    shopier_api_secret: Optional[str] = Field(None, description="Shopier API Secret")
    shopier_personal_access_token: Optional[str] = Field(None, validation_alias="SHOPIER_PERSONAL_ACCESS_TOKEN")
    shopier_webhook_token: Optional[str] = Field(None, validation_alias="SHOPIER_WEBHOOK_TOKEN", description="Shopier Webhook Token")
    shopify_admin_token: Optional[str] = Field(None, validation_alias="SHOPIFY_ADMIN_TOKEN")
    shopify_storefront_token: Optional[str] = Field(None, validation_alias="SHOPIFY_STOREFRONT_TOKEN")
    shopify_shop_domain: Optional[str] = Field(None, validation_alias="SHOPIFY_SHOP_DOMAIN")
    shopify_api_version: str = Field("2025-07", validation_alias="SHOPIFY_API_VERSION")
    
    model_config = SettingsConfigDict(
        env_prefix="PAYMENT_",
        protected_namespaces=()
    )

class EnhancedSettings(BaseSettings):
    """Main application settings."""
    app_name: str = Field("YouTube AI Platform")
    app_version: str = Field("2.0.0")
    debug: bool = Field(False)
    environment: str = Field("production")
    backend_origin: str = Field("http://localhost:8000")
    frontend_origin: str = Field("http://localhost:3001")
    shopier_app_mode: bool = Field(
        False,
        validation_alias="SHOPIER_APP_MODE",
        description="Serve the Shopier storefront as the root app view."
    )
    
    # Sub-configurations
    ai: AISettings = AISettings()
    database: DatabaseSettings = DatabaseSettings()
    cache: CacheSettings = CacheSettings()
    analytics: AnalyticsSettings = AnalyticsSettings()
    scheduling: SchedulingSettings = SchedulingSettings()
    security: SecuritySettings = SecuritySettings()
    storage: StorageSettings = StorageSettings()
    notifications: NotificationSettings = NotificationSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    payment: PaymentSettings = PaymentSettings()
    youtube: YouTubeSettings = YouTubeSettings()
    
    # Configuration file path
    config_file: str = Field("config.json", env="CONFIG_FILE")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=()
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Ensure secret_key is loaded from env if mapping failed
        if not self.security.secret_key:
            self.security.secret_key = os.getenv("SECURITY_SECRET_KEY") or os.getenv("SECRET_KEY")
            
        # Security key fallback for dev/demo
        if not self.security.secret_key:
            self.security.secret_key = secrets.token_urlsafe(64)
            print("[WARNING] No SECRET_KEY found in environment. Generated a random key for this session. This is NOT secure for production!")
        elif len(self.security.secret_key) < 32:
            print("[WARNING] SECRET_KEY is too short (<32 chars). This is NOT secure for production!")
        
        if not self.database.url or self.database.url == "sqlite:///./youtube_ai.db":
            self.database.url = os.getenv("DATABASE_URL") or "sqlite:///./youtube_ai.db"
            
        # Ensure YouTube settings are loaded from env if prefix mapping failed
        if not self.youtube.client_id:
            self.youtube.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        if not self.youtube.client_secret:
            self.youtube.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        if not self.youtube.api_key:
            self.youtube.api_key = os.getenv("YOUTUBE_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        
        self.load_from_file()
    
    def load_from_file(self):
        """Load configuration from JSON file if it exists."""
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Update settings with file configuration
                for section, values in file_config.items():
                    if hasattr(self, section) and isinstance(values, dict):
                        section_obj = getattr(self, section)
                        for key, value in values.items():
                            if hasattr(section_obj, key):
                                setattr(section_obj, key, value)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def save_to_file(self):
        """Save current configuration to JSON file."""
        config_data = {}
        
        # Collect all sub-configuration data
        for attr_name in ['ai', 'database', 'cache', 'analytics', 'scheduling', 
                         'security', 'storage', 'notifications', 'monitoring']:
            if hasattr(self, attr_name):
                section_obj = getattr(self, attr_name)
                config_data[attr_name] = section_obj.dict()
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving config file {self.config_file}: {e}")
    
    def update_section(self, section: str, updates: Dict[str, Any]):
        """Update a specific configuration section."""
        if hasattr(self, section):
            section_obj = getattr(self, section)
            for key, value in updates.items():
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
            self.save_to_file()
        else:
            raise ValueError(f"Unknown configuration section: {section}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get configuration for a specific section."""
        if hasattr(self, section):
            section_obj = getattr(self, section)
            return section_obj.dict()
        else:
            raise ValueError(f"Unknown configuration section: {section}")
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate the current configuration and return any issues."""
        issues = {}
        
        # Validate AI settings
        ai_issues = []
        if self.ai.provider == "openai":
            if not self.ai.openai_api_key or self.ai.openai_api_key == "your-api-key-here":
                ai_issues.append("OpenAI API key is not set or using placeholder value")
        if self.ai.temperature < 0 or self.ai.temperature > 2:
            ai_issues.append("Temperature should be between 0 and 2")
        if self.ai.max_tokens < 1 or self.ai.max_tokens > 8000:
            ai_issues.append("Max tokens should be between 1 and 8000")
        if ai_issues:
            issues['ai'] = ai_issues
        
        # Validate database settings
        db_issues = []
        if not self.database.url:
            db_issues.append("Database URL is required")
        if self.database.pool_size < 1:
            db_issues.append("Pool size must be at least 1")
        if db_issues:
            issues['database'] = db_issues
        
        # Validate security settings
        security_issues = []
        if not self.security.secret_key or len(self.security.secret_key) < 32:
            security_issues.append("Secret key should be at least 32 characters long")
        if self.security.jwt_expiration < 300:  # 5 minutes minimum
            security_issues.append("JWT expiration should be at least 300 seconds")
        if security_issues:
            issues['security'] = security_issues
        
        # Validate storage settings
        storage_issues = []
        if self.storage.provider == "gcs" and not self.storage.gcs_bucket:
            storage_issues.append("GCS bucket name is required when using GCS provider")
        if self.storage.provider == "s3" and not self.storage.s3_bucket:
            storage_issues.append("S3 bucket name is required when using S3 provider")
        if self.storage.max_file_size < 1024:  # 1KB minimum
            storage_issues.append("Max file size should be at least 1KB")
        if storage_issues:
            issues['storage'] = storage_issues
        
        return issues
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about the current environment."""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "debug": self.debug,
            "python_version": os.sys.version,
            "config_file": self.config_file,
            "config_file_exists": Path(self.config_file).exists(),
        }

# Global settings instance
settings = EnhancedSettings()

# Configuration validation on startup
def validate_startup_config():
    """Validate configuration on application startup."""
    issues = settings.validate_configuration()
    if issues:
        print("Configuration validation issues found:")
        for section, section_issues in issues.items():
            print(f"  {section.upper()}:")
            for issue in section_issues:
                print(f"    - {issue}")
        
        if settings.environment == "production":
            raise ValueError("Configuration validation failed in production environment")
        else:
            print("Warning: Configuration issues detected in non-production environment")
    else:
        print("Configuration validation passed")

# Export commonly used settings
def get_settings() -> EnhancedSettings:
    return settings

def get_ai_settings() -> AISettings:
    return settings.ai

def get_database_settings() -> DatabaseSettings:
    return settings.database

def get_security_settings() -> SecuritySettings:
    return settings.security

def get_storage_settings() -> StorageSettings:
    return settings.storage
