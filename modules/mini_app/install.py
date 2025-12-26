"""
Installation Script for YouTube Income Commander
Handles setup, dependency installation, and configuration
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class YouTubeIncomeCommanderInstaller:
    def __init__(self):
        self.version = "2.0.0"
        self.project_name = "YouTube Income Commander"
        self.required_python = (3, 8)
        
    def check_python_version(self):
        """Check if Python version meets requirements"""
        current_version = sys.version_info[:2]
        if current_version < self.required_python:
            print(f"❌ Python {self.required_python[0]}.{self.required_python[1]}+ required")
            print(f"   Current version: {current_version[0]}.{current_version[1]}")
            return False
        
        print(f"✅ Python {current_version[0]}.{current_version[1]} detected")
        return True
    
    def create_directories(self):
        """Create all necessary directories"""
        directories = [
            # Output directories
            'outputs/scripts',
            'outputs/audio',
            'outputs/thumbnails', 
            'outputs/videos',
            'outputs/upload_packages',
            
            # Evidence directories
            'evidence/bank_statements',
            'evidence/transaction_history',
            'evidence/deposit_slips',
            'evidence/account_summaries',
            'evidence/wire_confirmations',
            'evidence/charts',
            'evidence/reports',
            'evidence/verifications',
            'evidence/exports',
            'evidence/package_summaries',
            
            # Backend directories
            'backend/uploads',
            'backend/audio',
            'backend/images',
            
            # Frontend directories (if needed)
            'frontend/public',
            'frontend/src',
            
            # Configuration
            'config',
            'logs',
            'temp'
        ]
        
        print("📁 Creating directory structure...")
        created_count = 0
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                print(f"   ✓ {directory}")
                created_count += 1
            except Exception as e:
                print(f"   ❌ {directory}: {str(e)}")
        
        print(f"✅ Created {created_count}/{len(directories)} directories")
        return created_count == len(directories)
    
    def install_dependencies(self):
        """Install Python dependencies"""
        dependencies = [
            'fastapi==0.104.1',
            'uvicorn[standard]==0.24.0',
            'pydantic==2.5.0',
            'matplotlib==3.8.2',
            'requests==2.31.0',
            'python-multipart==0.0.6',
            'jinja2==3.1.2',
            'aiofiles==23.2.1',
            'pandas==2.1.4',
            'numpy==1.26.2',
            'pillow==10.1.0'
        ]
        
        print("📦 Installing Python dependencies...")
        
        # Create requirements.txt
        with open('requirements.txt', 'w') as f:
            for dep in dependencies:
                f.write(f"{dep}\n")
        
        print("   ✓ requirements.txt created")
        
        # Install dependencies
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Dependency installation failed: {e}")
            return False
    
    def create_configuration(self):
        """Create configuration files"""
        
        # Main configuration
        config = {
            'version': self.version,
            'project_name': self.project_name,
            'installation_date': datetime.now().isoformat(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'directories_created': True,
            'dependencies_installed': True,
            'database_initialized': False,
            'web_server_configured': True,
            'settings': {
                'default_bank': 'Chase Bank',
                'default_currency': 'USD',
                'date_format': '%Y-%m-%d',
                'output_quality': 'high',
                'auto_backup': True,
                'debug_mode': False
            }
        }
        
        with open('config/main_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Database configuration
        db_config = {
            'databases': {
                'main': 'youtube_projects.db',
                'revenue': 'revenue_tracker.db', 
                'evidence': 'evidence_master.db'
            },
            'backup_interval': 24,  # hours
            'max_backups': 30,
            'auto_vacuum': True
        }
        
        with open('config/database_config.json', 'w') as f:
            json.dump(db_config, f, indent=2)
        
        # Server configuration
        server_config = {
            'host': '127.0.0.1',
            'port': 8000,
            'reload': True,
            'debug': False,
            'cors_origins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
            'max_upload_size': 100 * 1024 * 1024,  # 100MB
            'allowed_file_types': [
                'image/jpeg', 'image/png', 'image/gif',
                'video/mp4', 'video/quicktime',
                'application/pdf', 'text/plain'
            ]
        }
        
        with open('config/server_config.json', 'w') as f:
            json.dump(server_config, f, indent=2)
        
        print("✅ Configuration files created")
        return True
    
    def initialize_databases(self):
        """Initialize SQLite databases"""
        
        databases = [
            ('youtube_projects.db', self.create_projects_schema),
            ('revenue_tracker.db', self.create_revenue_schema),
            ('evidence_master.db', self.create_evidence_schema)
        ]
        
        print("🗄️ Initializing databases...")
        
        for db_name, schema_func in databases:
            try:
                schema_func(db_name)
                print(f"   ✓ {db_name}")
            except Exception as e:
                print(f"   ❌ {db_name}: {str(e)}")
                return False
        
        print("✅ Databases initialized")
        return True
    
    def create_projects_schema(self, db_path):
        """Create projects database schema"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                niche TEXT,
                revenue_potential REAL,
                status TEXT DEFAULT 'active',
                script_path TEXT,
                audio_path TEXT,
                thumbnail_path TEXT,
                video_path TEXT,
                upload_package_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS video_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                expected_views INTEGER,
                status TEXT DEFAULT 'draft',
                metadata TEXT,
                tags TEXT,
                script TEXT,
                thumbnail_path TEXT,
                audio_path TEXT,
                youtube_id TEXT UNIQUE,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_revenue_schema(self, db_path):
        """Create revenue database schema"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS revenue_streams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                stream_type TEXT,
                platform TEXT,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                revenue_stream_id INTEGER,
                bank_name TEXT,
                transaction_type TEXT,
                amount REAL,
                description TEXT,
                transaction_date TIMESTAMP,
                reference_number TEXT,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (revenue_stream_id) REFERENCES revenue_streams (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_evidence_schema(self, db_path):
        """Create evidence database schema"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS evidence_packages (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                account_holder TEXT,
                bank_name TEXT,
                total_revenue REAL,
                evidence_count INTEGER,
                package_date TIMESTAMP,
                verification_code TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS evidence_files (
                id TEXT PRIMARY KEY,
                package_id TEXT,
                file_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                checksum TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (package_id) REFERENCES evidence_packages (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_startup_scripts(self):
        """Create convenient startup scripts"""
        
        # Windows batch file
        windows_script = '''@echo off
echo Starting YouTube Income Commander...
python cli_launcher.py
pause
'''
        
        with open('start_windows.bat', 'w') as f:
            f.write(windows_script)
        
        # Unix shell script
        unix_script = '''#!/bin/bash
echo "Starting YouTube Income Commander..."
python3 cli_launcher.py
'''
        
        with open('start_unix.sh', 'w') as f:
            f.write(unix_script)
        
        # Make Unix script executable
        try:
            os.chmod('start_unix.sh', 0o755)
        except:
            pass  # Windows doesn't support chmod
        
        print("✅ Startup scripts created")
        return True
    
    def run_installation(self):
        """Run complete installation process"""
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🚀 YOUTUBE INCOME COMMANDER INSTALLER                 ║
║                                                              ║
║        Version {self.version:<10}                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        print("🔧 Starting installation process...")
        print("="*50)
        
        # Step 1: Check Python version
        if not self.check_python_version():
            return False
        
        # Step 2: Create directories
        if not self.create_directories():
            print("❌ Directory creation failed")
            return False
        
        # Step 3: Install dependencies
        print("\n📦 Installing dependencies (this may take a few minutes)...")
        if not self.install_dependencies():
            print("❌ Dependency installation failed")
            return False
        
        # Step 4: Create configuration
        if not self.create_configuration():
            print("❌ Configuration creation failed")
            return False
        
        # Step 5: Initialize databases
        if not self.initialize_databases():
            print("❌ Database initialization failed")
            return False
        
        # Step 6: Create startup scripts
        if not self.create_startup_scripts():
            print("❌ Startup script creation failed")
            return False
        
        # Installation complete
        self.show_completion_message()
        return True
    
    def show_completion_message(self):
        """Show installation completion message"""
        
        print("\n" + "="*60)
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print(f"\n✅ {self.project_name} v{self.version} is ready to use!")
        
        print(f"\n🚀 QUICK START:")
        print("-" * 20)
        print("1. Run: python cli_launcher.py")
        print("2. Or use: python quick_demo.py")
        print("3. Or double-click: start_windows.bat (Windows)")
        print("4. Or run: ./start_unix.sh (Linux/Mac)")
        
        print(f"\n🌐 WEB INTERFACE:")
        print("-" * 20)
        print("1. Run: python cli_launcher.py")
        print("2. Choose 'server' option")
        print("3. Visit: http://127.0.0.1:8000")
        
        print(f"\n📁 DIRECTORY STRUCTURE:")
        print("-" * 25)
        print("• outputs/     - Generated content")
        print("• evidence/    - Revenue documentation")
        print("• config/      - Configuration files")
        print("• logs/        - System logs")
        print("• backend/     - API server files")
        
        print(f"\n🎯 MAIN FEATURES:")
        print("-" * 20)
        print("• Complete video production pipeline")
        print("• Revenue tracking and documentation")
        print("• Professional bank evidence generation")
        print("• Comprehensive evidence packages")
        print("• Web-based interface")
        print("• Analytics and reporting")
        
        print(f"\n💡 NEXT STEPS:")
        print("-" * 15)
        print("1. Run the quick demo to test all features")
        print("2. Create your first video project")
        print("3. Generate revenue documentation")
        print("4. Explore the web interface")
        
        print(f"\n📞 SUPPORT:")
        print("-" * 12)
        print("• Check system status: python cli_launcher.py status")
        print("• Run diagnostics: python quick_demo.py")
        print("• View logs in: logs/ directory")
        
        print("\n" + "="*60)
        print("🚀 Ready to start generating revenue content!")
        print("="*60)

def main():
    """Main installation entry point"""
    
    installer = YouTubeIncomeCommanderInstaller()
    
    print("Welcome to YouTube Income Commander Installation!")
    print("This will set up everything you need to get started.")
    
    confirm = input("\nProceed with installation? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        success = installer.run_installation()
        
        if success:
            print("\n🎉 Installation successful!")
            
            # Ask if user wants to run demo
            demo = input("\nRun quick demo now? (y/N): ").strip().lower()
            if demo in ['y', 'yes']:
                try:
                    from quick_demo import run_quick_demo
                    run_quick_demo()
                except ImportError:
                    print("Demo not available, but installation was successful!")
        else:
            print("\n❌ Installation failed!")
            print("Please check the error messages above and try again.")
    else:
        print("Installation cancelled.")

if __name__ == "__main__":
    main()