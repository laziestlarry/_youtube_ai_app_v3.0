"""
Backup and Recovery Service
Automated data backup and recovery functionality
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import asyncio

from backend.core.config import settings

logger = logging.getLogger(__name__)

class BackupService:
    """Handle database and file backups."""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    async def create_database_backup(self) -> Dict[str, Any]:
        """Create a backup of the database."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            if settings.DATABASE_URL.startswith("sqlite"):
                # SQLite backup
                db_path = settings.DATABASE_URL.replace("sqlite:///", "")
                backup_path = self.backup_dir / f"database_backup_{timestamp}.db"
                
                if os.path.exists(db_path):
                    shutil.copy2(db_path, backup_path)
                    backup_size = os.path.getsize(backup_path)
                    
                    return {
                        "status": "success",
                        "backup_file": str(backup_path),
                        "backup_size_bytes": backup_size,
                        "timestamp": timestamp
                    }
                else:
                    return {"status": "error", "message": "Database file not found"}
            
            else:
                # PostgreSQL backup (requires pg_dump)
                backup_path = self.backup_dir / f"database_backup_{timestamp}.sql"
                
                # Run pg_dump command
                process = await asyncio.create_subprocess_exec(
                    "pg_dump", settings.DATABASE_URL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    with open(backup_path, 'wb') as f:
                        f.write(stdout)
                    
                    backup_size = os.path.getsize(backup_path)
                    
                    return {
                        "status": "success",
                        "backup_file": str(backup_path),
                        "backup_size_bytes": backup_size,
                        "timestamp": timestamp
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"pg_dump failed: {stderr.decode()}"
                    }
        
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_full_backup(self) -> Dict[str, Any]:
        """Create a complete backup including database and files."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            # Create database backup
            db_backup = await self.create_database_backup()
            
            # Create uploads backup if directory exists
            uploads_backup = None
            uploads_dir = Path(settings.UPLOAD_FOLDER)
            if uploads_dir.exists():
                backup_uploads_dir = self.backup_dir / f"uploads_backup_{timestamp}"
                shutil.copytree(uploads_dir, backup_uploads_dir)
                uploads_backup = {
                    "backup_dir": str(backup_uploads_dir),
                    "file_count": len(list(backup_uploads_dir.rglob("*")))
                }
            
            return {
                "status": "success",
                "timestamp": timestamp,
                "database_backup": db_backup,
                "uploads_backup": uploads_backup
            }
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*"):
                if backup_file.is_file():
                    stat = backup_file.stat()
                    backups.append({
                        "filename": backup_file.name,
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "type": "database" if backup_file.suffix in [".db", ".sql"] else "unknown"
                    })
            
            return sorted(backups, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_days: int = 30) -> Dict[str, Any]:
        """Remove backups older than specified days."""
        try:
            cutoff_date = datetime.utcnow().timestamp() - (keep_days * 24 * 60 * 60)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob("*"):
                if backup_file.is_file() and backup_file.stat().st_ctime < cutoff_date:
                    backup_file.unlink()
                    removed_count += 1
            
            return {
                "status": "success",
                "removed_count": removed_count,
                "keep_days": keep_days
            }
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {"status": "error", "message": str(e)}

# Global backup service instance
backup_service = BackupService()