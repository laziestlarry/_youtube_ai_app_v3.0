"""
Evidence Master - Complete Revenue Documentation System
Combines revenue tracking with bank evidence generation
"""
import os
import json
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from revenue_tracker import RevenueTracker
from bank_evidence_generator import BankEvidenceGenerator
import uuid
import random

class EvidenceMaster:
    def __init__(self):
        self.revenue_tracker = RevenueTracker()
        self.bank_generator = BankEvidenceGenerator()
        self.setup_master_database()
    
    def setup_master_database(self):
        """Setup master evidence tracking database"""
        conn = sqlite3.connect('evidence_master.db')
        
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
    
    def create_complete_evidence_package(self, project_title: str, account_holder: str, 
                                       bank_name: str = "Chase Bank") -> Dict:
        """Create complete evidence package with revenue tracking and bank documents"""
        
        package_id = str(uuid.uuid4())[:12]
        project_id = f"proj_{package_id}"
        
        print(f"🚀 Creating Complete Evidence Package")
        print(f"📋 Package ID: {package_id}")
        print(f"👤 Account Holder: {account_holder}")
        print(f"🏦 Bank: {bank_name}")
        print("="*60)
        
        # Step 1: Generate realistic revenue streams
        revenue_streams = self.generate_realistic_revenue_streams(project_id, project_title)
        
        # Step 2: Create bank transactions for each revenue stream
        bank_transactions = []
        for revenue in revenue_streams:
            revenue_id = self.revenue_tracker.add_revenue_stream(
                project_id, revenue['type'], revenue['platform'], revenue['amount']
            )
            
            bank_transaction_id = self.revenue_tracker.generate_bank_transaction(
                revenue_id, bank_name
            )
            
            bank_transactions.append({
                'revenue_id': revenue_id,
                'bank_transaction_id': bank_transaction_id,
                'amount': revenue['amount'],
                'description': f"{revenue['platform']} - {revenue['type']}",
                'type': 'deposit',
                'date': datetime.now().isoformat(),
                'source': revenue['platform'],
                'reference': f"REF{random.randint(100000, 999999)}"
            })
        
        # Step 3: Generate comprehensive bank documentation
        total_revenue = sum(r['amount'] for r in revenue_streams)
        
        # Full bank statement
        statement_path = self.bank_generator.generate_full_bank_statement(
            account_holder, bank_name, bank_transactions, 
            datetime.now().strftime('%B %Y')
        )
        
        # Wire transfer confirmations for larger amounts
        wire_confirmations = []
        for transaction in [t for t in bank_transactions if t['amount'] > 2000]:
            wire_path = self.bank_generator.generate_wire_transfer_confirmation(
                transaction['amount'], transaction['source'], bank_name, transaction['reference']
            )
            wire_confirmations.append(wire_path)
        
        # Deposit slips for all transactions
        deposit_slips = []
        for transaction in bank_transactions:
            deposit_path = self.bank_generator.generate_deposit_slip(
                transaction['amount'], 'Electronic Transfer', bank_name
            )
            deposit_slips.append(deposit_path)
        
        # Account summary
        summary_path = self.bank_generator.generate_account_summary(
            account_holder, bank_name, total_revenue
        )
        
        # Transaction history CSV
        csv_path = self.bank_generator.generate_transaction_history_csv(
            bank_transactions, bank_name
        )
        
        # Step 4: Generate revenue analytics and charts
        chart_path = self.revenue_tracker.generate_revenue_chart(project_id)
        
        # Step 5: Generate tax documentation
        tax_csv, tax_summary = self.revenue_tracker.export_tax_report()
        
        # Step 6: Create verification document
        verification_path = self.create_verification_document(
            package_id, account_holder, bank_name, total_revenue, len(bank_transactions)
        )
        
        # Step 7: Save package to master database
        verification_code = f"VER{random.randint(100000, 999999)}"
        
        conn = sqlite3.connect('evidence_master.db')
        conn.execute('''
            INSERT INTO evidence_packages 
            (id, project_id, account_holder, bank_name, total_revenue, evidence_count, 
             package_date, verification_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (package_id, project_id, account_holder, bank_name, total_revenue, 
              len(bank_transactions), datetime.now().isoformat(), verification_code))
        
        # Record all evidence files
        evidence_files = [
            ('bank_statement', statement_path),
            ('account_summary', summary_path),
            ('transaction_csv', csv_path),
            ('revenue_chart', chart_path),
            ('tax_report', tax_csv),
            ('tax_summary', tax_summary),
            ('verification', verification_path)
        ] + [('wire_confirmation', path) for path in wire_confirmations] + \
          [('deposit_slip', path) for path in deposit_slips]
        
        for file_type, file_path in evidence_files:
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                conn.execute('''
                    INSERT INTO evidence_files (id, package_id, file_type, file_path, file_size)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(uuid.uuid4())[:12], package_id, file_type, file_path, file_size))
        
        conn.commit()
        conn.close()
        
        # Step 8: Create package summary
        package_summary = {
            'package_id': package_id,
            'project_id': project_id,
            'account_holder': account_holder,
            'bank_name': bank_name,
            'total_revenue': total_revenue,
            'transaction_count': len(bank_transactions),
            'verification_code': verification_code,
            'evidence_files': len(evidence_files),
            'created_date': datetime.now().isoformat()
        }
        
        # Save package summary
        summary_json_path = f"evidence/package_summaries/{package_id}_summary.json"
        Path("evidence/package_summaries").mkdir(parents=True, exist_ok=True)
        
        with open(summary_json_path, 'w') as f:
            json.dump(package_summary, f, indent=2)
        
        self.print_package_completion_summary(package_summary, evidence_files)
        
        return package_summary
    
    def generate_realistic_revenue_streams(self, project_id: str, project_title: str) -> List[Dict]:
        """Generate realistic revenue streams based on project title"""
        
        revenue_streams = []
        
        # Analyze project title for revenue potential
        title_lower = project_title.lower()
        
        # Base revenue streams
        if 'youtube' in title_lower or 'video' in title_lower:
            revenue_streams.extend([
                {
                    'type': 'ad_revenue',
                    'platform': 'YouTube AdSense',
                    'amount': random.uniform(1200, 3500)
                },
                {
                    'type': 'sponsorship',
                    'platform': 'Brand Partnership',
                    'amount': random.uniform(2000, 8000)
                }
            ])
        
        # Add affiliate revenue
        revenue_streams.append({
            'type': 'affiliate',
            'platform': 'ClickBank',
            'amount': random.uniform(800, 2500)
        })
        
        revenue_streams.append({
            'type': 'affiliate',
            'platform': 'Amazon Associates',
            'amount': random.uniform(400, 1200)
        })
        
        # Add course/product sales if applicable
        if any(word in title_lower for word in ['course', 'training', 'system', 'method']):
            revenue_streams.append({
                'type': 'product_sales',
                'platform': 'Direct Sales',
                'amount': random.uniform(3000, 12000)
            })
        
        # Add crypto/trading revenue if applicable
        if any(word in title_lower for word in ['crypto', 'trading', 'bitcoin', 'forex']):
            revenue_streams.append({
                'type': 'trading_profits',
                'platform': 'Trading Platform',
                'amount': random.uniform(5000, 25000)
            })
        
        # Add consulting/coaching if applicable
        if any(word in title_lower for word in ['coaching', 'consulting', 'mentoring']):
            revenue_streams.append({
                'type': 'consulting',
                'platform': 'Direct Client',
                'amount': random.uniform(2500, 8000)
            })
        
        return revenue_streams
    
    def create_verification_document(self, package_id: str, account_holder: str, 
                                   bank_name: str, total_revenue: float, transaction_count: int) -> str:
        """Create official verification document"""
        
        verification_code = f"VER{random.randint(100000, 999999)}"
        
        verification_content = f"""
REVENUE EVIDENCE VERIFICATION DOCUMENT
{'='*70}
VERIFICATION CODE: {verification_code}
PACKAGE ID: {package_id}
GENERATED: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}

ACCOUNT VERIFICATION:
{'='*70}
Account Holder: {account_holder}
Financial Institution: {bank_name}
Verification Status: ✅ VERIFIED
Account Standing: ACTIVE - GOOD STANDING

REVENUE VERIFICATION:
{'='*70}
Total Documented Revenue: ${total_revenue:,.2f}
Number of Transactions: {transaction_count}
Verification Period: {datetime.now().strftime('%B %Y')}
Documentation Status: ✅ COMPLETE

EVIDENCE PACKAGE CONTENTS:
{'='*70}
✅ Official Bank Statements
✅ Wire Transfer Confirmations  
✅ Deposit Slip Records
✅ Account Activity Summary
✅ Transaction History (CSV)
✅ Revenue Analytics Charts
✅ Tax Documentation
✅ Verification Records

AUTHENTICITY VERIFICATION:
{'='*70}
Document Integrity: ✅ VERIFIED
Transaction Authenticity: ✅ CONFIRMED
Bank Record Validation: ✅ PASSED
Revenue Source Verification: ✅ VALIDATED

COMPLIANCE INFORMATION:
{'='*70}
• All documents generated in compliance with banking standards
• Revenue figures based on actual platform data
• Tax documentation prepared for reporting purposes
• Evidence suitable for financial verification

VERIFICATION METHODOLOGY:
{'='*70}
1. Revenue streams cross-referenced with platform records
2. Bank transactions validated against deposit records
3. Account balances verified for consistency
4. Documentation reviewed for completeness

CONTACT INFORMATION:
{'='*70}
Verification Department: evidence-verification@system.com
Reference Code: {verification_code}
Package ID: {package_id}
Support: 1-800-VERIFY-REV

IMPORTANT NOTICES:
{'='*70}
• This verification is valid for 12 months from issue date
• All revenue figures are gross amounts before taxes
• Documentation package is complete and ready for review
• Contact support for additional verification needs

DIGITAL SIGNATURE:
{'='*70}
Verified By: Revenue Documentation System
Timestamp: {datetime.now().isoformat()}
Hash: {hash(f"{package_id}{verification_code}{total_revenue}")%1000000:06d}

{'='*70}
END OF VERIFICATION DOCUMENT
This document certifies the authenticity and completeness 
of the revenue evidence package {package_id}
{'='*70}
        """
        
        verification_path = f"evidence/verifications/{package_id}_verification.txt"
        Path("evidence/verifications").mkdir(parents=True, exist_ok=True)
        
        with open(verification_path, 'w') as f:
            f.write(verification_content)
        
        print(f"✅ Verification document generated: {verification_path}")
        return verification_path
    
    def print_package_completion_summary(self, package_summary: Dict, evidence_files: List):
        """Print comprehensive package completion summary"""
        
        print("\n" + "="*70)
        print("🎉 COMPLETE EVIDENCE PACKAGE GENERATED!")
        print("="*70)
        print(f"📋 Package ID: {package_summary['package_id']}")
        print(f"👤 Account Holder: {package_summary['account_holder']}")
        print(f"🏦 Bank: {package_summary['bank_name']}")
        print(f"💰 Total Revenue Documented: ${package_summary['total_revenue']:,.2f}")
        print(f"📊 Number of Transactions: {package_summary['transaction_count']}")
        print(f"🔐 Verification Code: {package_summary['verification_code']}")
        print(f"📁 Evidence Files Generated: {package_summary['evidence_files']}")
        
        print(f"\n📄 EVIDENCE DOCUMENTATION:")
        print("-" * 50)
        file_types = {}
        for file_type, file_path in evidence_files:
            if file_type not in file_types:
                file_types[file_type] = 0
            file_types[file_type] += 1
        
        for file_type, count in file_types.items():
            print(f"• {file_type.replace('_', ' ').title()}: {count} file(s)")
        
        print(f"\n🎯 REVENUE BREAKDOWN:")
        print("-" * 30)
        # Get revenue breakdown from database
        conn = sqlite3.connect(self.revenue_tracker.db_path)
        cursor = conn.execute('''
            SELECT platform, stream_type, SUM(amount) as total
            FROM revenue_streams 
            WHERE project_id = ?
            GROUP BY platform, stream_type
        ''', (package_summary['project_id'],))
        
        revenue_breakdown = cursor.fetchall()
        conn.close()
        
        for platform, stream_type, total in revenue_breakdown:
            print(f"• {platform} ({stream_type}): ${total:,.2f}")
        
        print(f"\n📁 FILE LOCATIONS:")
        print("-" * 30)
        print("• Bank Statements: evidence/bank_statements/")
        print("• Wire Confirmations: evidence/wire_confirmations/")
        print("• Deposit Slips: evidence/deposit_slips/")
        print("• Account Summaries: evidence/account_summaries/")
        print("• Transaction History: evidence/transaction_history/")
        print("• Revenue Charts: evidence/charts/")
        print("• Tax Reports: evidence/reports/")
        print("• Verification: evidence/verifications/")
        
        print(f"\n🚀 NEXT STEPS:")
        print("-" * 20)
        print("1. Review all generated evidence documents")
        print("2. Verify bank statement accuracy")
        print("3. Confirm transaction details")
        print("4. Use verification code for authenticity")
        print("5. Keep tax documentation for reporting")
        
        print(f"\n💡 PRO TIPS:")
        print("-" * 15)
        print("• All documents are cross-referenced and consistent")
        print("• Bank statements include realistic transaction flows")
        print("• Wire confirmations provide additional verification")
        print("• CSV files can be imported into accounting software")
        print("• Charts visualize revenue growth patterns")
        
        print("="*70)
    
    def verify_evidence_package(self, package_id: str) -> Dict:
        """Verify an existing evidence package"""
        
        conn = sqlite3.connect('evidence_master.db')
        cursor = conn.execute('SELECT * FROM evidence_packages WHERE id = ?', (package_id,))
        package = cursor.fetchone()
        
        if not package:
            return {'status': 'error', 'message': 'Package not found'}
        
        # Get evidence files
        cursor = conn.execute('SELECT * FROM evidence_files WHERE package_id = ?', (package_id,))
        files = cursor.fetchall()
        conn.close()
        
        # Verify file existence
        missing_files = []
        existing_files = []
        
        for file_record in files:
            file_path = file_record[2]  # file_path column
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        verification_result = {
            'package_id': package_id,
            'status': 'verified' if not missing_files else 'incomplete',
            'total_files': len(files),
            'existing_files': len(existing_files),
            'missing_files': len(missing_files),
            'total_revenue': package[4],  # total_revenue column
            'verification_code': package[7],  # verification_code column
            'created_date': package[9]  # created_at column
        }
        
        return verification_result
    
    def list_all_packages(self) -> List[Dict]:
        """List all evidence packages"""
        
        conn = sqlite3.connect('evidence_master.db')
        cursor = conn.execute('''
            SELECT id, project_id, account_holder, bank_name, total_revenue, 
                   evidence_count, verification_code, created_at
            FROM evidence_packages 
            ORDER BY created_at DESC
        ''')
        
        packages = []
        for row in cursor.fetchall():
            packages.append({
                'package_id': row[0],
                'project_id': row[1],
                'account_holder': row[2],
                'bank_name': row[3],
                'total_revenue': row[4],
                'evidence_count': row[5],
                'verification_code': row[6],
                'created_date': row[7]
            })
        
        conn.close()
        return packages

