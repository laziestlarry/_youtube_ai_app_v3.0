"""
System Health Check and Diagnostics
YouTube Income Commander v2.0
"""
import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from version_info import VERSION, SYSTEM_INFO, MODULES

class HealthChecker:
    def __init__(self):
        self.results = {
            "overall_status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "version": VERSION,
            "checks": {}
        }
    
    def run_all_checks(self):
        """Run comprehensive system health check"""
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🏥 SYSTEM HEALTH CHECK                                ║
║                                                              ║
║        YouTube Income Commander v{VERSION}                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        print("🔍 Running comprehensive system diagnostics...")
        print("="*60)
        
        # Run all checks
        self.check_python_environment()
        self.check_core_files()
        self.check_directories()
        self.check_configuration()
        self.check_databases()
        self.check_dependencies()
        self.check_permissions()
        self.check_disk_space()
        self.check_system_resources()
        
        # Determine overall status
        self.determine_overall_status()
        
        # Print summary
        self.print_health_summary()
        
        return self.results
    
    def check_python_environment(self):
        """Check Python environment"""
        print("\n🐍 PYTHON ENVIRONMENT")
        print("-" * 30)
        
        checks = {}
        
        # Python version
        version = sys.version_info
        if version >= (3, 8):
            print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
            checks["python_version"] = {"status": "pass", "value": f"{version.major}.{version.minor}.{version.micro}"}
        else:
            print(f"❌ Python version: {version.major}.{version.minor}.{version.micro} (3.8+ required)")
            checks["python_version"] = {"status": "fail", "value": f"{version.major}.{version.minor}.{version.micro}"}
        
        # Virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment: Active")
            checks["virtual_env"] = {"status": "pass", "value": "active"}
        else:
            print("⚠️ Virtual environment: Not active")
            checks["virtual_env"] = {"status": "warning", "value": "not_active"}
        
        # Pip availability
        try:
            import pip
            print("✅ Pip: Available")
            checks["pip"] = {"status": "pass", "value": "available"}
        except ImportError:
            print("❌ Pip: Not available")
            checks["pip"] = {"status": "fail", "value": "not_available"}
        
        self.results["checks"]["python_environment"] = checks
    
    def check_core_files(self):
        """Check core system files"""
        print("\n📁 CORE FILES")
        print("-" * 20)
        
        checks = {}
        
        for category, files in MODULES.items():
            category_checks = {}
            
            for file_path in files:
                if file_path.endswith('/'):
                    # Directory check
                    if os.path.exists(file_path):
                        print(f"✅ {file_path}")
                        category_checks[file_path] = {"status": "pass", "type": "directory"}
                    else:
                        print(f"❌ {file_path}")
                        category_checks[file_path] = {"status": "fail", "type": "directory"}
                else:
                    # File check
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        print(f"✅ {file_path} ({size} bytes)")
                        category_checks[file_path] = {"status": "pass", "type": "file", "size": size}
                    else:
                        print(f"❌ {file_path}")
                        category_checks[file_path] = {"status": "fail", "type": "file"}
            
            checks[category] = category_checks
        
        self.results["checks"]["core_files"] = checks
    
    def check_directories(self):
        """Check required directories"""
        print("\n📂 DIRECTORIES")
        print("-" * 20)
        
        required_dirs = [
            'outputs', 'outputs/scripts', 'outputs/audio', 'outputs/thumbnails',
            'outputs/videos', 'outputs/upload_packages',
            'evidence', 'evidence/bank_statements', 'evidence/transaction_history',
            'evidence/deposit_slips', 'evidence/account_summaries',
            'evidence/wire_confirmations', 'evidence/charts', 'evidence/reports',
            'config', 'logs', 'temp'
        ]
        
        checks = {}
        
        for directory in required_dirs:
            if os.path.exists(directory):
                file_count = len(os.listdir(directory)) if os.path.isdir(directory) else 0
                print(f"✅ {directory}/ ({file_count} files)")
                checks[directory] = {"status": "pass", "file_count": file_count}
            else:
                print(f"⚠️ {directory}/ (missing)")
                checks[directory] = {"status": "missing"}
                # Create missing directory
                try:
                    Path(directory).mkdir(parents=True, exist_ok=True)
                    print(f"   ✓ Created {directory}/")
                    checks[directory]["status"] = "created"
                except Exception as e:
                    print(f"   ❌ Failed to create: {e}")
                    checks[directory]["status"] = "fail"
        
        self.results["checks"]["directories"] = checks
    
    def check_configuration(self):
        """Check configuration files"""
        print("\n⚙️ CONFIGURATION")
        print("-" * 20)
        
        config_files = [
            'config/main_config.json',
            'config/database_config.json',
            'config/server_config.json'
        ]
        
        checks = {}
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    print(f"✅ {config_file} (valid JSON)")
                    checks[config_file] = {"status": "pass", "keys": len(config_data)}
                except json.JSONDecodeError as e:
                    print(f"❌ {config_file} (invalid JSON: {e})")
                    checks[config_file] = {"status": "fail", "error": str(e)}
            else:
                print(f"⚠️ {config_file} (missing)")
                checks[config_file] = {"status": "missing"}
        
        self.results["checks"]["configuration"] = checks
    
    def check_databases(self):
        """Check database files and integrity"""
        print("\n🗄️ DATABASES")
        print("-" * 15)
        
        databases = [
            'youtube_projects.db',
            'revenue_tracker.db',
            'evidence_master.db'
        ]
        
        checks = {}
        
        for db_file in databases:
            if os.path.exists(db_file):
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Check database integrity
                    cursor.execute("PRAGMA integrity_check")
                    integrity = cursor.fetchone()[0]
                    
                    # Get table count
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    if integrity == "ok":
                        print(f"✅ {db_file} ({table_count} tables)")
                        checks[db_file] = {"status": "pass", "tables": table_count, "integrity": "ok"}
                    else:
                        print(f"❌ {db_file} (integrity check failed)")
                        checks[db_file] = {"status": "fail", "integrity": integrity}
                        
                except Exception as e:
                    print(f"❌ {db_file} (error: {e})")
                    checks[db_file] = {"status": "fail", "error": str(e)}
            else:
                print(f"⚠️ {db_file} (missing)")
                checks[db_file] = {"status": "missing"}
        
        self.results["checks"]["databases"] = checks
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("\n📦 DEPENDENCIES")
        print("-" * 20)
        
        required_deps = [
            'fastapi', 'uvicorn', 'pydantic', 'matplotlib',
            'requests', 'jinja2', 'aiofiles', 'pandas',
            'numpy', 'pillow'
        ]
        
        optional_deps = [
            'psutil', 'opencv-python', 'ffmpeg-python'
        ]
        
        checks = {"required": {}, "optional": {}}
        
        print("Required dependencies:")
        for dep in required_deps:
            try:
                module = __import__(dep.replace('-', '_'))
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {dep} ({version})")
                checks["required"][dep] = {"status": "pass", "version": version}
            except ImportError:
                print(f"❌ {dep} (missing)")
                checks["required"][dep] = {"status": "missing"}
        
        print("\nOptional dependencies:")
        for dep in optional_deps:
            try:
                module = __import__(dep.replace('-', '_'))
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {dep} ({version})")
                checks["optional"][dep] = {"status": "pass", "version": version}
            except ImportError:
                print(f"⚠️ {dep} (optional)")
                checks["optional"][dep] = {"status": "optional"}
        
        self.results["checks"]["dependencies"] = checks
    
    def check_permissions(self):
        """Check file system permissions"""
        print("\n🔐 PERMISSIONS")
        print("-" * 18)
        
        checks = {}
        
        # Check write permissions in key directories
        test_dirs = ['outputs', 'evidence', 'config', 'logs', 'temp']
        
        for directory in test_dirs:
            if os.path.exists(directory):
                test_file = os.path.join(directory, 'permission_test.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    print(f"✅ {directory}/ (read/write)")
                    checks[directory] = {"status": "pass", "permissions": "read/write"}
                except Exception as e:
                    print(f"❌ {directory}/ (permission denied: {e})")
                    checks[directory] = {"status": "fail", "error": str(e)}
            else:
                print(f"⚠️ {directory}/ (missing)")
                checks[directory] = {"status": "missing"}
        
        # Check executable permissions
        executables = ['cli_launcher.py', 'quick_demo.py', 'install.py']
        for exe in executables:
            if os.path.exists(exe):
                if os.access(exe, os.R_OK):
                    print(f"✅ {exe} (readable)")
                    checks[exe] = {"status": "pass", "permissions": "readable"}
                else:
                    print(f"❌ {exe} (not readable)")
                    checks[exe] = {"status": "fail", "permissions": "not_readable"}
            else:
                checks[exe] = {"status": "missing"}
        
        self.results["checks"]["permissions"] = checks
    
    def check_disk_space(self):
        """Check available disk space"""
        print("\n💾 DISK SPACE")
        print("-" * 15)
        
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            
            total_gb = total // (1024**3)
            used_gb = used // (1024**3)
            free_gb = free // (1024**3)
            used_percent = (used / total) * 100
            
            print(f"Total: {total_gb} GB")
            print(f"Used: {used_gb} GB ({used_percent:.1f}%)")
            print(f"Free: {free_gb} GB")
            
            if free_gb >= 5:
                print("✅ Sufficient disk space")
                status = "pass"
            elif free_gb >= 1:
                print("⚠️ Low disk space")
                status = "warning"
            else:
                print("❌ Critical disk space")
                status = "critical"
            
            self.results["checks"]["disk_space"] = {
                "status": status,
                "total_gb": total_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
                "used_percent": used_percent
            }
            
        except Exception as e:
            print(f"❌ Could not check disk space: {e}")
            self.results["checks"]["disk_space"] = {"status": "fail", "error": str(e)}
    
    def check_system_resources(self):
        """Check system resources"""
        print("\n🖥️ SYSTEM RESOURCES")
        print("-" * 22)
        
        checks = {}
        
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"CPU Usage: {cpu_percent}%")
            
            if cpu_percent < 80:
                cpu_status = "pass"
            elif cpu_percent < 95:
                cpu_status = "warning"
            else:
                cpu_status = "critical"
            
            checks["cpu"] = {"status": cpu_status, "usage_percent": cpu_percent}
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available // (1024**3)
            
            print(f"Memory Usage: {memory_percent}%")
            print(f"Memory Available: {memory_available_gb} GB")
            
            if memory_percent < 80:
                memory_status = "pass"
            elif memory_percent < 95:
                memory_status = "warning"
            else:
                memory_status = "critical"
            
            checks["memory"] = {
                "status": memory_status,
                "usage_percent": memory_percent,
                "available_gb": memory_available_gb
            }
            
            # Process count
            process_count = len(psutil.pids())
            print(f"Running Processes: {process_count}")
            checks["processes"] = {"count": process_count}
            
            if cpu_status == "pass" and memory_status == "pass":
                print("✅ System resources OK")
            else:
                print("⚠️ System resources under stress")
            
        except ImportError:
            print("⚠️ psutil not available - install for detailed monitoring")
            checks["psutil"] = {"status": "missing"}
        except Exception as e:
            print(f"❌ Could not check system resources: {e}")
            checks["error"] = str(e)
        
        self.results["checks"]["system_resources"] = checks
    
    def determine_overall_status(self):
        """Determine overall system health status"""
        
        critical_failures = 0
        warnings = 0
        passes = 0
        
        def count_status(check_data):
            nonlocal critical_failures, warnings, passes
            
            if isinstance(check_data, dict):
                for key, value in check_data.items():
                    if isinstance(value, dict) and "status" in value:
                        status = value["status"]
                        if status in ["fail", "critical", "missing"]:
                            critical_failures += 1
                        elif status in ["warning", "optional"]:
                            warnings += 1
                        elif status in ["pass", "created"]:
                            passes += 1
                    else:
                        count_status(value)
        
        # Count all statuses
        for check_category in self.results["checks"].values():
            count_status(check_category)
        
        # Determine overall status
        if critical_failures == 0 and warnings <= 2:
            self.results["overall_status"] = "healthy"
        elif critical_failures <= 2 and warnings <= 5:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "critical"
        
        self.results["summary"] = {
            "passes": passes,
            "warnings": warnings,
            "failures": critical_failures,
            "total_checks": passes + warnings + critical_failures
        }
    
    def print_health_summary(self):
        """Print health check summary"""
        
        print("\n" + "="*60)
        print("📊 HEALTH CHECK SUMMARY")
        print("="*60)
        
        status = self.results["overall_status"]
        summary = self.results["summary"]
        
        # Status indicator
        if status == "healthy":
            print("🟢 SYSTEM STATUS: HEALTHY")
        elif status == "warning":
            print("🟡 SYSTEM STATUS: WARNING")
        else:
            print("🔴 SYSTEM STATUS: CRITICAL")
        
        print(f"\n📈 CHECK RESULTS:")
        print(f"   ✅ Passed: {summary['passes']}")
        print(f"   ⚠️ Warnings: {summary['warnings']}")
        print(f"   ❌ Failures: {summary['failures']}")
        print(f"   📊 Total: {summary['total_checks']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if status == "healthy":
            print("   • System is running optimally")
            print("   • All core components are functional")
            print("   • Ready for production use")
        
        elif status == "warning":
            print("   • System is functional but has minor issues")
            print("   • Consider addressing warnings for optimal performance")
            print("   • Monitor system resources")
            
            if summary['warnings'] > 0:
                print("   • Run: python install.py to fix missing components")
        
        else:
            print("   • System has critical issues that need attention")
            print("   • Some features may not work properly")
            print("   • Run: python install.py to reinstall system")
            print("   • Check file permissions and disk space")
        
        # Next steps
        print(f"\n🚀 NEXT STEPS:")
        if status == "healthy":
            print("   • Start using: python cli_launcher.py")
            print("   • Try the demo: python quick_demo.py")
            print("   • Access web interface: python cli_launcher.py server")
        else:
            print("   • Fix critical issues first")
            print("   • Re-run health check: python health_check.py")
            print("   • Contact support if issues persist")
        
        print("\n" + "="*60)
    
    def save_report(self, filename=None):
        """Save health check report to file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/health_check_{timestamp}.json"
        
        try:
            # Ensure logs directory exists
            Path("logs").mkdir(exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"\n💾 Health report saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"\n❌ Could not save report: {e}")
            return None

def run_quick_health_check():
    """Run a quick health check with minimal output"""
    
    print("🏥 Quick Health Check...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python version too old")
    
    # Check core files
    if not os.path.exists("cli_launcher.py"):
        issues.append("Core files missing")
    
    # Check directories
    if not os.path.exists("outputs"):
        issues.append("Output directories missing")
    
    # Check dependencies
    try:
        import fastapi
        import uvicorn
    except ImportError:
        issues.append("Core dependencies missing")
    
    if not issues:
        print("✅ System appears healthy")
        return True
    else:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   • {issue}")
        print("\nRun full health check: python health_check.py")
        return False

def main():
    """Main health check entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Income Commander Health Check")
    parser.add_argument("--quick", action="store_true", help="Run quick health check")
    parser.add_argument("--save", type=str, help="Save report to file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    if args.quick:
        return run_quick_health_check()
    
    # Run full health check
    checker = HealthChecker()
    results = checker.run_all_checks()
    
    # Save report if requested
    if args.save:
        checker.save_report(args.save)
    
    # Output JSON if requested
    if args.json:
        print("\n" + "="*60)
        print("JSON REPORT:")
        print("="*60)
        print(json.dumps(results, indent=2))
    
    return results["overall_status"] == "healthy"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)