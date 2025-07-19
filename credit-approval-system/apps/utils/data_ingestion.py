import pandas as pd
from datetime import datetime
from apps.customers.models import Customer
from apps.loans.models import Loan

def ingest_customer_data(file_path):
    """Ingest customer data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        
        for _, row in df.iterrows():
            Customer.objects.get_or_create(
                customer_id=row["Customer ID"],
                defaults={
                    "first_name": row["First Name"],
                    "last_name": row["Last Name"],
                    "phone_number": str(row["Phone Number"]),
                    "monthly_salary": row["Monthly Salary"],
                    "approved_limit": row["Approved Limit"],
                    "current_debt": row.get("Current Debt", 0),
                    "age": row.get("Age", 25)
                }
            )
        print(f"Successfully ingested {len(df)} customer records")
    except Exception as e:
        print(f"Error ingesting customer data: {e}")

def ingest_loan_data(file_path):
    """Ingest loan data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row["Customer ID"])
                
                # Parse dates
                start_date = pd.to_datetime(row["Date of Approval"]).date()
                end_date = pd.to_datetime(row["End Date"]).date()
                
                Loan.objects.get_or_create(
                    loan_id=row["Loan ID"],
                    defaults={
                        "customer": customer,
                        "loan_amount": row["Loan Amount"],
                        "tenure": row["Tenure"],
                        "interest_rate": row["Interest Rate"],
                        "monthly_repayment": row["Monthly payment"],
                        "emis_paid_on_time": row["EMIs paid on Time"],
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )
            except Customer.DoesNotExist:
                print(f"Customer {row['Customer ID']} not found for loan {row['Loan ID']}")
            except Exception as e:
                print(f"Error processing loan {row.get('Loan ID', 'unknown')}: {e}")
        
        print(f"Successfully processed {len(df)} loan records")
    except Exception as e:
        print(f"Error ingesting loan data: {e}")