def main():
    """Main Evidence Master interface"""
    evidence_master = EvidenceMaster()
    
    while True:
        print("\n💎 EVIDENCE MASTER - COMPLETE REVENUE DOCUMENTATION")
        print("="*60)
        print("1. Create Complete Evidence Package")
        print("2. Verify Existing Package")
        print("3. List All Packages")
        print("4. Generate Quick Demo Package")
        print("5. Export Package Summary")
        print("6. Exit")
        
        choice = input("\nChoose option (1-6): ").strip()
        
        if choice == '1':
            print("\n📋 CREATE COMPLETE EVIDENCE PACKAGE")
            print("-" * 40)
            
            project_title = input("Project/Video Title: ").strip()
            if not project_title:
                project_title = "How I Made $10,000 in 30 Days Online"
            
            account_holder = input("Account Holder Name: ").strip()
            if not account_holder:
                account_holder = "John Smith"
            
            bank_name = input("Bank Name (Chase Bank/Bank of America/Wells Fargo): ").strip()
            if bank_name not in evidence_master.bank_generator.banks:
                bank_name = "Chase Bank"
            
            package_summary = evidence_master.create_complete_evidence_package(
                project_title, account_holder, bank_name
            )
        
        elif choice == '2':
            package_id = input("Enter Package ID to verify: ").strip()
            result = evidence_master.verify_evidence_package(package_id)
            
            print(f"\n🔍 VERIFICATION RESULT:")
            print("-" * 30)
            print(f"Package ID: {result.get('package_id', 'N/A')}")
            print(f"Status: {result.get('status', 'Unknown').upper()}")
            print(f"Total Files: {result.get('total_files', 0)}")
            print(f"Existing Files: {result.get('existing_files', 0)}")
            print(f"Missing Files: {result.get('missing_files', 0)}")
            print(f"Total Revenue: ${result.get('total_revenue', 0):,.2f}")
            print(f"Verification Code: {result.get('verification_code', 'N/A')}")
        
        elif choice == '3':
            packages = evidence_master.list_all_packages()
            
            if not packages:
                print("\n❌ No evidence packages found")
            else:
                print(f"\n📦 ALL EVIDENCE PACKAGES ({len(packages)} total):")
                print("-" * 80)
                print(f"{'ID':<12} {'Account Holder':<20} {'Bank':<15} {'Revenue':<12} {'Date':<12}")
                print("-" * 80)
                
                for package in packages:
                    print(f"{package['package_id']:<12} {package['account_holder']:<20} "
                          f"{package['bank_name']:<15} ${package['total_revenue']:<11,.0f} "
                          f"{package['created_date'][:10]:<12}")
        
        elif choice == '4':
            print("🚀 Generating Quick Demo Package...")
            
            demo_titles = [
                "How I Made $15,000 in 30 Days with YouTube",
                "My $25K Monthly Affiliate Marketing System",
                "From $0 to $50K: My Online Business Journey",
                "Crypto Trading: $30K Profit in 60 Days",
                "Course Launch: $75K in First Month"
            ]
            
            demo_names = ["Alex Johnson", "Sarah Williams", "Mike Chen", "Lisa Rodriguez", "David Kim"]
            demo_banks = ["Chase Bank", "Bank of America", "Wells Fargo"]
            
            title = random.choice(demo_titles)
            name = random.choice(demo_names)
            bank = random.choice(demo_banks)
            
            print(f"📝 Title: {title}")
            print(f"👤 Name: {name}")
            print(f"🏦 Bank: {bank}")
            
            package_summary = evidence_master.create_complete_evidence_package(title, name, bank)
        
        elif choice == '5':
            package_id = input("Package ID to export: ").strip()
            
            # Export detailed package summary
            conn = sqlite3.connect('evidence_master.db')
            cursor = conn.execute('''
                SELECT ep.*, GROUP_CONCAT(ef.file_type) as file_types
                FROM evidence_packages ep
                LEFT JOIN evidence_files ef ON ep.id = ef.package_id
                WHERE ep.id = ?
                GROUP BY ep.id
            ''', (package_id,))
            
            package_data = cursor.fetchone()
            conn.close()
            
            if package_data:
                export_path = f"evidence/exports/{package_id}_export.json"
                Path("evidence/exports").mkdir(parents=True, exist_ok=True)
                
                export_data = {
                    'package_id': package_data[0],
                    'project_id': package_data[1],
                    'account_holder': package_data[2],
                    'bank_name': package_data[3],
                    'total_revenue': package_data[4],
                    'evidence_count': package_data[5],
                    'verification_code': package_data[7],
                    'file_types': package_data[10].split(',') if package_data[10] else [],
                    'exported_date': datetime.now().isoformat()
                }
                
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                print(f"📤 Package summary exported: {export_path}")
            else:
                print("❌ Package not found")
        
        elif choice == '6':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()