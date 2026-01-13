from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from ..config.enhanced_settings import settings, validate_startup_config
from ..auth.dependencies import get_current_admin_user
from ..models.responses import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/config", tags=["Configuration"])

class ConfigUpdateRequest(BaseModel):
    section: str
    updates: Dict[str, Any]

class ConfigSectionResponse(BaseModel):
    section: str
    data: Dict[str, Any]

class ValidationIssue(BaseModel):
    section: str
    issues: List[str]

class EnvironmentInfo(BaseModel):
    app_target: str
    app_name: str
    app_version: str
    environment: str
    debug: bool
    python_version: str
    config_file: str
    config_file_exists: bool

@router.get("/current", response_model=APIResponse)
async def get_current_configuration(
    admin_user = Depends(get_current_admin_user)
):
    """Get the current system configuration."""
    try:
        config_data = {
            "ai": settings.ai.dict(),
            "database": settings.database.dict(),
            "cache": settings.cache.dict(),
            "analytics": settings.analytics.dict(),
            "scheduling": settings.scheduling.dict(),
            "security": {
                # Exclude sensitive data
                "jwt_algorithm": settings.security.jwt_algorithm,
                "jwt_expiration": settings.security.jwt_expiration,
                "cors_origins": settings.security.cors_origins,
                "rate_limit_enabled": settings.security.rate_limit_enabled,
                "rate_limit_requests": settings.security.rate_limit_requests,
                "rate_limit_window": settings.security.rate_limit_window,
            },
            "storage": settings.storage.dict(),
            "notifications": settings.notifications.dict(),
            "monitoring": settings.monitoring.dict(),
        }
        
        return APIResponse(
            status="success",
            data=config_data,
            message="Configuration retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/section/{section_name}", response_model=APIResponse)
async def get_configuration_section(
    section_name: str,
    admin_user = Depends(get_current_admin_user)
):
    """Get configuration for a specific section."""
    try:
        section_data = settings.get_section(section_name)
        
        # Filter sensitive data for security section
        if section_name == "security":
            section_data = {
                k: v for k, v in section_data.items() 
                if k not in ["secret_key"]
            }
        
        return APIResponse(
            status="success",
            data=ConfigSectionResponse(section=section_name, data=section_data),
            message=f"Configuration section '{section_name}' retrieved successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving configuration section: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update", response_model=APIResponse)
