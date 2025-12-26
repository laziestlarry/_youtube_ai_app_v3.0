"""
Backup and Recovery Manager
YouTube Income Commander v2.0
"""
import os
import json
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.config_file = "config/backup_config.json"
        self.load_config()
    
    def load_config(self):
        """Load backup configuration"""
        default_config = {
            "auto_backup": True,
            "backup_interval_hours": 24,
            "max_backups": 30,
            "include_outputs": True,
            "include_evidence": True,
            "include_databases": True,
            "include_config": True,
            "compression_level": 6
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            else:
                self.config = default_config
                self.save_config()
        except Exception:
            self.config = default_config
    
    def save_config(self):
        """Save backup configuration"""
        try:
            Path(self.config_file).parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save backup config: {e}")
    
    def create_backup(self, backup_name=None, include_outputs=None):
        """Create a complete system backup"""
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        print(f"🔄 Creating backup: {backup_name}")
        print(f"📁 Backup location: {backup_path}")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, 
                               compresslevel=self.config['compression_level']) as zipf:
                
                # Backup databases
                if self.config['include_databases']:
                    self._backup_databases(zipf)
                
                # Backup configuration
                if self.config['include_config']:
                    self._backup_config(zipf)
                
                # Backup outputs
                if include_outputs or self.config['include_outputs']:
                    self._backup_outputs(zipf)
                
                # Backup evidence
                if self.config['include_evidence']:
                    self._backup_evidence(zipf)
                
                # Add backup metadata
                self._add_backup_metadata(zipf, backup_name)
            
            # Verify backup
            backup_size = backup_path.stat().st_size
            backup_size_mb = backup_size / (1024 * 1024)
            
            print(f"✅ Backup created successfully")
            print(f"📊 Backup size: {backup_size_mb:.1f} MB")
            
            # Clean old backups
            self._cleanup_old_backups()
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def _backup_databases(self, zipf):
        """Backup database files"""
        print("   📊 Backing up databases...")
        
        db_files = [
            'youtube_projects.db',
            'revenue_tracker.db',
            'evidence_master.db'
        ]
        
        for db_file in db_files:
            if os.path.exists(db_file):
                # Create a backup copy to ensure consistency
                temp_backup = f"temp_{db_file}"
                try:
                    # Use SQLite backup API for consistency
                    source_conn = sqlite3.connect(db_file)
                    backup_conn = sqlite3.connect(temp_backup)
                    source_conn.backup(backup_conn)
                    source_conn.close()
                    backup_conn.close()
                    
                    # Add to zip
                    zipf.write(temp_backup, f"databases/{db_file}")
                    os.remove(temp_backup)
                    print(f"      ✅ {db_file}")
                    
                except Exception as e:
                    print(f"      ❌ {db_file}: {e}")
                    if os.path.exists(temp_backup):
                        os.remove(temp_backup)
    
    def _backup_config(self, zipf):
        """Backup configuration files"""
        print("   ⚙️ Backing up configuration...")
        
        if os.path.exists("config"):
            for root, dirs, files in os.walk("config"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = file_path.replace("\\", "/")
                    zipf.write(file_path, arc_path)
                    print(f"      ✅ {arc_path}")
    
    def _backup_outputs(self, zipf):
        """Backup output files"""
        print("   📁 Backing up outputs...")
        
        if os.path.exists("outputs"):
            file_count = 0
            for root, dirs, files in os.walk("outputs"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = file_path.replace("\\", "/")
                    zipf.write(file_path, arc_path)
                    file_count += 1
            print(f"      ✅ {file_count} output files")
    
    def _backup_evidence(self, zipf):
        """Backup evidence files"""
        print("   💰 Backing up evidence...")
        
        if os.path.exists("evidence"):
            file_count = 0
            for root, dirs, files in os.walk("evidence"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = file_path.replace("\\", "/")
                    zipf.write(file_path, arc_path)
                    file_count += 1
            print(f"      ✅ {file_count} evidence files")
    
    def _add_backup_metadata(self, zipf, backup_name):
        """Add backup metadata"""
        metadata = {
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "version": "2.0.0",
            "system": "YouTube Income Commander",
            "config": self.config,
            "file_count": len(zipf.namelist())
        }
        
        metadata_json = json.dumps(metadata, indent=2)
        zipf.writestr("backup_metadata.json", metadata_json)
    
    def _cleanup_old_backups(self):
        """Remove old backup files"""
        if self.config['max_backups'] <= 0:
            return
        
        backup_files = list(self.backup_dir.glob("backup_*.zip"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(backup_files) > self.config['max_backups']:
            old_backups = backup_files[self.config['max_backups']:]
            for old_backup in old_backups:
                try:
                    old_backup.unlink()
                    print(f"   🗑️ Removed old backup: {old_backup.name}")
                except Exception as e:
                    print(f"   ⚠️ Could not remove {old_backup.name}: {e}")
    
    def list_backups(self):
        """List available backups"""
        backup_files = list(self.backup_dir.glob("backup_*.zip"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not backup_files:
            print("📦 No backups found")
            return []
        
        print("📦 AVAILABLE BACKUPS")
        print("="*50)
        
        backups = []
        for backup_file in backup_files:
            try:
                stat = backup_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                created = datetime.fromtimestamp(stat.st_mtime)
                
                # Try to read metadata
                metadata = self._read_backup_metadata(backup_file)
                
                backup_info = {
                    "name": backup_file.stem,
                    "file": str(backup_file),
                    "size_mb": size_mb,
                    "created": created,
                    "metadata": metadata
                }
                
                backups.append(backup_info)
                
                print(f"📁 {backup_file.stem}")
                print(f"   📅 Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   📊 Size: {size_mb:.1f} MB")
                if metadata:
                    print(f"   📄 Files: {metadata.get('file_count', 'unknown')}")
                print()
                
            except Exception as e:
                print(f"❌ Error reading {backup_file.name}: {e}")
        
        return backups
    
    def _read_backup_metadata(self, backup_path):
        """Read metadata from backup file"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if "backup_metadata.json" in zipf.namelist():
                    metadata_content = zipf.read("backup_metadata.json")
                    return json.loads(metadata_content.decode('utf-8'))
        except Exception:
            pass
        return None
    
    def restore_backup(self, backup_name, restore_path=None):
        """Restore from backup"""
        
        if restore_path is None:
            restore_path = "."
        
        backup_file = self.backup_dir / f"{backup_name}.zip"
        
        if not backup_file.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        print(f"🔄 Restoring backup: {backup_name}")
        print(f"📁 Restore location: {restore_path}")
        
        # Confirm restoration
        confirm = input("⚠️ This will overwrite existing files. Continue? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("❌ Restore cancelled")
            return False
        
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Extract all files
                zipf.extractall(restore_path)
                
                # Read metadata
                metadata = self._read_backup_metadata(backup_file)
                
                print(f"✅ Backup restored successfully")
                if metadata:
                    print(f"📊 Restored {metadata.get('file_count', 'unknown')} files")
                    print(f"📅 Backup created: {metadata.get('created_at', 'unknown')}")
                
                return True
                
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def verify_backup(self, backup_name):
        """Verify backup integrity"""
        
        backup_file = self.backup_dir / f"{backup_name}.zip"
        
        if not backup_file.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        print(f"🔍 Verifying backup: {backup_name}")
        
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Test zip file integrity
                bad_files = zipf.testzip()
                
                if bad_files:
                    print(f"❌ Backup corrupted: {bad_files}")
                    return False
                
                # Check metadata
                metadata = self._read_backup_metadata(backup_file)
                if not metadata:
                    print("⚠️ No metadata found")
                
                file_count = len(zipf.namelist())
                print(f"✅ Backup verified successfully")
                print(f"📊 Files: {file_count}")
                
                if metadata:
                    expected_files = metadata.get('file_count', 0)
                    if file_count != expected_files:
                        print(f"⚠️ File count mismatch: expected {expected_files}, found {file_count}")
                
                return True
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def auto_backup_check(self):
        """Check if auto backup is needed"""
        
        if not self.config['auto_backup']:
            return False
        
        # Find most recent backup
        backup_files = list(self.backup_dir.glob("backup_*.zip"))
        
        if not backup_files:
            print("🔄 No previous backups found, creating initial backup...")
            return True
        
        # Check most recent backup age
        most_recent = max(backup_files, key=lambda x: x.stat().st_mtime)
        backup_age = datetime.now() - datetime.fromtimestamp(most_recent.stat().st_mtime)
        
        hours_since_backup = backup_age.total_seconds() / 3600
        
        if hours_since_backup >= self.config['backup_interval_hours']:
            print(f"🔄 Last backup was {hours_since_backup:.1f} hours ago, creating new backup...")
            return True
        
        return False
    
    def export_backup_config(self, filename=None):
        """Export backup configuration"""
        
        if filename is None:
            filename = f"backup_config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"✅ Backup configuration exported: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def import_backup_config(self, filename):
        """Import backup configuration"""
        
        try:
            with open(filename, 'r') as f:
                imported_config = json.load(f)
            
            # Validate configuration
            required_keys = ['auto_backup', 'backup_interval_hours', 'max_backups']
            for key in required_keys:
                if key not in imported_config:
                    print(f"❌ Invalid configuration: missing {key}")
                    return False
            
            self.config.update(imported_config)
            self.save_config()
            
            print(f"✅ Backup configuration imported: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False

def main():
    """Main backup manager interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Income Commander Backup Manager")
    parser.add_argument("action", choices=['create', 'list', 'restore', 'verify', 'config'], 
                       help="Action to perform")
    parser.add_argument("--name", type=str, help="Backup name")
    parser.add_argument("--include-outputs", action="store_true", help="Include output files")
    parser.add_argument("--auto-check", action="store_true", help="Check if auto backup needed")
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.action == "create":
        if args.auto_check and not manager.auto_backup_check():
            print("✅ No backup needed at this time")
            return
        
        backup_path = manager.create_backup(args.name, args.include_outputs)
        if backup_path:
            print(f"🎉 Backup completed: {backup_path}")
        else:
            print("❌ Backup failed")
    
    elif args.action == "list":
        manager.list_backups()
    
    elif args.action == "restore":
        if not args.name:
            print("❌ Backup name required for restore")
            return
        
        success = manager.restore_backup(args.name)
        if success:
            print("🎉 Restore completed successfully")
        else:
            print("❌ Restore failed")
    
    elif args.action == "verify":
        if not args.name:
            print("❌ Backup name required for verify")
            return
        
        success = manager.verify_backup(args.name)
        if success:
            print("🎉 Backup verification passed")
        else:
            print("❌ Backup verification failed")
    
    elif args.action == "config":
        print("📋 BACKUP CONFIGURATION")
        print("="*30)
        for key, value in manager.config.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()