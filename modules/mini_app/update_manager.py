"""
Update Manager for YouTube Income Commander
Handles system updates, patches, and version management
"""
import os
import json
import requests
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from version_info import VERSION, SYSTEM_INFO
import subprocess
import hashlib

class UpdateManager:
    def __init__(self):
        self.current_version = VERSION
        self.update_server = "https://api.youtube-income-commander.com"  # Placeholder
        self.update_dir = Path("updates")
        self.update_dir.mkdir(exist_ok=True)
        self.backup_before_update = True
        
    def check_for_updates(self, check_beta=False):
        """Check for available updates"""
        
        print("🔍 Checking for updates...")
        
        try:
            # In a real implementation, this would check a remote server
            # For now, we'll simulate update checking
            
            available_updates = self._simulate_update_check(check_beta)
            
            if not available_updates:
                print("✅ You have the latest version")
                return None
            
            print(f"🆕 Updates available:")
            for update in available_updates:
                print(f"   📦 Version {update['version']} - {update['description']}")
                print(f"      📅 Released: {update['release_date']}")
                print(f"      📊 Size: {update['size_mb']} MB")
                print()
            
            return available_updates
            
        except Exception as e:
            print(f"❌ Update check failed: {e}")
            return None
    
    def _simulate_update_check(self, check_beta=False):
        """Simulate update checking (replace with real API call)"""
        
        # Simulate available updates
        updates = []
        
        # Check if we're on an older version (for demo purposes)
        if self.current_version == "2.0.0":
            # No updates available for latest version
            pass
        else:
            # Simulate updates for older versions
            updates.append({
                "version": "2.0.1",
                "type": "patch",
                "description": "Bug fixes and performance improvements",
                "release_date": "2024-12-15",
                "size_mb": 15.2,
                "critical": False,
                "changelog": [
                    "Fixed database connection issues",
                    "Improved error handling",
                    "Enhanced backup system",
                    "Updated dependencies"
                ]
            })
        
        if check_beta:
            updates.append({
                "version": "2.1.0-beta",
                "type": "beta",
                "description": "AI voice cloning and advanced analytics",
                "release_date": "2024-12-20",
                "size_mb": 45.8,
                "critical": False,
                "changelog": [
                    "Added AI voice cloning",
                    "Advanced analytics dashboard",
                    "Multi-language support",
                    "Enhanced automation features"
                ]
            })
        
        return updates
    
    def download_update(self, version):
        """Download update package"""
        
        print(f"📥 Downloading update {version}...")
        
        try:
            # In real implementation, download from server
            # For now, simulate download
            
            update_file = self.update_dir / f"update_{version}.zip"
            
            # Simulate download progress
            import time
            for i in range(0, 101, 10):
                print(f"\r   Progress: {i}%", end="", flush=True)
                time.sleep(0.1)
            
            print(f"\n✅ Update downloaded: {update_file}")
            
            # Create a dummy update file for demonstration
            self._create_dummy_update_file(update_file, version)
            
            return str(update_file)
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def _create_dummy_update_file(self, update_file, version):
        """Create a dummy update file for demonstration"""
        
        update_data = {
            "version": version,
            "files": {
                "cli_launcher.py": "updated_content",
                "version_info.py": f"VERSION = '{version}'",
                "config/update_applied.json": json.dumps({
                    "version": version,
                    "applied_at": datetime.now().isoformat()
                })
            },
            "scripts": [
                "echo 'Applying database migrations...'",
                "echo 'Updating configuration files...'",
                "echo 'Clearing cache...'"
            ]
        }
        
        with zipfile.ZipFile(update_file, 'w') as zipf:
            zipf.writestr("update_manifest.json", json.dumps(update_data, indent=2))
            
            for file_path, content in update_data["files"].items():
                zipf.writestr(file_path, content)
    
    def verify_update(self, update_file):
        """Verify update package integrity"""
        
        print(f"🔍 Verifying update package...")
        
        try:
            with zipfile.ZipFile(update_file, 'r') as zipf:
                # Test zip integrity
                bad_files = zipf.testzip()
                if bad_files:
                    print(f"❌ Corrupted files: {bad_files}")
                    return False
                
                # Check for required files
                required_files = ["update_manifest.json"]
                for required_file in required_files:
                    if required_file not in zipf.namelist():
                        print(f"❌ Missing required file: {required_file}")
                        return False
                
                # Verify manifest
                manifest_content = zipf.read("update_manifest.json")
                manifest = json.loads(manifest_content.decode('utf-8'))
                
                if "version" not in manifest:
                    print("❌ Invalid manifest: missing version")
                    return False
                
                print("✅ Update package verified")
                return True
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def apply_update(self, update_file, force=False):
        """Apply update to system"""
        
        print(f"🔄 Applying update...")
        
        if not force:
            confirm = input("⚠️ This will update your system. Continue? (y/N): ")
            if confirm.lower() not in ['y', 'yes']:
                print("❌ Update cancelled")
                return False
        
        try:
            # Create backup before update
            if self.backup_before_update:
                print("📦 Creating backup before update...")
                from backup_manager import BackupManager
                backup_manager = BackupManager()
                backup_name = f"pre_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_path = backup_manager.create_backup(backup_name)
                if not backup_path:
                    print("❌ Backup failed, aborting update")
                    return False
            
            # Extract and apply update
            with zipfile.ZipFile(update_file, 'r') as zipf:
                # Read manifest
                manifest_content = zipf.read("update_manifest.json")
                manifest = json.loads(manifest_content.decode('utf-8'))
                
                print(f"📋 Applying update {manifest['version']}...")
                
                # Apply file updates
                if "files" in manifest:
                    for file_path, _ in manifest["files"].items():
                        if file_path in zipf.namelist():
                            # Create directory if needed
                            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                            
                            # Extract file
                            zipf.extract(file_path, ".")
                            print(f"   ✅ Updated: {file_path}")
                
                # Run update scripts
                if "scripts" in manifest:
                    print("🔧 Running update scripts...")
                    for script in manifest["scripts"]:
                        try:
                            result = subprocess.run(script, shell=True, capture_output=True, text=True)
                            if result.returncode == 0:
                                print(f"   ✅ {script}")
                            else:
                                print(f"   ⚠️ {script} (warning: {result.stderr})")
                        except Exception as e:
                            print(f"   ❌ {script} (error: {e})")
                
                # Update version info
                self._update_version_info(manifest["version"])
                
                print(f"✅ Update {manifest['version']} applied successfully")
                print("🔄 Please restart the application to complete the update")
                
                return True
                
        except Exception as e:
            print(f"❌ Update failed: {e}")
            print("🔄 You may need to restore from backup")
            return False
    
    def _update_version_info(self, new_version):
        """Update version information"""
        
        try:
            # Read current version file
            version_file = "version_info.py"
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    content = f.read()
                
                # Update version string
                updated_content = content.replace(
                    f'VERSION = "{self.current_version}"',
                    f'VERSION = "{new_version}"'
                )
                
                # Write updated content
                with open(version_file, 'w') as f:
                    f.write(updated_content)
                
                print(f"   ✅ Version updated to {new_version}")
                
        except Exception as e:
            print(f"   ⚠️ Could not update version info: {e}")
    
    def rollback_update(self, backup_name=None):
        """Rollback to previous version"""
        
        print("🔄 Rolling back update...")
        
        try:
            from backup_manager import BackupManager
            backup_manager = BackupManager()
            
            if backup_name is None:
                # Find most recent pre-update backup
                backups = backup_manager.list_backups()
                pre_update_backups = [b for b in backups if "pre_update" in b["name"]]
                
                if not pre_update_backups:
                    print("❌ No pre-update backup found")
                    return False
                
                # Use most recent pre-update backup
                backup_name = pre_update_backups[0]["name"]
                print(f"📦 Using backup: {backup_name}")
            
            # Restore backup
            success = backup_manager.restore_backup(backup_name)
            
            if success:
                print("✅ Rollback completed successfully")
                print("🔄 Please restart the application")
                return True
            else:
                print("❌ Rollback failed")
                return False
                
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def check_system_compatibility(self, target_version):
        """Check if system is compatible with target version"""
        
        print(f"🔍 Checking compatibility for version {target_version}...")
        
        compatibility_issues = []
        
        # Check Python version
        import sys
        python_version = sys.version_info
        if python_version < (3, 8):
            compatibility_issues.append("Python 3.8+ required")
        
        # Check disk space
        try:
            import shutil
            _, _, free = shutil.disk_usage(".")
            free_gb = free // (1024**3)
            if free_gb < 1:
                compatibility_issues.append("Insufficient disk space (1GB required)")
        except:
            compatibility_issues.append("Could not check disk space")
        
        # Check dependencies
        required_modules = ['fastapi', 'uvicorn', 'requests']
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                compatibility_issues.append(f"Missing dependency: {module}")
        
        if compatibility_issues:
            print("❌ Compatibility issues found:")
            for issue in compatibility_issues:
                print(f"   • {issue}")
            return False
        else:
            print("✅ System is compatible")
            return True
    
    def get_update_history(self):
        """Get update history"""
        
        history_file = "config/update_history.json"
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            if history:
                print("📋 UPDATE HISTORY")
                print("="*30)
                for update in reversed(history):
                    print(f"📦 Version {update['version']}")
                    print(f"   📅 Applied: {update['applied_at']}")
                    print(f"   👤 Applied by: {update.get('applied_by', 'unknown')}")
                    if 'notes' in update:
                        print(f"   📝 Notes: {update['notes']}")
                    print()
            else:
                print("📋 No update history found")
            
            return history
            
        except Exception as e:
            print(f"❌ Could not read update history: {e}")
            return []
    
    def record_update(self, version, notes=None):
        """Record update in history"""
        
        history_file = "config/update_history.json"
        
        try:
            # Load existing history
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Add new update record
            update_record = {
                "version": version,
                "applied_at": datetime.now().isoformat(),
                "applied_by": os.getenv("USER", "unknown"),
                "previous_version": self.current_version
            }
            
            if notes:
                update_record["notes"] = notes
            
            history.append(update_record)
            
            # Save updated history
            Path(history_file).parent.mkdir(exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
        except Exception as e:
            print(f"⚠️ Could not record update: {e}")

def main():
    """Main update manager interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Income Commander Update Manager")
    parser.add_argument("action", choices=['check', 'download', 'apply', 'rollback', 'history'], 
                       help="Action to perform")
    parser.add_argument("--version", type=str, help="Specific version to target")
    parser.add_argument("--beta", action="store_true", help="Include beta versions")
    parser.add_argument("--force", action="store_true", help="Force update without confirmation")
    parser.add_argument("--backup", type=str, help="Backup name for rollback")
    
    args = parser.parse_args()
    
    manager = UpdateManager()
    
    if args.action == "check":
        updates = manager.check_for_updates(args.beta)
        if updates:
            print(f"\n💡 To download and apply updates:")
            print(f"   python update_manager.py download --version <version>")
            print(f"   python update_manager.py apply --version <version>")
    
    elif args.action == "download":
        if not args.version:
            print("❌ Version required for download")
            return
        
        # Check compatibility first
        if not manager.check_system_compatibility(args.version):
            print("❌ System not compatible with target version")
            return
        
        update_file = manager.download_update(args.version)
        if update_file:
            # Verify download
            if manager.verify_update(update_file):
                print(f"🎉 Update ready to apply: {update_file}")
                print(f"   python update_manager.py apply --version {args.version}")
            else:
                print("❌ Update verification failed")
    
    elif args.action == "apply":
        if not args.version:
            print("❌ Version required for apply")
            return
        
        update_file = manager.update_dir / f"update_{args.version}.zip"
        
        if not update_file.exists():
            print(f"❌ Update file not found: {update_file}")
            print(f"   Download first: python update_manager.py download --version {args.version}")
            return
        
        success = manager.apply_update(str(update_file), args.force)
        if success:
            manager.record_update(args.version)
            print("🎉 Update applied successfully")
        else:
            print("❌ Update failed")
    
    elif args.action == "rollback":
        success = manager.rollback_update(args.backup)
        if success:
            print("🎉 Rollback completed successfully")
        else:
            print("❌ Rollback failed")
    
    elif args.action == "history":
        manager.get_update_history()

if __name__ == "__main__":
    main()