async def update_configuration(
    request: ConfigUpdateRequest,
    admin_user = Depends(get_current_admin_user)
):
    """Update configuration for a specific section."""
    try:
        # Validate that sensitive settings aren't being updated inappropriately
        if request.section == "security":
            sensitive_keys = ["secret_key"]
            for key in sensitive_keys:
                if key in request.updates:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Cannot update sensitive setting: {key}"
                    )
        
        # Update the configuration
        settings.update_section(request.section, request.updates)
        
        # Validate the updated configuration
        issues = settings.validate_configuration()
        if issues:
            logger.warning(f"Configuration validation issues after update: {issues}")
        
        return APIResponse(
            status="success",
            data={
                "section": request.section,
                "updated_keys": list(request.updates.keys()),
                "validation_issues": issues
            },
            message="Configuration updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=APIResponse)
async def validate_configuration(
    admin_user = Depends(get_current_admin_user)
):
    """Validate the current configuration."""
    try:
        issues = settings.validate_configuration()
        
        validation_results = []
        for section, section_issues in issues.items():
            validation_results.append(
                ValidationIssue(section=section, issues=section_issues)
            )
        
        return APIResponse(
            status="success" if not issues else "warning",
            data={
                "valid": len(issues) == 0,
                "issues": validation_results,
                "total_issues": sum(len(section_issues) for section_issues in issues.values())
            },
            message="Configuration validation completed"
        )
    except Exception as e:
        logger.error(f"Error validating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/environment", response_model=APIResponse)
async def get_environment_info(
    admin_user = Depends(get_current_admin_user)
):
    """Get information about the current environment."""
    try:
        env_info = settings.get_environment_info()
        
        return APIResponse(
            status="success",
            data=EnvironmentInfo(**env_info),
            message="Environment information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving environment info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-section/{section_name}", response_model=APIResponse)
async def reset_configuration_section(
    section_name: str,
    admin_user = Depends(get_current_admin_user)
):
    """Reset a configuration section to default values."""
    try:
        # Create a new instance of the section with default values
        section_classes = {
            "ai": settings.ai.__class__,
            "database": settings.database.__class__,
            "cache": settings.cache.__class__,
            "analytics": settings.analytics.__class__,
            "scheduling": settings.scheduling.__class__,
            "security": settings.security.__class__,
            "storage": settings.storage.__class__,
            "notifications": settings.notifications.__class__,
            "monitoring": settings.monitoring.__class__,
        }
        
        if section_name not in section_classes:
            raise HTTPException(status_code=404, detail=f"Unknown section: {section_name}")
        
        # Don't allow resetting security section for safety
        if section_name == "security":
            raise HTTPException(
                status_code=400, 
                detail="Security section cannot be reset for safety reasons"
            )
        
        # Create new instance with defaults
        default_section = section_classes[section_name]()
        setattr(settings, section_name, default_section)
        
        # Save the updated configuration
        settings.save_to_file()
        
        return APIResponse(
            status="success",
            data={"section": section_name, "reset_to_defaults": True},
            message=f"Configuration section '{section_name}' reset to defaults"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting configuration section: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup", response_model=APIResponse)
async def backup_configuration(
    admin_user = Depends(get_current_admin_user)
):
    """Create a backup of the current configuration."""
    try:
        import shutil
        from datetime import datetime
        from pathlib import Path
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"config_backup_{timestamp}.json"
        backup_path = Path("backups") / backup_filename
        
        # Ensure backup directory exists
        backup_path.parent.mkdir(exist_ok=True)
        
        # Copy current config file to backup
        if Path(settings.config_file).exists():
            shutil.copy2(settings.config_file, backup_path)
        else:
            # If no config file exists, save current settings
            settings.save_to_file()
            shutil.copy2(settings.config_file, backup_path)
        
        return APIResponse(
            status="success",
            data={
                "backup_file": str(backup_path),
                "timestamp": timestamp,
                "original_file": settings.config_file
            },
            message="Configuration backup created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating configuration backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore/{backup_filename}", response_model=APIResponse)
async def restore_configuration(
    backup_filename: str,
    admin_user = Depends(get_current_admin_user)
):
    """Restore configuration from a backup file."""
    try:
        from pathlib import Path
        import shutil
        
        backup_path = Path("backups") / backup_filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        # Create a backup of current config before restoring
        current_backup = f"config_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if Path(settings.config_file).exists():
            shutil.copy2(settings.config_file, Path("backups") / current_backup)
        
        # Restore from backup
        shutil.copy2(backup_path, settings.config_file)
        
        # Reload settings
        settings.load_from_file()
        
        # Validate restored configuration
        issues = settings.validate_configuration()
        
        return APIResponse(
            status="success" if not issues else "warning",
            data={
                "restored_from": backup_filename,
                "current_backup": current_backup,
                "validation_issues": issues
            },
            message="Configuration restored successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backups", response_model=APIResponse)
async def list_configuration_backups(
    admin_user = Depends(get_current_admin_user)
):
    """List available configuration backup files."""
    try:
        from pathlib import Path
        import os
        
        backup_dir = Path("backups")
        if not backup_dir.exists():
            return APIResponse(
                status="success",
                data={"backups": []},
                message="No backup directory found"
            )
        
        backups = []
        for backup_file in backup_dir.glob("config_*.json"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "path": str(backup_file)
            })
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return APIResponse(
            status="success",
            data={"backups": backups},
            message=f"Found {len(backups)} configuration backups"
        )
    except Exception as e:
        logger.error(f"Error listing configuration backups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schema", response_model=APIResponse)
async def get_configuration_schema(
    admin_user = Depends(get_current_admin_user)
):
    """Get the configuration schema for validation and UI generation."""
    try:
        schema = {
            "ai": {
                "openai_api_key": {"type": "string", "required": True, "sensitive": True},
                "model_name": {"type": "string", "default": "gpt-4", "options": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]},
                "max_tokens": {"type": "integer", "min": 1, "max": 8000, "default": 4000},
                "temperature": {"type": "float", "min": 0.0, "max": 2.0, "default": 0.7},
                "auto_generation_enabled": {"type": "boolean", "default": True},
                "batch_processing_enabled": {"type": "boolean", "default": True},
                "quality_threshold": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.8},
                "content_moderation_enabled": {"type": "boolean", "default": True}
            },
            "database": {
                "url": {"type": "string", "required": True},
                "pool_size": {"type": "integer", "min": 1, "max": 100, "default": 10},
                "max_overflow": {"type": "integer", "min": 0, "max": 100, "default": 20},
                "pool_timeout": {"type": "integer", "min": 1, "max": 300, "default": 30},
                "pool_recycle": {"type": "integer", "min": 300, "max": 86400, "default": 3600},
                "echo": {"type": "boolean", "default": False},
                "backup_enabled": {"type": "boolean", "default": True},
                "backup_interval": {"type": "integer", "min": 1, "max": 168, "default": 24}
            },
            "cache": {
                "enabled": {"type": "boolean", "default": True},
                "redis_url": {"type": "string", "default": "redis://localhost:6379"},
                "default_ttl": {"type": "integer", "min": 60, "max": 86400, "default": 3600},
                "max_connections": {"type": "integer", "min": 1, "max": 100, "default": 10}
            },
            "analytics": {
                "enabled": {"type": "boolean", "default": True},
                "realtime_enabled": {"type": "boolean", "default": True},
                "export_enabled": {"type": "boolean", "default": True},
                "retention_days": {"type": "integer", "min": 1, "max": 365, "default": 90},
                "aggregation_interval": {"type": "integer", "min": 60, "max": 3600, "default": 300}
            },
            "scheduling": {
                "enabled": {"type": "boolean", "default": True},
                "max_concurrent_tasks": {"type": "integer", "min": 1, "max": 50, "default": 5},
                "task_timeout": {"type": "integer", "min": 300, "max": 7200, "default": 3600},
                "retry_attempts": {"type": "integer", "min": 0, "max": 10, "default": 3},
                "retry_delay": {"type": "integer", "min": 60, "max": 1800, "default": 300}
            },
            "storage": {
                "provider": {"type": "string", "options": ["local", "gcs", "s3"], "default": "local"},
                "local_path": {"type": "string", "default": "./storage"},
                "gcs_bucket": {"type": "string", "required_if": {"provider": "gcs"}},
                "s3_bucket": {"type": "string", "required_if": {"provider": "s3"}},
                "s3_region": {"type": "string", "required_if": {"provider": "s3"}},
                "max_file_size": {"type": "integer", "min": 1024, "max": 1073741824, "default": 104857600}
            },
            "notifications": {
                "enabled": {"type": "boolean", "default": True},
                "email_enabled": {"type": "boolean", "default": False},
                "webhook_enabled": {"type": "boolean", "default": False},
                "smtp_server": {"type": "string", "required_if": {"email_enabled": True}},
                "smtp_port": {"type": "integer", "min": 1, "max": 65535, "default": 587},
                "smtp_username": {"type": "string", "required_if": {"email_enabled": True}},
                "smtp_password": {"type": "string", "sensitive": True, "required_if": {"email_enabled": True}},
                "webhook_url": {"type": "string", "required_if": {"webhook_enabled": True}}
            },
            "monitoring": {
                "log_level": {"type": "string", "options": ["DEBUG", "INFO", "WARNING", "ERROR"], "default": "INFO"},
                "log_format": {"type": "string", "options": ["json", "text"], "default": "json"},
                "metrics_enabled": {"type": "boolean", "default": True},
                "health_check_interval": {"type": "integer", "min": 10, "max": 300, "default": 30},
                "performance_monitoring": {"type": "boolean", "default": True}
            }
        }
        
        return APIResponse(
            status="success",
            data={"schema": schema},
            message="Configuration schema retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving configuration schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config/status")
async def config_status():
    issues = settings.validate_configuration()
    return {"status": "ok" if not issues else "error", "issues": issues}
