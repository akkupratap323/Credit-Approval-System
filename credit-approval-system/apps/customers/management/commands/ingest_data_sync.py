from django.core.management.base import BaseCommand
from apps.utils.data_ingestion import ingest_customer_data, ingest_loan_data
import os

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files synchronously'

    def handle(self, *args, **options):
        # Use the correct path for data files in Docker container
        customer_file = 'data/customer_data.xlsx'
        loan_file = 'data/loan_data.xlsx'

        self.stdout.write('Starting data ingestion...')
        
        if os.path.exists(customer_file):
            self.stdout.write('Ingesting customer data...')
            ingest_customer_data(customer_file)
            self.stdout.write(self.style.SUCCESS('✅ Customer data ingestion completed'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Customer file not found: {customer_file}'))

        if os.path.exists(loan_file):
            self.stdout.write('Ingesting loan data...')
            ingest_loan_data(loan_file)
            self.stdout.write(self.style.SUCCESS('✅ Loan data ingestion completed'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Loan file not found: {loan_file}'))

        self.stdout.write(self.style.SUCCESS('🎉 Data ingestion completed!')) 