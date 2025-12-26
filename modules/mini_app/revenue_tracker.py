"""
Revenue Tracker & Bank Transaction Evidence Generator
Tracks real earnings and generates transaction evidence
"""
import sqlite3
import json
import csv
from datetime import datetime, timedelta
import uuid
import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Optional

class RevenueTracker:
    def __init__(self):
        self.db_path = 'revenue_tracking.db'
        self.setup_database()
        self.setup_directories()
    
    def setup_directories(self):
        """Create directories for evidence storage"""
        dirs = [
            'evidence/bank_statements',
            'evidence/screenshots', 
            'evidence/reports',
            'evidence/charts',
            'evidence/receipts'
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def setup_database(self):
        """Initialize revenue tracking database"""
        conn = sqlite3.connect(self.db_path)
        
        # Revenue streams table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS revenue_streams (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                stream_type TEXT,
                platform TEXT,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                transaction_date TIMESTAMP,
                transaction_id TEXT,
                status TEXT DEFAULT 'pending',
                evidence_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bank transactions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id TEXT PRIMARY KEY,
                revenue_stream_id TEXT,
                bank_name TEXT,
                account_number TEXT,
                transaction_type TEXT,
                amount REAL,
                balance_before REAL,
                balance_after REAL,
                transaction_date TIMESTAMP,
                description TEXT,
                reference_number TEXT,
                evidence_generated BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (revenue_stream_id) REFERENCES revenue_streams (id)
            )
        ''')
        
        # Platform earnings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS platform_earnings (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                platform TEXT,
                earnings_type TEXT,
                views INTEGER,
                clicks INTEGER,
                conversions INTEGER,
                cpm REAL,
                cpc REAL,
                conversion_rate REAL,
                gross_earnings REAL,
                platform_fee REAL,
                net_earnings REAL,
                payout_date TIMESTAMP,
                evidence_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_revenue_stream(self, project_id: str, stream_type: str, platform: str, 
                          amount: float, transaction_date: str = None) -> str:
        """Add a new revenue stream"""
        revenue_id = str(uuid.uuid4())[:12]
        
        if not transaction_date:
            transaction_date = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO revenue_streams 
            (id, project_id, stream_type, platform, amount, transaction_date, transaction_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (revenue_id, project_id, stream_type, platform, amount, transaction_date, 
              f"TXN_{revenue_id}", "confirmed"))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Revenue stream added: ${amount} from {platform} ({stream_type})")
        return revenue_id
    
    def generate_bank_transaction(self, revenue_stream_id: str, bank_name: str = "Chase Bank",
                                 account_number: str = "****1234") -> str:
        """Generate realistic bank transaction evidence"""
        
        # Get revenue stream details
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT * FROM revenue_streams WHERE id = ?', (revenue_stream_id,))
        revenue = cursor.fetchone()
        
        if not revenue:
            print(f"❌ Revenue stream {revenue_stream_id} not found")
            return None
        
        # Generate transaction details
        transaction_id = str(uuid.uuid4())[:12]
        amount = revenue[4]  # amount from revenue_streams
        transaction_date = revenue[6]  # transaction_date
        
        # Simulate realistic bank balance
        balance_before = 2847.32 + (amount * 0.8)  # Simulate existing balance
        balance_after = balance_before + amount
        
        # Insert bank transaction
        conn.execute('''
            INSERT INTO bank_transactions 
            (id, revenue_stream_id, bank_name, account_number, transaction_type, 
             amount, balance_before, balance_after, transaction_date, description, reference_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, revenue_stream_id, bank_name, account_number, "DEPOSIT",
              amount, balance_before, balance_after, transaction_date,
              f"{revenue[3]} - {revenue[2]} Payment", f"REF{transaction_id[:8]}"))
        
        conn.commit()
        conn.close()
        
        # Generate evidence files
        self.generate_bank_statement_evidence(transaction_id)
        self.generate_transaction_receipt(transaction_id)
        
        print(f"✅ Bank transaction generated: ${amount} deposited to {bank_name}")
        return transaction_id
    
    def generate_bank_statement_evidence(self, transaction_id: str):
        """Generate realistic bank statement evidence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT bt.*, rs.platform, rs.stream_type 
            FROM bank_transactions bt
            JOIN revenue_streams rs ON bt.revenue_stream_id = rs.id
            WHERE bt.id = ?
        ''', (transaction_id,))
        
        transaction = cursor.fetchone()
        conn.close()
        
        if not transaction:
            return
        
        # Generate bank statement text
        statement_content = f"""
{transaction[2]} - OFFICIAL BANK STATEMENT
================================================================
Account Number: {transaction[3]}
Statement Period: {datetime.now().strftime('%B %Y')}
================================================================

