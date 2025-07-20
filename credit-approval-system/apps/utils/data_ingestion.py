import pandas as pd
from datetime import datetime
from apps.customers.models import Customer
from apps.loans.models import Loan

def ingest_customer_data(file_path):
    """Ingest customer data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        print(f"Found {len(df)} customer records to ingest")
        
        for _, row in df.iterrows():
            Customer.objects.get_or_create(
                customer_id=row["customer_id"],
                defaults={
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "phone_number": str(row["phone_number"]),
                    "monthly_salary": row["monthly_salary"],
                    "approved_limit": row["approved_limit"],
                    "current_debt": row.get("current_debt", 0),
                    "age": row.get("age", 25)
                }
            )
        print(f"Successfully ingested {len(df)} customer records")
    except Exception as e:
        print(f"Error ingesting customer data: {e}")

def ingest_loan_data(file_path):
    """Ingest loan data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        print(f"Found {len(df)} loan records to ingest")
        
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row["customer_id"])
                
                # Parse dates
                start_date = pd.to_datetime(row["start_date"]).date()
                end_date = pd.to_datetime(row["end_date"]).date()
                
                Loan.objects.get_or_create(
                    loan_id=row["loan_id"],
                    defaults={
                        "customer": customer,
                        "loan_amount": row["loan_amount"],
                        "tenure": row["tenure"],
                        "interest_rate": row["interest_rate"],
                        "monthly_payment": row["monthly_repayment"],
                        "emis_paid_on_time": row["emis_paid_on_time"],
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )
            except Customer.DoesNotExist:
                print(f"Customer {row['customer_id']} not found for loan {row['loan_id']}")
            except Exception as e:
                print(f"Error processing loan {row.get('loan_id', 'unknown')}: {e}")
        
        print(f"Successfully processed {len(df)} loan records")
    except Exception as e:
        print(f"Error ingesting loan data: {e}")
