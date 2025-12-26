#!/usr/bin/env python3
"""
CLI Launcher - Main entry point for YouTube Income Commander
Provides unified interface for all tools and pipelines
"""
import os
import sys
import subprocess
from pathlib import Path
import json
from datetime import datetime

class YouTubeIncomeCommanderCLI:
    def __init__(self):
        self.version = "2.0.0"
        self.tools = {
            "pipeline": "Complete Sequential Pipeline",
            "revenue": "Revenue Tracker & Evidence Generator", 
            "bank": "Bank Evidence Generator",
            "evidence": "Evidence Master (Complete Package)",
            "server": "Web Server (FastAPI)",
            "ideas": "Idea Generator",
            "scripts": "Script Generator",
            "thumbnails": "Thumbnail Generator"
        }
    
    def show_banner(self):
        """Display application banner"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🚀 YOUTUBE INCOME COMMANDER v{self.version}                    ║
║                                                              ║
║        Complete Revenue Generation & Documentation System    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def show_main_menu(self):
        """Display main menu"""
        print("\n📋 AVAILABLE TOOLS:")
        print("="*50)
        
        for key, description in self.tools.items():
            print(f"{key:12} - {description}")
        
        print("\n🔧 SYSTEM COMMANDS:")
        print("="*50)
        print("setup       - Initial system setup")
        print("status      - Check system status")
        print("update      - Update system")
        print("help        - Show detailed help")
        print("exit        - Exit application")
    
    def run_pipeline(self):
        """Run complete sequential pipeline"""
        try:
            from complete_sequential_pipeline import CompleteYouTubePipeline
            
            pipeline = CompleteYouTubePipeline()
            
            print("\n🎬 COMPLETE YOUTUBE PIPELINE")
            print("="*40)
            
            title = input("Video Title: ").strip()
            if not title:
                title = "How I Made $10,000 in 30 Days Online"
            
            niche = input("Niche (crypto/finance/business): ").strip().lower()
            if niche not in ['crypto', 'finance', 'business']:
                niche = 'finance'
            
            revenue_potential = input("Revenue Potential ($): ").strip()
            try:
                revenue_potential = float(revenue_potential)
            except:
                revenue_potential = 5000.0
            
            result = pipeline.run_complete_pipeline(title, niche, revenue_potential)
            
            if result['success']:
                print(f"\n✅ Pipeline completed successfully!")
                print(f"📋 Project ID: {result['project_id']}")
            else:
                print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")
                
        except ImportError:
            print("❌ Pipeline module not found. Please check installation.")
        except Exception as e:
            print(f"❌ Error running pipeline: {str(e)}")
    
    def run_revenue_tracker(self):
        """Run revenue tracker"""
        try:
            from revenue_tracker import main as revenue_main
            revenue_main()
        except ImportError:
            print("❌ Revenue tracker module not found.")
        except Exception as e:
            print(f"❌ Error running revenue tracker: {str(e)}")
    
    def run_bank_generator(self):
        """Run bank evidence generator"""
        try:
            from bank_evidence_generator import main as bank_main
            bank_main()
        except ImportError:
            print("❌ Bank generator module not found.")
        except Exception as e:
            print(f"❌ Error running bank generator: {str(e)}")
    
    def run_evidence_master(self):
        """Run evidence master"""
        try:
            from evidence_master import main as evidence_main
            evidence_main()
        except ImportError:
            print("❌ Evidence master module not found.")
        except Exception as e:
            print(f"❌ Error running evidence master: {str(e)}")
    
    def run_web_server(self):
        """Run FastAPI web server"""
        try:
            print("🌐 Starting web server...")
            print("Server will be available at: http://127.0.0.1:8000")
            print("API Documentation: http://127.0.0.1:8000/docs")
            print("Press Ctrl+C to stop the server")
            
            # Check if we're in the backend directory
            if os.path.exists("main.py"):
                subprocess.run(["uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"])
            elif os.path.exists("backend/main.py"):
                os.chdir("backend")
                subprocess.run(["uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"])
            else:
                print("❌ FastAPI server files not found. Please check installation.")
                
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except FileNotFoundError:
            print("❌ uvicorn not found. Please install: pip install uvicorn")
        except Exception as e:
            print(f"❌ Error starting server: {str(e)}")
    
    def run_idea_generator(self):
        """Run idea generator"""
        try:
            from backend.idea_generator import generate_ideas
            
            print("\n💡 IDEA GENERATOR")
            print("="*30)
            
            category = input("Category (tech/finance/lifestyle): ").strip()
            if not category:
                category = "finance"
            
            count = input("Number of ideas (default 5): ").strip()
            try:
                count = int(count)
            except:
                count = 5
            
            ideas = generate_ideas(category, count)
            
            print(f"\n🎯 GENERATED IDEAS ({category.upper()}):")
            print("-" * 40)
            
            for i, idea in enumerate(ideas, 1):
                if isinstance(idea, dict):
                    print(f"{i}. {idea['title']}")
                    print(f"   Expected Views: {idea.get('expected_views', 'N/A')}")
                    print(f"   Revenue Potential: ${idea.get('revenue_potential', 0)}")
                else:
                    print(f"{i}. {idea}")
                print()
                
        except ImportError:
            print("❌ Idea generator module not found.")
        except Exception as e:
            print(f"❌ Error running idea generator: {str(e)}")
    
    def setup_system(self):
        """Initial system setup"""
        print("\n🔧 SYSTEM SETUP")
        print("="*30)
        
        # Create necessary directories
        directories = [
            'outputs/scripts',
            'outputs/audio', 
            'outputs/thumbnails',
            'outputs/videos',
            'outputs/upload_packages',
            'evidence/bank_statements',
            'evidence/transaction_history',
            'evidence/deposit_slips',
            'evidence/account_summaries',
            'evidence/wire_confirmations',
            'evidence/charts',
            'evidence/reports',
            'evidence/verifications',
            'evidence/exports',
            'evidence/package_summaries'
        ]
        
        print("📁 Creating directories...")
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"   ✓ {directory}")
        
        # Check Python dependencies
        print("\n📦 Checking dependencies...")
        required_packages = [
            'fastapi',
            'uvicorn',
            'sqlite3',
            'matplotlib',
            'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✓ {package}")
            except ImportError:
                print(f"   ❌ {package} (missing)")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Run: pip install " + " ".join(missing_packages))
        else:
            print("\n✅ All dependencies satisfied!")
        
        # Create config file
        config = {
            'version': self.version,
            'setup_date': datetime.now().isoformat(),
            'directories_created': len(directories),
            'status': 'configured'
        }
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ System setup completed!")
    
    def check_status(self):
        """Check system status"""
        print("\n📊 SYSTEM STATUS")
        print("="*30)
        
        # Check config
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
            print(f"✅ Configuration: v{config.get('version', 'unknown')}")
            print(f"📅 Setup Date: {config.get('setup_date', 'unknown')[:10]}")
        else:
            print("❌ Configuration: Not found (run 'setup')")
        
        # Check directories
        critical_dirs = ['outputs', 'evidence']
        for directory in critical_dirs:
            if os.path.exists(directory):
                print(f"✅ Directory {directory}: OK")
            else:
                print(f"❌ Directory {directory}: Missing")
        
        # Check databases
        databases = ['youtube_projects.db', 'revenue_tracker.db', 'evidence_master.db']
        for db in databases:
            if os.path.exists(db):
                print(f"✅ Database {db}: OK")
            else:
                print(f"⚠️  Database {db}: Will be created on first use")
        
        # Check modules
        modules = ['complete_sequential_pipeline', 'revenue_tracker', 'evidence_master']
        for module in modules:
            try:
                __import__(module)
                print(f"✅ Module {module}: OK")
            except ImportError:
                print(f"❌ Module {module}: Not found")
    
    def show_help(self):
        """Show detailed help"""
        print(f"""
