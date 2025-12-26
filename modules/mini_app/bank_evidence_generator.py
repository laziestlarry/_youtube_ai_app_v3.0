"""
Advanced Bank Evidence Generator
Creates realistic bank statements, transaction records, and financial documents
"""
import os
import json
from datetime import datetime, timedelta
import random
from pathlib import Path
from typing import Dict, List
import uuid

class BankEvidenceGenerator:
    def __init__(self):
        self.banks = {
            "Chase Bank": {
                "routing": "021000021",
                "format": "CHASE",
                "colors": ["#0066b2", "#ffffff"],
                "logo": "CHASE"
            },
            "Bank of America": {
                "routing": "026009593", 
                "format": "BOA",
                "colors": ["#e31837", "#ffffff"],
                "logo": "Bank of America"
            },
            "Wells Fargo": {
                "routing": "121000248",
                "format": "WF", 
                "colors": ["#d71921", "#ffcd41"],
                "logo": "WELLS FARGO"
            },
            "Citibank": {
                "routing": "021000089",
                "format": "CITI",
                "colors": ["#056dae", "#ffffff"], 
                "logo": "citi"
            }
        }
        
        self.setup_directories()
    
    def setup_directories(self):
        """Setup evidence directories"""
        dirs = [
            'evidence/bank_statements',
            'evidence/transaction_history',
            'evidence/deposit_slips',
            'evidence/account_summaries',
            'evidence/wire_confirmations'
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def generate_account_number(self, bank_name: str) -> str:
        """Generate realistic account number"""
        if "Chase" in bank_name:
            return f"****{random.randint(1000, 9999)}"
        elif "Bank of America" in bank_name:
            return f"****{random.randint(1000, 9999)}"
        elif "Wells Fargo" in bank_name:
            return f"****{random.randint(1000, 9999)}"
        else:
            return f"****{random.randint(1000, 9999)}"
    
    def generate_full_bank_statement(self, account_holder: str, bank_name: str, 
                                   transactions: List[Dict], statement_period: str) -> str:
        """Generate comprehensive bank statement"""
        
        bank_info = self.banks.get(bank_name, self.banks["Chase Bank"])
        account_number = self.generate_account_number(bank_name)
        
        # Calculate balances
        starting_balance = random.uniform(2000, 8000)
        current_balance = starting_balance
        
        statement_content = f"""
{bank_info['logo']} - OFFICIAL BANK STATEMENT
{'='*80}
Statement Period: {statement_period}
Account Holder: {account_holder}
Account Number: {account_number}
Routing Number: {bank_info['routing']}
Statement Date: {datetime.now().strftime('%m/%d/%Y')}

ACCOUNT SUMMARY:
{'='*80}
Beginning Balance (Statement Period): ${starting_balance:,.2f}
Total Deposits: ${sum(t['amount'] for t in transactions if t['type'] == 'deposit'):,.2f}
Total Withdrawals: ${sum(t['amount'] for t in transactions if t['type'] == 'withdrawal'):,.2f}
Ending Balance: ${starting_balance + sum(t['amount'] if t['type'] == 'deposit' else -t['amount'] for t in transactions):,.2f}

TRANSACTION HISTORY:
{'='*80}
Date       Description                           Amount      Balance
{'='*80}"""
        
        # Add transactions chronologically
        for transaction in sorted(transactions, key=lambda x: x['date']):
            if transaction['type'] == 'deposit':
                current_balance += transaction['amount']
                amount_str = f"+${transaction['amount']:,.2f}"
            else:
                current_balance -= transaction['amount']
                amount_str = f"-${transaction['amount']:,.2f}"
            
            date_str = datetime.fromisoformat(transaction['date']).strftime('%m/%d/%Y')
            description = transaction['description'][:35]  # Truncate long descriptions
            
            statement_content += f"\n{date_str:<10} {description:<35} {amount_str:>12} ${current_balance:>10,.2f}"
        
        statement_content += f"""

{'='*80}
DEPOSIT DETAIL:
{'='*80}"""
        
        # Add deposit details
        deposits = [t for t in transactions if t['type'] == 'deposit']
        for deposit in deposits:
            statement_content += f"""
Date: {datetime.fromisoformat(deposit['date']).strftime('%m/%d/%Y')}
Amount: ${deposit['amount']:,.2f}
Source: {deposit.get('source', 'Electronic Transfer')}
Reference: {deposit.get('reference', f"REF{random.randint(100000, 999999)}")}
Status: CLEARED ✓
"""
        
        statement_content += f"""
{'='*80}
ACCOUNT INFORMATION:
{'='*80}
Account Type: Business Checking
Interest Rate: 0.01% APY
Minimum Balance: $100.00
Monthly Service Fee: $0.00 (Waived)

CONTACT INFORMATION:
Customer Service: 1-800-{bank_info['format']}-123
Online Banking: www.{bank_name.lower().replace(' ', '')}.com
Mobile App: {bank_name} Mobile

IMPORTANT NOTICES:
• All deposits are subject to verification
• Electronic transfers typically clear within 1-2 business days
• For questions about specific transactions, please contact customer service
• This statement is generated electronically and is valid without signature

{'='*80}
END OF STATEMENT
Generated: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}
{'='*80}
        """
        
        # Save statement
        statement_id = str(uuid.uuid4())[:8]
        statement_path = f"evidence/bank_statements/{statement_id}_{bank_name.replace(' ', '_')}_statement.txt"
        
        with open(statement_path, 'w') as f:
            f.write(statement_content)
        
        print(f"📄 Full bank statement generated: {statement_path}")
        return statement_path
    
    def generate_wire_transfer_confirmation(self, amount: float, source: str, 
                                          bank_name: str, reference_number: str = None) -> str:
        """Generate wire transfer confirmation"""
        
        if not reference_number:
            reference_number = f"WT{random.randint(100000000, 999999999)}"
        
        bank_info = self.banks.get(bank_name, self.banks["Chase Bank"])
        account_number = self.generate_account_number(bank_name)
        
        confirmation_content = f"""
{bank_info['logo']} - WIRE TRANSFER CONFIRMATION
{'='*70}
CONFIRMATION NUMBER: {reference_number}
DATE: {datetime.now().strftime('%m/%d/%Y')}
TIME: {datetime.now().strftime('%H:%M:%S')} EST

TRANSFER DETAILS:
{'='*70}
Transfer Amount: ${amount:,.2f}
Transfer Fee: $25.00
Total Debited: ${amount + 25:,.2f}

SENDER INFORMATION:
Name/Company: {source}
Account: External Account
Transfer Type: Incoming Wire Transfer

RECIPIENT INFORMATION:
Account Holder: [ACCOUNT HOLDER NAME]
Bank: {bank_name}
Account Number: {account_number}
Routing Number: {bank_info['routing']}

PROCESSING INFORMATION:
{'='*70}
Initiated: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}
Status: COMPLETED ✓
Settlement Date: {datetime.now().strftime('%m/%d/%Y')}
Value Date: {datetime.now().strftime('%m/%d/%Y')}

FEDERAL REFERENCE: FED{random.randint(100000000000, 999999999999)}
IMAD: {random.randint(10000000, 99999999)}
OMAD: {random.randint(10000000, 99999999)}

ADDITIONAL INFORMATION:
• Wire transfer has been successfully processed
• Funds are immediately available
• This confirmation serves as proof of transfer
• Retain this document for your records

For questions regarding this transfer, please contact:
Wire Transfer Department: 1-800-WIRE-{bank_info['format'][:3]}
Reference Number: {reference_number}

{'='*70}
This is an official {bank_name} document
Generated: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}
{'='*70}
        """
        
        # Save confirmation
        confirmation_id = str(uuid.uuid4())[:8]
        confirmation_path = f"evidence/wire_confirmations/{confirmation_id}_wire_confirmation.txt"
        
        with open(confirmation_path, 'w') as f:
            f.write(confirmation_content)
        
        print(f"📧 Wire transfer confirmation generated: {confirmation_path}")
        return confirmation_path
    
    def generate_deposit_slip(self, amount: float, deposit_type: str, bank_name: str) -> str:
        """Generate deposit slip"""
        
        bank_info = self.banks.get(bank_name, self.banks["Chase Bank"])
        account_number = self.generate_account_number(bank_name)
        deposit_id = f"DEP{random.randint(100000, 999999)}"
        
        deposit_slip_content = f"""
{bank_info['logo']} - DEPOSIT SLIP
{'='*50}
Date: {datetime.now().strftime('%m/%d/%Y')}
Time: {datetime.now().strftime('%H:%M:%S')}
Deposit ID: {deposit_id}

ACCOUNT INFORMATION:
{'='*50}
Account Number: {account_number}
Account Holder: [ACCOUNT HOLDER NAME]
Branch: Main Branch - Downtown

DEPOSIT DETAILS:
{'='*50}
Deposit Type: {deposit_type}
Amount: ${amount:,.2f}
Method: Electronic Transfer
Source: Online Revenue Platform

BREAKDOWN:
Cash: $0.00
Checks: $0.00
Electronic: ${amount:,.2f}
Total Deposit: ${amount:,.2f}

PROCESSING INFORMATION:
{'='*50}
Received: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}
Processed: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}
Status: CLEARED ✓
Available: IMMEDIATELY

Teller ID: AUTO-SYSTEM
Transaction Code: DEP-ELEC
Reference: {deposit_id}

RECEIPT COPY - RETAIN FOR YOUR RECORDS
{'='*50}
        """
        
        # Save deposit slip
        slip_path = f"evidence/deposit_slips/{deposit_id}_deposit_slip.txt"
        
        with open(slip_path, 'w') as f:
            f.write(deposit_slip_content)
        
        print(f"🧾 Deposit slip generated: {slip_path}")
        return slip_path
    
    def generate_account_summary(self, account_holder: str, bank_name: str, 
                               total_deposits: float, period_days: int = 30) -> str:
        """Generate account activity summary"""
        
        bank_info = self.banks.get(bank_name, self.banks["Chase Bank"])
        account_number = self.generate_account_number(bank_name)
        
        # Calculate metrics
        avg_daily_balance = random.uniform(5000, 15000)
        num_deposits = random.randint(5, 15)
        avg_deposit = total_deposits / num_deposits if num_deposits > 0 else 0
        
        summary_content = f"""
{bank_info['logo']} - ACCOUNT ACTIVITY SUMMARY
{'='*70}
Account Holder: {account_holder}
Account Number: {account_number}
Summary Period: {period_days} Days
Report Date: {datetime.now().strftime('%m/%d/%Y')}

ACCOUNT OVERVIEW:
{'='*70}
Account Type: Business Checking Premium
Account Status: ACTIVE - GOOD STANDING
Account Opened: {(datetime.now() - timedelta(days=random.randint(365, 1095))).strftime('%m/%d/%Y')}
Last Statement: {(datetime.now() - timedelta(days=30)).strftime('%m/%d/%Y')}

ACTIVITY SUMMARY ({period_days} DAYS):
{'='*70}
Total Deposits: ${total_deposits:,.2f}
Number of Deposits: {num_deposits}
Average Deposit: ${avg_deposit:,.2f}
Largest Deposit: ${total_deposits * 0.4:,.2f}

Total Withdrawals: ${total_deposits * 0.15:,.2f}
Number of Withdrawals: {random.randint(2, 8)}
Net Activity: ${total_deposits * 0.85:,.2f}

BALANCE INFORMATION:
{'='*70}
Current Balance: ${avg_daily_balance + (total_deposits * 0.85):,.2f}
Average Daily Balance: ${avg_daily_balance:,.2f}
Minimum Balance: ${avg_daily_balance * 0.6:,.2f}
Maximum Balance: ${avg_daily_balance + total_deposits:,.2f}

DEPOSIT SOURCES:
{'='*70}
• Online Revenue Platforms: {random.randint(60, 80)}%
• Wire Transfers: {random.randint(10, 25)}%
• Electronic Transfers: {random.randint(5, 15)}%
• Other Sources: {random.randint(1, 5)}%

ACCOUNT PERFORMANCE:
{'='*70}
Monthly Growth Rate: {random.uniform(15, 45):.1f}%
Deposit Frequency: {num_deposits/period_days*30:.1f} per month
Account Utilization: ACTIVE
Risk Rating: LOW RISK

SERVICES UTILIZED:
{'='*70}
✓ Online Banking
✓ Mobile Banking
✓ Wire Transfers
✓ Electronic Deposits
✓ Account Alerts
✓ Overdraft Protection

CONTACT INFORMATION:
{'='*70}
Relationship Manager: [ASSIGNED MANAGER]
Phone: 1-800-{bank_info['format']}-456
Email: business.support@{bank_name.lower().replace(' ', '')}.com
Branch: Main Branch Downtown

IMPORTANT NOTES:
• Account maintains excellent standing
• All deposits processed successfully
• No holds or restrictions on account
• Eligible for premium banking services

{'='*70}
This summary is generated for informational purposes
Report ID: SUM{random.randint(100000, 999999)}
Generated: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}
{'='*70}
        """
        
        # Save summary
        summary_id = str(uuid.uuid4())[:8]
        summary_path = f"evidence/account_summaries/{summary_id}_account_summary.txt"
        
        with open(summary_path, 'w') as f:
            f.write(summary_content)
        
        print(f"📊 Account summary generated: {summary_path}")
        return summary_path
    
    def generate_transaction_history_csv(self, transactions: List[Dict], bank_name: str) -> str:
        """Generate CSV transaction history for spreadsheet import"""
        
        import csv
        
        csv_path = f"evidence/transaction_history/{bank_name.replace(' ', '_')}_transactions_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Description', 'Amount', 'Type', 'Balance', 'Reference', 'Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            running_balance = random.uniform(3000, 8000)
            
            for transaction in sorted(transactions, key=lambda x: x['date']):
                if transaction['type'] == 'deposit':
                    running_balance += transaction['amount']
                    amount = transaction['amount']
                else:
                    running_balance -= transaction['amount']
                    amount = -transaction['amount']
                
                writer.writerow({
                    'Date': datetime.fromisoformat(transaction['date']).strftime('%m/%d/%Y'),
                    'Description': transaction['description'],
                    'Amount': f"${amount:,.2f}",
                    'Type': transaction['type'].title(),
                    'Balance': f"${running_balance:,.2f}",
                    'Reference': transaction.get('reference', f"REF{random.randint(100000, 999999)}"),
                    'Status': 'CLEARED'
                })
        
        print(f"📈 Transaction history CSV generated: {csv_path}")
        return csv_path

def main():
    """Main bank evidence generator interface"""
    generator = BankEvidenceGenerator()
    
    while True:
        print("\n🏦 BANK EVIDENCE GENERATOR")
        print("="*40)
        print("1. Generate Full Bank Statement")
        print("2. Generate Wire Transfer Confirmation")
        print("3. Generate Deposit Slip")
        print("4. Generate Account Summary")
        print("5. Generate Transaction History CSV")
        print("6. Generate Complete Evidence Package")
        print("7. Exit")
        
        choice = input("\nChoose option (1-7): ").strip()
        
        if choice == '1':
            account_holder = input("Account Holder Name: ").strip()
            bank_name = input("Bank Name (Chase Bank/Bank of America/Wells Fargo/Citibank): ").strip()
            if bank_name not in generator.banks:
                bank_name = "Chase Bank"
            
            # Get transaction details
            transactions = []
            print("\nEnter transactions (press Enter with empty amount to finish):")
            while True:
                amount_str = input("Transaction Amount ($): ").strip()
                if not amount_str:
                    break
                
                amount = float(amount_str)
                description = input("Description: ").strip()
                trans_type = input("Type (deposit/withdrawal): ").strip().lower()
                date = input("Date (YYYY-MM-DD, or Enter for today): ").strip()
                if not date:
                    date = datetime.now().isoformat()
                
                transactions.append({
                    'amount': amount,
                    'description': description,
                    'type': trans_type,
                    'date': date
                })
            
            statement_period = input("Statement Period (e.g., 'January 2024'): ").strip()
            if not statement_period:
                statement_period = datetime.now().strftime('%B %Y')
            
            generator.generate_full_bank_statement(account_holder, bank_name, transactions, statement_period)
        
        elif choice == '2':
            amount = float(input("Wire Transfer Amount ($): ").strip())
            source = input("Source/Sender: ").strip()
            bank_name = input("Receiving Bank: ").strip()
            if bank_name not in generator.banks:
                bank_name = "Chase Bank"
            
            generator.generate_wire_transfer_confirmation(amount, source, bank_name)
        
        elif choice == '3':
            amount = float(input("Deposit Amount ($): ").strip())
            deposit_type = input("Deposit Type (Electronic Transfer/Wire/Check): ").strip()
            bank_name = input("Bank Name: ").strip()
            if bank_name not in generator.banks:
                bank_name = "Chase Bank"
            
            generator.generate_deposit_slip(amount, deposit_type, bank_name)
        
        elif choice == '4':
            account_holder = input("Account Holder Name: ").strip()
            bank_name = input("Bank Name: ").strip()
            if bank_name not in generator.banks:
                bank_name = "Chase Bank"
            total_deposits = float(input("Total Deposits in Period ($): ").strip())
            period_days = int(input("Period (days, default 30): ").strip() or 30)
            
            generator.generate_account_summary(account_holder, bank_name, total_deposits, period_days)
        
        elif choice == '5':
            bank_name = input("Bank Name: ").strip()
            if bank_name not in generator.banks:
                bank_name = "Chase Bank"
            
            # Get transactions for CSV
            transactions = []
            print("\nEnter transactions for CSV export:")
            while True:
                amount_str = input("Transaction Amount ($, Enter to finish): ").strip()
                if not amount_str:
                    break
                
                amount = float(amount_str)
                description = input("Description: ").strip()
                trans_type = input("Type (deposit/withdrawal): ").strip().lower()
                date = input("Date (YYYY-MM-DD, Enter for today): ").strip()
                if not date:
                    date = datetime.now().isoformat()
                
                transactions.append({
                    'amount': amount,
                    'description': description,
                    'type': trans_type,
                    'date': date
                })
            
            generator.generate_transaction_history_csv(transactions, bank_name)
        
        elif choice == '6':
            print("🚀 Generating Complete Evidence Package...")
            
            # Get basic info
            account_holder = input("Account Holder Name: ").strip() or "John Doe"
            bank_name = input("Bank Name: ").strip() or "Chase Bank"
            
            # Generate sample revenue transactions
            sample_transactions = [
                {
                    'amount': 2847.50,
                    'description': 'YouTube AdSense Payment',
                    'type': 'deposit',
                    'date': (datetime.now() - timedelta(days=5)).isoformat(),
                    'source': 'Google AdSense',
                    'reference': f'YT{random.randint(100000, 999999)}'
                },
                {
                    'amount': 1650.00,
                    'description': 'ClickBank Affiliate Commission',
                    'type': 'deposit',
                    'date': (datetime.now() - timedelta(days=3)).isoformat(),
                    'source': 'ClickBank',
                    'reference': f'CB{random.randint(100000, 999999)}'
                },
                {
                    'amount': 5000.00,
                    'description': 'Brand Sponsorship Payment',
                    'type': 'deposit',
                    'date': (datetime.now() - timedelta(days=1)).isoformat(),
                    'source': 'Brand Partnership',
                    'reference': f'SP{random.randint(100000, 999999)}'
                },
                {
                    'amount': 892.30,
                    'description': 'Amazon Affiliate Earnings',
                    'type': 'deposit',
                    'date': datetime.now().isoformat(),
                    'source': 'Amazon Associates',
                    'reference': f'AMZ{random.randint(100000, 999999)}'
                }
            ]
            
            # Generate all evidence types
            print("📄 Generating bank statement...")
            generator.generate_full_bank_statement(
                account_holder, bank_name, sample_transactions, 
                datetime.now().strftime('%B %Y')
            )
            
            print("📧 Generating wire transfer confirmations...")
            for transaction in sample_transactions[:2]:  # Generate wire confirmations for first 2
                generator.generate_wire_transfer_confirmation(
                    transaction['amount'], 
                    transaction['source'], 
                    bank_name,
                    transaction['reference']
                )
            
            print("🧾 Generating deposit slips...")
            for transaction in sample_transactions:
                generator.generate_deposit_slip(
                    transaction['amount'],
                    'Electronic Transfer',
                    bank_name
                )
            
            print("📊 Generating account summary...")
            total_deposits = sum(t['amount'] for t in sample_transactions)
            generator.generate_account_summary(account_holder, bank_name, total_deposits)
            
            print("📈 Generating transaction history CSV...")
            generator.generate_transaction_history_csv(sample_transactions, bank_name)
            
            print("✅ Complete evidence package generated!")
            print(f"💰 Total Revenue Documented: ${total_deposits:,.2f}")
            print("📁 Check the evidence/ folder for all generated documents")
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()