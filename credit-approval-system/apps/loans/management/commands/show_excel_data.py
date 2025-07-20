from django.core.management.base import BaseCommand
import pandas as pd

class Command(BaseCommand):
    help = 'Display complete Excel data content for demonstration'

    def add_arguments(self, parser):
        parser.add_argument('--full', action='store_true', help='Show all records (not just summary)')

    def handle(self, *args, **options):
        show_full = options['full']
        
        self.stdout.write(self.style.SUCCESS('📊 COMPLETE EXCEL DATA CONTENT'))
        self.stdout.write('=' * 80)
        
        try:
            # Display Customer Data
            self.stdout.write(self.style.WARNING('\n📋 CUSTOMER DATA (customer_data.xlsx)'))
            customer_df = pd.read_excel('data/customer_data.xlsx')
            self.stdout.write(f'Total Customers: {len(customer_df)}')
            self.stdout.write('-' * 80)
            
            display_limit = len(customer_df) if show_full else 20
            
            for index, row in customer_df.iterrows():
                if index >= display_limit:
                    self.stdout.write(f'... and {len(customer_df) - display_limit} more customers')
                    break
                    
                self.stdout.write(
                    f'Customer {row["customer_id"]:3d}: '
                    f'{row["first_name"]} {row["last_name"]:12s} | '
                    f'Age: {row["age"]:2d} | '
                    f'Salary: ₹{row["monthly_salary"]:,}/month | '
                    f'Limit: ₹{row["approved_limit"]:,} | '
                    f'Phone: {row["phone_number"]} | '
                    f'Debt: ₹{row["current_debt"]:,}'
                )
            
            # Display Loan Data
            self.stdout.write(self.style.WARNING('\n💰 LOAN DATA (loan_data.xlsx)'))
            loan_df = pd.read_excel('data/loan_data.xlsx')
            self.stdout.write(f'Total Loans: {len(loan_df)}')
            self.stdout.write('-' * 80)
            
            display_limit = len(loan_df) if show_full else 30
            
            for index, row in loan_df.iterrows():
                if index >= display_limit:
                    self.stdout.write(f'... and {len(loan_df) - display_limit} more loans')
                    break
                
                payment_rate = (row['emis_paid_on_time'] / row['tenure'] * 100) if row['tenure'] > 0 else 0
                
                self.stdout.write(
                    f'Loan {row["loan_id"]:3d}: '
                    f'Customer {row["customer_id"]:3d} | '
                    f'Amount: ₹{row["loan_amount"]:,} | '
                    f'{row["tenure"]:2d} months @ {row["interest_rate"]}% | '
                    f'EMI: ₹{row["monthly_repayment"]:,.2f} | '
                    f'Paid: {row["emis_paid_on_time"]}/{row["tenure"]} ({payment_rate:.1f}%) | '
                    f'{row["start_date"]} → {row["end_date"]}')
            
            # Statistics
            self.stdout.write(self.style.SUCCESS(f'\n📊 STATISTICS:'))
            self.stdout.write(f'   👥 Total Customers: {len(customer_df)}')
            self.stdout.write(f'   💰 Total Loans: {len(loan_df)}')
            self.stdout.write(f'   💵 Total Loan Amount: ₹{loan_df["loan_amount"].sum():,}')
            self.stdout.write(f'   📈 Average Salary: ₹{customer_df["monthly_salary"].mean():,.0f}')
            self.stdout.write(f'   🎯 Average Payment Rate: {(loan_df["emis_paid_on_time"].sum() / loan_df["tenure"].sum() * 100):.1f}%')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Excel data display completed!'))
            
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'❌ Excel files not found: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}')) 