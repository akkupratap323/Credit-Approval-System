from celery import shared_task
import pandas as pd
from django.db import transaction
from .models import Customer, Loan
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def ingest_customer_data(self, file_path):
    """
    Background task to ingest customer data from Excel file
    """
    try:
        logger.info(f"Starting customer data ingestion from {file_path}")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        customers_created = 0
        customers_updated = 0
        
        with transaction.atomic():
            for index, row in df.iterrows():
                customer, created = Customer.objects.get_or_create(
                    customer_id=row['customer_id'],
                    defaults={
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'age': row['age'],
                        'phone_number': row['phone_number'],
                        'monthly_salary': row['monthly_salary'],
                        'approved_limit': row['approved_limit'],
                        'current_debt': row.get('current_debt', 0)
                    }
                )
                
                if created:
                    customers_created += 1
                else:
                    customers_updated += 1
                
                # Update progress
                if index % 100 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={'current': index, 'total': len(df)}
                    )
        
        result = {
            'status': 'SUCCESS',
            'customers_created': customers_created,
            'customers_updated': customers_updated,
            'total_processed': len(df)
        }
        
        logger.info(f"Customer data ingestion completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in customer data ingestion: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@shared_task(bind=True)
def ingest_loan_data(self, file_path):
    """
    Background task to ingest loan data from Excel file
    """
    try:
        logger.info(f"Starting loan data ingestion from {file_path}")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        loans_created = 0
        loans_updated = 0
        
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    customer = Customer.objects.get(customer_id=row['customer_id'])
                    
                    loan, created = Loan.objects.get_or_create(
                        loan_id=row['loan_id'],
                        defaults={
                            'customer': customer,
                            'loan_amount': row['loan_amount'],
                            'tenure': row['tenure'],
                            'interest_rate': row['interest_rate'],
                            'monthly_payment': row['monthly_repayment'],
                            'emis_paid_on_time': row['emis_paid_on_time'],
                            'start_date': pd.to_datetime(row['start_date']).date(),
                            'end_date': pd.to_datetime(row['end_date']).date()
                        }
                    )
                    
                    if created:
                        loans_created += 1
                    else:
                        loans_updated += 1
                        
                except Customer.DoesNotExist:
                    logger.warning(f"Customer {row['customer_id']} not found for loan {row['loan_id']}")
                    continue
                
                # Update progress
                if index % 100 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={'current': index, 'total': len(df)}
                    )
        
        result = {
            'status': 'SUCCESS',
            'loans_created': loans_created,
            'loans_updated': loans_updated,
            'total_processed': len(df)
        }
        
        logger.info(f"Loan data ingestion completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in loan data ingestion: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3) 