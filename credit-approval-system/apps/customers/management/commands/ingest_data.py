from django.core.management.base import BaseCommand
from apps.utils.data_ingestion import ingest_customer_data, ingest_loan_data
import os
from apps.utils.tasks import ingest_customers_task, ingest_loans_task

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        # Use the correct path for data files in Docker container
        customer_file = 'data/customer_data.xlsx'
        loan_file = 'data/loan_data.xlsx'

        if os.path.exists(customer_file):
            self.stdout.write('Queuing customer data ingestion...')
            ingest_customers_task.delay(customer_file)
            self.stdout.write(self.style.SUCCESS('Customer data ingestion task queued'))

        if os.path.exists(loan_file):
            self.stdout.write('Queuing loan data ingestion...')
            ingest_loans_task.delay(loan_file)
            self.stdout.write(self.style.SUCCESS('Loan data ingestion task queued'))
