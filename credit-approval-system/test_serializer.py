import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
django.setup()

from apps.loans.serializers import LoanEligibilitySerializer

data = {"customer_id": 1, "loan_amount": 500000.00, "interest_rate": 12.0, "tenure": 24}
ser = LoanEligibilitySerializer(data=data)
print("Is valid:", ser.is_valid())
print("Errors:", ser.errors) 