from django.core.management.base import BaseCommand
import pandas as pd
from datetime import datetime, timedelta
import random
import os

class Command(BaseCommand):
    help = 'Create sample Excel files for data ingestion demo'

    def handle(self, *args, **options):
        # Create data directory
        os.makedirs('data', exist_ok=True)
        
        # Sample customer data
        customers = []
        for i in range(1, 101):  # 100 customers
            customers.append({
                'customer_id': i,
                'first_name': random.choice(['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anita']),
                'last_name': random.choice(['Sharma', 'Patel', 'Kumar', 'Gupta', 'Singh', 'Verma']),
                'age': random.randint(25, 60),
                'phone_number': f'98765{43210 + i:05d}',
                'monthly_salary': random.choice([45000, 55000, 65000, 75000, 85000, 95000, 105000]),
                'approved_limit': 0,  # Will be calculated
                'current_debt': random.randint(0, 50000)
            })
        
        # Calculate approved limit
        for customer in customers:
            customer['approved_limit'] = customer['monthly_salary'] * 36
        
        # Create customer DataFrame
        customer_df = pd.DataFrame(customers)
        customer_df.to_excel('data/customer_data.xlsx', index=False)
        
        # Sample loan data
        loans = []
        loan_id = 1
        
        for customer_id in range(1, 101):
            # Each customer can have 0-3 loans
            num_loans = random.randint(0, 3)
            
            for _ in range(num_loans):
                start_date = datetime.now() - timedelta(days=random.randint(30, 730))
                tenure = random.choice([12, 18, 24, 36, 48])
                end_date = start_date + timedelta(days=30 * tenure)
                
                loan_amount = random.choice([50000, 100000, 200000, 300000, 500000])
                interest_rate = random.choice([10.5, 12.0, 14.5, 16.0])
                
                # Calculate monthly repayment
                monthly_rate = interest_rate / (12 * 100)
                if monthly_rate == 0:
                    monthly_payment = loan_amount / tenure
                else:
                    monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
                
                loans.append({
                    'customer_id': customer_id,
                    'loan_id': loan_id,
                    'loan_amount': loan_amount,
                    'tenure': tenure,
                    'interest_rate': interest_rate,
                    'monthly_repayment': round(monthly_payment, 2),
                    'emis_paid_on_time': random.randint(max(0, tenure - 6), tenure),
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                })
                
                loan_id += 1
        
        # Create loan DataFrame
        loan_df = pd.DataFrame(loans)
        loan_df.to_excel('data/loan_data.xlsx', index=False)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created sample Excel files:'))
        self.stdout.write(f'   📄 data/customer_data.xlsx ({len(customers)} customers)')
        self.stdout.write(f'   📄 data/loan_data.xlsx ({len(loans)} loans)') 