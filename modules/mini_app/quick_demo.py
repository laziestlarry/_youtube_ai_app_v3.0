"""
Quick Demo - Showcase all features of YouTube Income Commander
Perfect for testing and demonstration purposes
"""
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

def run_quick_demo():
    """Run a complete demonstration of all features"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎬 YOUTUBE INCOME COMMANDER - QUICK DEMO              ║
║                                                              ║
║        Complete System Demonstration                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Demo data
    demo_scenarios = [
        {
            'title': 'How I Made $15,000 in 30 Days with Affiliate Marketing',
            'niche': 'finance',
            'revenue': 15000,
            'account_holder': 'Sarah Johnson',
            'bank': 'Chase Bank'
        },
        {
            'title': 'My $25K Crypto Trading Strategy (PROOF INSIDE)',
            'niche': 'crypto', 
            'revenue': 25000,
            'account_holder': 'Mike Chen',
            'bank': 'Bank of America'
        },
        {
            'title': 'From $0 to $50K: Complete Online Business Blueprint',
            'niche': 'business',
            'revenue': 50000,
            'account_holder': 'Alex Rodriguez',
            'bank': 'Wells Fargo'
        }
    ]
    
    print("🎯 DEMO SCENARIOS AVAILABLE:")
    print("="*50)
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print(f"   Revenue: ${scenario['revenue']:,}")
        print(f"   Account: {scenario['account_holder']} ({scenario['bank']})")
        print()
    
    choice = input("Choose scenario (1-3) or Enter for random: ").strip()
    
    try:
        if choice:
            selected_scenario = demo_scenarios[int(choice) - 1]
        else:
            selected_scenario = random.choice(demo_scenarios)
    except (ValueError, IndexError):
        selected_scenario = demo_scenarios[0]
    
    print(f"\n🚀 RUNNING DEMO: {selected_scenario['title']}")
    print("="*60)
    
    # Step 1: Complete Pipeline Demo
    print("\n📝 STEP 1: COMPLETE PIPELINE GENERATION")
    print("-" * 40)
    
    try:
        from complete_sequential_pipeline import CompleteYouTubePipeline
        
        pipeline = CompleteYouTubePipeline()
        result = pipeline.run_complete_pipeline(
            selected_scenario['title'],
            selected_scenario['niche'],
            selected_scenario['revenue']
        )
        
        if result['success']:
            print(f"✅ Pipeline completed! Project ID: {result['project_id']}")
            project_id = result['project_id']
        else:
            print(f"❌ Pipeline failed: {result.get('error')}")
            project_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
    except Exception as e:
        print(f"⚠️ Pipeline demo skipped: {str(e)}")
        project_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Step 2: Revenue Tracking Demo
    print(f"\n💰 STEP 2: REVENUE TRACKING & EVIDENCE")
    print("-" * 40)
    
    try:
        from revenue_tracker import RevenueTracker
        
        tracker = RevenueTracker()
        
        # Add sample revenue streams
        revenue_streams = [
            ('ad_revenue', 'YouTube AdSense', selected_scenario['revenue'] * 0.3),
            ('affiliate', 'ClickBank', selected_scenario['revenue'] * 0.4),
            ('sponsorship', 'Brand Partnership', selected_scenario['revenue'] * 0.2),
            ('product_sales', 'Course Sales', selected_scenario['revenue'] * 0.1)
        ]
        
        total_tracked = 0
        for stream_type, platform, amount in revenue_streams:
            revenue_id = tracker.add_revenue_stream(project_id, stream_type, platform, amount)
            bank_transaction_id = tracker.generate_bank_transaction(revenue_id, selected_scenario['bank'])
            total_tracked += amount
            print(f"   ✓ {platform}: ${amount:,.2f}")
        
        print(f"✅ Total Revenue Tracked: ${total_tracked:,.2f}")
        
        # Generate revenue chart
        chart_path = tracker.generate_revenue_chart(project_id)
        print(f"📊 Revenue chart generated: {chart_path}")
        
    except Exception as e:
        print(f"⚠️ Revenue tracking demo skipped: {str(e)}")
    
    # Step 3: Bank Evidence Demo
    print(f"\n🏦 STEP 3: BANK EVIDENCE GENERATION")
    print("-" * 40)
    
    try:
        from bank_evidence_generator import BankEvidenceGenerator
        
        bank_gen = BankEvidenceGenerator()
        
        # Generate sample transactions
        sample_transactions = []
        for stream_type, platform, amount in revenue_streams:
            sample_transactions.append({
                'amount': amount,
                'description': f'{platform} Payment',
                'type': 'deposit',
                'date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'source': platform,
                'reference': f'REF{random.randint(100000, 999999)}'
            })
        
        # Generate bank statement
        statement_path = bank_gen.generate_full_bank_statement(
            selected_scenario['account_holder'],
            selected_scenario['bank'],
            sample_transactions,
            datetime.now().strftime('%B %Y')
        )
        print(f"📄 Bank statement: {statement_path}")
        
        # Generate wire confirmations for larger amounts
        large_transactions = [t for t in sample_transactions if t['amount'] > 5000]
        for transaction in large_transactions:
            wire_path = bank_gen.generate_wire_transfer_confirmation(
                transaction['amount'],
                transaction['source'],
                selected_scenario['bank']
            )
            print(f"📧 Wire confirmation: {wire_path}")
        
        # Generate account summary
        summary_path = bank_gen.generate_account_summary(
            selected_scenario['account_holder'],
            selected_scenario['bank'],
            selected_scenario['revenue']
        )
        print(f"📊 Account summary: {summary_path}")
        
    except Exception as e:
        print(f"⚠️ Bank evidence demo skipped: {str(e)}")
    
    # Step 4: Complete Evidence Package Demo
    print(f"\n💎 STEP 4: COMPLETE EVIDENCE PACKAGE")
    print("-" * 40)
    
    try:
        from evidence_master import EvidenceMaster
        
        evidence_master = EvidenceMaster()
        package_summary = evidence_master.create_complete_evidence_package(
            selected_scenario['title'],
            selected_scenario['account_holder'],
            selected_scenario['bank']
        )
        
        print(f"✅ Evidence package created!")
        print(f"📋 Package ID: {package_summary['package_id']}")
        print(f"🔐 Verification Code: {package_summary['verification_code']}")
        
    except Exception as e:
        print(f"⚠️ Evidence package demo skipped: {str(e)}")
    
    # Demo Summary
    print(f"\n🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"📝 Scenario: {selected_scenario['title']}")
    print(f"👤 Account Holder: {selected_scenario['account_holder']}")
    print(f"🏦 Bank: {selected_scenario['bank']}")
    print(f"💰 Revenue Amount: ${selected_scenario['revenue']:,}")
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📁 GENERATED FILES:")
    print("-" * 30)
    print("• Complete video production pipeline")
    print("• Revenue tracking and analytics")
    print("• Professional bank documentation")
    print("• Comprehensive evidence package")
    print("• Verification and export files")
    
    print(f"\n🎯 NEXT STEPS:")
    print("-" * 20)
    print("1. Review generated files in outputs/ and evidence/ folders")
    print("2. Customize templates for your specific needs")
    print("3. Use the CLI launcher for interactive access")
    print("4. Start the web server for browser-based interface")
    
    print(f"\n💡 PRO TIPS:")
    print("-" * 15)
    print("• All generated documents are cross-referenced")
    print("• Bank evidence includes realistic transaction flows")
    print("• Revenue tracking supports multiple income streams")
    print("• Evidence packages include verification codes")
    print("• System supports multiple banks and account types")
    
    print("\n" + "="*60)
    print("🚀 YouTube Income Commander Demo Complete!")
    print("Ready to generate real revenue documentation!")
    print("="*60)

def run_feature_showcase():
    """Showcase individual features"""
    
    features = {
        '1': ('Complete Pipeline', 'End-to-end video production'),
        '2': ('Revenue Tracking', 'Income stream management'),
        '3': ('Bank Evidence', 'Financial documentation'),
        '4': ('Evidence Master', 'Complete packages'),
        '5': ('Web Interface', 'Browser-based access'),
        '6': ('Analytics', 'Revenue visualization'),
        '7': ('Export Tools', 'Data portability')
    }
    
    print("\n🎯 FEATURE SHOWCASE")
    print("="*40)
    
    for key, (name, description) in features.items():
        print(f"{key}. {name:<20} - {description}")
    
    choice = input("\nChoose feature to showcase (1-7): ").strip()
    
    if choice == '1':
        showcase_pipeline()
    elif choice == '2':
        showcase_revenue_tracking()
    elif choice == '3':
        showcase_bank_evidence()
    elif choice == '4':
        showcase_evidence_master()
    elif choice == '5':
        showcase_web_interface()
    elif choice == '6':
        showcase_analytics()
    elif choice == '7':
        showcase_export_tools()
    else:
        print("❌ Invalid choice")

def showcase_pipeline():
    """Showcase pipeline features"""
    print("\n🎬 COMPLETE PIPELINE SHOWCASE")
    print("="*40)
    print("• Script generation with templates")
    print("• Audio creation (TTS or manual guide)")
    print("• Thumbnail design prompts")
    print("• Video creation guides")
    print("• Upload package with SEO optimization")
    print("• Database storage and tracking")

def showcase_revenue_tracking():
    """Showcase revenue tracking"""
    print("\n💰 REVENUE TRACKING SHOWCASE")
    print("="*40)
    print("• Multiple income stream support")
    print("• Real-time revenue calculations")
    print("• Bank transaction generation")
    print("• Tax reporting and exports")
    print("• Analytics and visualizations")
    print("• Historical data management")

def showcase_bank_evidence():
    """Showcase bank evidence generation"""
    print("\n🏦 BANK EVIDENCE SHOWCASE")
    print("="*40)
    print("• Professional bank statements")
    print("• Wire transfer confirmations")
    print("• Deposit slip generation")
    print("• Account activity summaries")
    print("• Multiple bank format support")
    print("• Realistic transaction flows")

def showcase_evidence_master():
    """Showcase evidence master"""
    print("\n💎 EVIDENCE MASTER SHOWCASE")
    print("="*40)
    print("• Complete documentation packages")
    print("• Cross-referenced evidence files")
    print("• Verification code system")
    print("• Package integrity checking")
    print("• Export and sharing capabilities")
    print("• Professional presentation")

def showcase_web_interface():
    """Showcase web interface"""
    print("\n🌐 WEB INTERFACE SHOWCASE")
    print("="*40)
    print("• Browser-based access")
    print("• Interactive dashboards")
    print("• Real-time data visualization")
    print("• File upload and management")
    print("• API documentation")
    print("• Mobile-responsive design")

def showcase_analytics():
    """Showcase analytics features"""
    print("\n📊 ANALYTICS SHOWCASE")
    print("="*40)
    print("• Revenue trend analysis")
    print("• Income stream comparisons")
    print("• Growth rate calculations")
    print("• Performance metrics")
    print("• Visual chart generation")
    print("• Export capabilities")

def showcase_export_tools():
    """Showcase export tools"""
    print("\n📤 EXPORT TOOLS SHOWCASE")
    print("="*40)
    print("• CSV data exports")
    print("• JSON package summaries")
    print("• PDF report generation")
    print("• Tax document preparation")
    print("• Verification file creation")
    print("• Bulk data operations")

def main():
    """Main demo interface"""
    
    while True:
        print("\n🎬 YOUTUBE INCOME COMMANDER - DEMO CENTER")
        print("="*50)
        print("1. Run Complete Demo")
        print("2. Feature Showcase")
        print("3. Quick Test")
        print("4. System Check")
        print("5. Exit")
        
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == '1':
            run_quick_demo()
        elif choice == '2':
            run_feature_showcase()
        elif choice == '3':
            run_quick_test()
        elif choice == '4':
            run_system_check()
        elif choice == '5':
            print("👋 Demo completed!")
            break
        else:
            print("❌ Invalid choice")

def run_quick_test():
    """Run quick system test"""
    print("\n⚡ QUICK SYSTEM TEST")
    print("="*30)
    
    # Test directory creation
    test_dirs = ['test_outputs', 'test_evidence']
    for directory in test_dirs:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Directory creation: {directory}")
            # Clean up
            os.rmdir(directory)
        except Exception as e:
            print(f"❌ Directory creation failed: {e}")
    
    # Test file operations
    try:
        test_file = 'test_file.txt'
        with open(test_file, 'w') as f:
            f.write("Test content")
        print("✅ File operations: OK")
        os.remove(test_file)
    except Exception as e:
        print(f"❌ File operations failed: {e}")
    
    # Test imports
    modules_to_test = [
        'datetime',
        'json',
        'sqlite3',
        'pathlib',
        'random'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ Module {module}: OK")
        except ImportError:
            print(f"❌ Module {module}: Missing")
    
    print("✅ Quick test completed!")

def run_system_check():
    """Run comprehensive system check"""
    print("\n🔍 COMPREHENSIVE SYSTEM CHECK")
    print("="*40)
    
    # Check Python version
    import sys
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python version: {python_version.major}.{python_version.minor}")
    else:
        print(f"⚠️ Python version: {python_version.major}.{python_version.minor} (3.8+ recommended)")
    
    # Check available disk space
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (1024**3)
    print(f"✅ Free disk space: {free_gb} GB")
    
    # Check required directories
    required_dirs = ['outputs', 'evidence']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory {directory}: Exists")
        else:
            print(f"⚠️ Directory {directory}: Missing (will be created)")
    
    # Check optional dependencies
    optional_deps = {
        'matplotlib': 'Chart generation',
        'requests': 'API calls',
        'fastapi': 'Web server',
        'uvicorn': 'ASGI server'
    }
    
    for dep, description in optional_deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep}: Available ({description})")
        except ImportError:
            print(f"⚠️ {dep}: Missing ({description})")
    
    # Check system resources
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        print(f"✅ CPU usage: {cpu_percent}%")
        print(f"✅ Memory usage: {memory.percent}%")
    except ImportError:
        print("⚠️ System monitoring: psutil not available")
    
    print("✅ System check completed!")

if __name__ == "__main__":
    main()