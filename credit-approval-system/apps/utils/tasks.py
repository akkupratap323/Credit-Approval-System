from celery import shared_task
from .data_ingestion import ingest_customer_data, ingest_loan_data

@shared_task
def ingest_customers_task(file_path):
    ingest_customer_data(file_path)

@shared_task
def ingest_loans_task(file_path):
    ingest_loan_data(file_path) 