🔍 YOUTUBE INCOME COMMANDER v{self.version} - DETAILED HELP
{'='*60}

TOOL DESCRIPTIONS:
{'='*60}

pipeline    - Complete Sequential Pipeline
              Generates script → audio → thumbnail → video → upload package
              Perfect for end-to-end video production

revenue     - Revenue Tracker & Evidence Generator  
              Track income streams, generate bank evidence, create charts
              Includes tax reporting and analytics

bank        - Bank Evidence Generator
              Create realistic bank statements, wire confirmations, deposit slips
              Professional financial documentation

evidence    - Evidence Master (Complete Package)
              Combines revenue tracking with bank evidence generation
              Creates comprehensive documentation packages

server      - Web Server (FastAPI)
              Starts the web interface for browser-based access
              Includes API documentation and interactive tools

ideas       - Idea Generator
              Generate video ideas based on category and trends
              Includes revenue potential estimates

WORKFLOW RECOMMENDATIONS:
{'='*60}

For Complete Video Production:
1. Run 'pipeline' to create full video package
2. Use 'evidence' to document revenue results
3. Run 'server' for web-based management

For Revenue Documentation:
1. Use 'revenue' to track income streams
2. Run 'bank' to generate supporting documents
3. Use 'evidence' for complete packages

For Development/Testing:
1. Run 'setup' for initial configuration
2. Use 'status' to verify system health
3. Run 'server' for web interface testing

GETTING STARTED:
{'='*60}
1. Run: python cli_launcher.py setup
2. Choose a tool from the main menu
3. Follow the interactive prompts
4. Check outputs in respective directories

SUPPORT:
{'='*60}
• Check 'status' for system health
• Verify all directories exist
• Ensure Python dependencies are installed
• Review generated files in outputs/ and evidence/

{'='*60}
        """)
    
    def run(self):
        """Main application loop"""
        self.show_banner()
        
        while True:
            self.show_main_menu()
            
            choice = input("\n🎯 Choose a tool or command: ").strip().lower()
            
            if choice == 'pipeline':
                self.run_pipeline()
            
            elif choice == 'revenue':
                self.run_revenue_tracker()
            
            elif choice == 'bank':
                self.run_bank_generator()
            
            elif choice == 'evidence':
                self.run_evidence_master()
            
            elif choice == 'server':
                self.run_web_server()
            
            elif choice == 'ideas':
                self.run_idea_generator()
            
            elif choice == 'setup':
                self.setup_system()
            
            elif choice == 'status':
                self.check_status()
            
            elif choice == 'help':
                self.show_help()
            
            elif choice in ['exit', 'quit', 'q']:
                print("\n👋 Thank you for using YouTube Income Commander!")
                print("🚀 Keep creating and earning!")
                break
            
            else:
                print(f"❌ Unknown command: {choice}")
                print("💡 Type 'help' for detailed information")
            
            input("\n⏸️  Press Enter to continue...")

def main():
    """Entry point"""
    try:
        cli = YouTubeIncomeCommanderCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("💡 Please report this issue if it persists")

if __name__ == "__main__":
    main()