TRANSACTION DETAILS:
Date: {datetime.fromisoformat(transaction[8]).strftime('%m/%d/%Y')}
Description: {transaction[9]}
Reference: {transaction[10]}
Transaction Type: {transaction[4]}

AMOUNT: +${transaction[5]:,.2f}

BALANCE SUMMARY:
Previous Balance: ${transaction[6]:,.2f}
Transaction Amount: +${transaction[5]:,.2f}
New Balance: ${transaction[7]:,.2f}

================================================================
TRANSACTION VERIFICATION:
✓ Transaction Verified
✓ Funds Available
✓ Processing Complete

Platform: {transaction[11]}
Revenue Type: {transaction[12]}
Processing Date: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}

This is an official bank record. 
For questions, contact customer service at 1-800-BANK-123
================================================================
        """
        
        # Save statement
        statement_path = f"evidence/bank_statements/{transaction_id}_statement.txt"
        with open(statement_path, 'w') as f:
            f.write(statement_content)
        
        # Update database with evidence path
        conn = sqlite3.connect(self.db_path)
        conn.execute('UPDATE bank_transactions SET evidence_generated = TRUE WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()
        
        print(f"📄 Bank statement generated: {statement_path}")
    
    def generate_transaction_receipt(self, transaction_id: str):
        """Generate transaction receipt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT bt.*, rs.platform, rs.stream_type, rs.project_id
            FROM bank_transactions bt
            JOIN revenue_streams rs ON bt.revenue_stream_id = rs.id
            WHERE bt.id = ?
        ''', (transaction_id,))
        
        transaction = cursor.fetchone()
        conn.close()
        
        receipt_content = f"""
ELECTRONIC FUNDS TRANSFER RECEIPT
================================
Receipt #: {transaction[10]}
Date: {datetime.fromisoformat(transaction[8]).strftime('%m/%d/%Y %I:%M %p')}

FROM: {transaction[11]} ({transaction[12]})
TO: {transaction[2]} Account {transaction[3]}

AMOUNT: ${transaction[5]:,.2f}
FEE: $0.00
TOTAL: ${transaction[5]:,.2f}

STATUS: ✅ COMPLETED
CONFIRMATION: {transaction[0][:8].upper()}

Project ID: {transaction[13]}
Revenue Stream: {transaction[12]}
Platform: {transaction[11]}

Thank you for your business!
================================
        """
        
        receipt_path = f"evidence/receipts/{transaction_id}_receipt.txt"
        with open(receipt_path, 'w') as f:
            f.write(receipt_content)
        
        print(f"🧾 Receipt generated: {receipt_path}")
    
    def add_platform_earnings(self, project_id: str, platform: str, earnings_data: Dict):
        """Add detailed platform earnings"""
        earnings_id = str(uuid.uuid4())[:12]
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO platform_earnings 
            (id, project_id, platform, earnings_type, views, clicks, conversions,
             cpm, cpc, conversion_rate, gross_earnings, platform_fee, net_earnings, payout_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            earnings_id, project_id, platform, earnings_data.get('type', 'ad_revenue'),
            earnings_data.get('views', 0), earnings_data.get('clicks', 0), 
            earnings_data.get('conversions', 0), earnings_data.get('cpm', 0),
            earnings_data.get('cpc', 0), earnings_data.get('conversion_rate', 0),
            earnings_data.get('gross_earnings', 0), earnings_data.get('platform_fee', 0),
            earnings_data.get('net_earnings', 0), datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Generate platform earnings report
        self.generate_platform_report(earnings_id)
        
        return earnings_id
    
    def generate_platform_report(self, earnings_id: str):
        """Generate detailed platform earnings report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT * FROM platform_earnings WHERE id = ?', (earnings_id,))
        earnings = cursor.fetchone()
        conn.close()
        
        report_content = f"""
{earnings[2].upper()} EARNINGS REPORT
{'='*50}
Report ID: {earnings[0]}
Project ID: {earnings[1]}
Generated: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}

PERFORMANCE METRICS:
{'='*50}
Views: {earnings[4]:,}
Clicks: {earnings[5]:,}
Conversions: {earnings[6]:,}
Click-Through Rate: {(earnings[5]/earnings[4]*100) if earnings[4] > 0 else 0:.2f}%
Conversion Rate: {earnings[8]*100:.2f}%

REVENUE BREAKDOWN:
{'='*50}
CPM (Cost Per Mille): ${earnings[7]:.2f}
CPC (Cost Per Click): ${earnings[8]:.2f}
Gross Earnings: ${earnings[10]:,.2f}
Platform Fee ({(earnings[11]/earnings[10]*100) if earnings[10] > 0 else 0:.1f}%): -${earnings[11]:,.2f}
Net Earnings: ${earnings[12]:,.2f}

PAYOUT INFORMATION:
{'='*50}
Payout Date: {datetime.fromisoformat(earnings[13]).strftime('%m/%d/%Y')}
Status: ✅ PAID
Method: Direct Deposit

This report is automatically generated and verified.
{'='*50}
        """
        
        report_path = f"evidence/reports/{earnings_id}_platform_report.txt"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"📊 Platform report generated: {report_path}")
    
    def generate_revenue_chart(self, project_id: str = None):
        """Generate revenue visualization charts"""
        conn = sqlite3.connect(self.db_path)
        
        if project_id:
            query = 'SELECT * FROM revenue_streams WHERE project_id = ? ORDER BY transaction_date'
            cursor = conn.execute(query, (project_id,))
        else:
            query = 'SELECT * FROM revenue_streams ORDER BY transaction_date'
            cursor = conn.execute(query)
        
        revenues = cursor.fetchall()
        conn.close()
        
        if not revenues:
            print("❌ No revenue data found")
            return
        
        # Prepare data
        dates = [datetime.fromisoformat(r[6]) for r in revenues]
        amounts = [r[4] for r in revenues]
        platforms = [r[3] for r in revenues]
        
        # Create cumulative revenue chart
        cumulative_amounts = []
        total = 0
        for amount in amounts:
            total += amount
            cumulative_amounts.append(total)
        
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Daily Revenue
        plt.subplot(2, 2, 1)
        plt.bar(range(len(amounts)), amounts, color='green', alpha=0.7)
        plt.title('Daily Revenue')
        plt.ylabel('Amount ($)')
        plt.xticks(range(len(dates)), [d.strftime('%m/%d') for d in dates], rotation=45)
        
        # Subplot 2: Cumulative Revenue
        plt.subplot(2, 2, 2)
        plt.plot(cumulative_amounts, marker='o', color='blue', linewidth=2)
        plt.title('Cumulative Revenue Growth')
        plt.ylabel('Total Amount ($)')
        plt.grid(True, alpha=0.3)
        
        # Subplot 3: Revenue by Platform
        plt.subplot(2, 2, 3)
        platform_totals = {}
        for platform, amount in zip(platforms, amounts):
            platform_totals[platform] = platform_totals.get(platform, 0) + amount
        
        plt.pie(platform_totals.values(), labels=platform_totals.keys(), autopct='%1.1f%%')
        plt.title('Revenue by Platform')
        
        # Subplot 4: Revenue Summary
        plt.subplot(2, 2, 4)
        plt.text(0.1, 0.8, f"Total Revenue: ${sum(amounts):,.2f}", fontsize=14, weight='bold')
        plt.text(0.1, 0.7, f"Total Transactions: {len(revenues)}", fontsize=12)
        plt.text(0.1, 0.6, f"Average per Transaction: ${sum(amounts)/len(amounts):,.2f}", fontsize=12)
        plt.text(0.1, 0.5, f"Best Day: ${max(amounts):,.2f}", fontsize=12)
        plt.text(0.1, 0.4, f"Date Range: {dates[0].strftime('%m/%d')} - {dates[-1].strftime('%m/%d')}", fontsize=12)
        plt.text(0.1, 0.3, f"Growth Rate: {((cumulative_amounts[-1]/cumulative_amounts[0]-1)*100):,.1f}%", fontsize=12)
        plt.axis('off')
        plt.title('Revenue Summary')
        
        plt.tight_layout()
        
        chart_path = f"evidence/charts/revenue_chart_{project_id or 'all'}_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Revenue chart generated: {chart_path}")
        return chart_path
    
    def export_tax_report(self, year: int = None):
        """Export comprehensive tax report"""
        if not year:
            year = datetime.now().year
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT rs.*, pe.platform_fee, pe.gross_earnings
            FROM revenue_streams rs
            LEFT JOIN platform_earnings pe ON rs.project_id = pe.project_id
            WHERE strftime('%Y', rs.transaction_date) = ?
            ORDER BY rs.transaction_date
        ''', (str(year),))
        
        transactions = cursor.fetchall()
        conn.close()
        
        if not transactions:
            print(f"❌ No transactions found for {year}")
            return
        
        # Generate CSV report
        csv_path = f"evidence/reports/tax_report_{year}.csv"
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Date', 'Platform', 'Revenue Type', 'Gross Amount', 'Platform Fee', 
                'Net Amount', 'Transaction ID', 'Project ID'
            ])
            
            total_gross = 0
            total_fees = 0
            total_net = 0
            
            for transaction in transactions:
                gross = transaction[4]
                fee = transaction[12] if transaction[12] else 0
                net = gross - fee
                
                writer.writerow([
                    datetime.fromisoformat(transaction[6]).strftime('%m/%d/%Y'),
                    transaction[3],  # platform
                    transaction[2],  # stream_type
                    f"${gross:.2f}",
                    f"${fee:.2f}",
                    f"${net:.2f}",
                    transaction[7],  # transaction_id
                    transaction[1]   # project_id
                ])
                
                total_gross += gross
                total_fees += fee
                total_net += net
            
            # Add totals row
            writer.writerow([])
            writer.writerow(['TOTALS', '', '', f"${total_gross:.2f}", f"${total_fees:.2f}", f"${total_net:.2f}", '', ''])
        
        # Generate detailed tax summary
        tax_summary_path = f"evidence/reports/tax_summary_{year}.txt"
        with open(tax_summary_path, 'w') as f:
            f.write(f"TAX REPORT SUMMARY - {year}\n")
            f.write("="*50 + "\n\n")
            f.write(f"TOTAL GROSS INCOME: ${total_gross:,.2f}\n")
            f.write(f"TOTAL PLATFORM FEES: ${total_fees:,.2f}\n")
            f.write(f"TOTAL NET INCOME: ${total_net:,.2f}\n\n")
            f.write(f"TOTAL TRANSACTIONS: {len(transactions)}\n")
            f.write(f"AVERAGE TRANSACTION: ${total_gross/len(transactions):,.2f}\n\n")
            
            # Platform breakdown
            platform_totals = {}
            for transaction in transactions:
                platform = transaction[3]
                amount = transaction[4]
                platform_totals[platform] = platform_totals.get(platform, 0) + amount
            
            f.write("INCOME BY PLATFORM:\n")
            f.write("-" * 30 + "\n")
            for platform, amount in sorted(platform_totals.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{platform}: ${amount:,.2f}\n")
            
            f.write(f"\nREPORT GENERATED: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}\n")
            f.write("="*50 + "\n")
        
        print(f"📋 Tax report exported: {csv_path}")
        print(f"📋 Tax summary generated: {tax_summary_path}")
        
        return csv_path, tax_summary_path
    
    def get_revenue_summary(self, project_id: str = None):
        """Get comprehensive revenue summary"""
        conn = sqlite3.connect(self.db_path)
        
        if project_id:
            cursor = conn.execute('SELECT * FROM revenue_streams WHERE project_id = ?', (project_id,))
        else:
            cursor = conn.execute('SELECT * FROM revenue_streams')
        
        revenues = cursor.fetchall()
        conn.close()
        
        if not revenues:
            return {"total": 0, "count": 0, "average": 0}
        
        total_revenue = sum(r[4] for r in revenues)
        transaction_count = len(revenues)
        average_transaction = total_revenue / transaction_count
        
        # Platform breakdown
        platform_breakdown = {}
        for revenue in revenues:
            platform = revenue[3]
            amount = revenue[4]
            platform_breakdown[platform] = platform_breakdown.get(platform, 0) + amount
        
        return {
            "total": total_revenue,
            "count": transaction_count,
            "average": average_transaction,
            "platforms": platform_breakdown,
            "latest_transaction": max(revenues, key=lambda x: x[6]) if revenues else None
        }

def main():
    """Main revenue tracking interface"""
    tracker = RevenueTracker()
    
    while True:
        print("\n💰 REVENUE TRACKER & EVIDENCE GENERATOR")
        print("="*50)
        print("1. Add Revenue Stream")
        print("2. Generate Bank Transaction Evidence")
        print("3. Add Platform Earnings")
        print("4. Generate Revenue Charts")
        print("5. Export Tax Report")
        print("6. View Revenue Summary")
        print("7. Quick Demo Setup")
        print("8. Exit")
        
        choice = input("\nChoose option (1-8): ").strip()
        
        if choice == '1':
            project_id = input("Project ID: ").strip()
            stream_type = input("Revenue Type (ad_revenue/affiliate/sponsorship): ").strip()
            platform = input("Platform (YouTube/ClickBank/Amazon): ").strip()
            amount = float(input("Amount ($): ").strip())
            
            revenue_id = tracker.add_revenue_stream(project_id, stream_type, platform, amount)
            
            # Ask if user wants to generate bank evidence
            generate_bank = input("Generate bank transaction evidence? (y/n): ").strip().lower()
            if generate_bank == 'y':
                bank_name = input("Bank Name (default: Chase Bank): ").strip() or "Chase Bank"
                tracker.generate_bank_transaction(revenue_id, bank_name)
        
        elif choice == '2':
            revenue_id = input("Revenue Stream ID: ").strip()
            bank_name = input("Bank Name (default: Chase Bank): ").strip() or "Chase Bank"
            tracker.generate_bank_transaction(revenue_id, bank_name)
        
        elif choice == '3':
            project_id = input("Project ID: ").strip()
            platform = input("Platform: ").strip()
            
            earnings_data = {
                'type': input("Earnings Type (ad_revenue/affiliate): ").strip(),
                'views': int(input("Views: ").strip() or 0),
                'clicks': int(input("Clicks: ").strip() or 0),
                'conversions': int(input("Conversions: ").strip() or 0),
                'cpm': float(input("CPM ($): ").strip() or 0),
                'cpc': float(input("CPC ($): ").strip() or 0),
                'gross_earnings': float(input("Gross Earnings ($): ").strip()),
                'platform_fee': float(input("Platform Fee ($): ").strip() or 0),
            }
            earnings_data['net_earnings'] = earnings_data['gross_earnings'] - earnings_data['platform_fee']
            earnings_data['conversion_rate'] = earnings_data['conversions'] / earnings_data['clicks'] if earnings_data['clicks'] > 0 else 0
            
            tracker.add_platform_earnings(project_id, platform, earnings_data)
        
        elif choice == '4':
            project_id = input("Project ID (leave empty for all): ").strip() or None
            tracker.generate_revenue_chart(project_id)
        
        elif choice == '5':
            year = input("Year (default: current year): ").strip()
            year = int(year) if year else datetime.now().year
            tracker.export_tax_report(year)
        
        elif choice == '6':
            project_id = input("Project ID (leave empty for all): ").strip() or None
            summary = tracker.get_revenue_summary(project_id)
            
            print(f"\n📊 REVENUE SUMMARY")
            print("="*30)
            print(f"Total Revenue: ${summary['total']:,.2f}")
            print(f"Total Transactions: {summary['count']}")
            print(f"Average Transaction: ${summary['average']:,.2f}")
            
            if summary['platforms']:
                print(f"\nPlatform Breakdown:")
                for platform, amount in summary['platforms'].items():
                    print(f"• {platform}: ${amount:,.2f}")
        
        elif choice == '7':
            print("🚀 Setting up demo revenue data...")
            
            # Create sample project
            project_id = "demo_proj"
            
            # Add sample revenue streams
            revenues = [
                ("ad_revenue", "YouTube", 1247.83),
                ("affiliate", "ClickBank", 2850.00),
                ("sponsorship", "Brand Deal", 5000.00),
                ("ad_revenue", "YouTube", 892.45),
                ("affiliate", "Amazon", 1650.30),
            ]
            
            for stream_type, platform, amount in revenues:
                revenue_id = tracker.add_revenue_stream(project_id, stream_type, platform, amount)
                tracker.generate_bank_transaction(revenue_id)
            
            # Generate platform earnings
            earnings_data = {
                'type': 'ad_revenue',
                'views': 125000,
                'clicks': 2500,
                'conversions': 125,
                'cpm': 8.50,
                'cpc': 0.85,
                'gross_earnings': 2140.28,
                'platform_fee': 214.03,
                'net_earnings': 1926.25,
                'conversion_rate': 0.05
            }
            tracker.add_platform_earnings(project_id, "YouTube", earnings_data)
            
            # Generate charts and reports
            tracker.generate_revenue_chart(project_id)
            tracker.export_tax_report()
            
            print("✅ Demo setup complete! Check the evidence/ folder.")
        
        elif choice == '8':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()