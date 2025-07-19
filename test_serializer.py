import os
import sys
import django

# Add the project subdirectory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'credit-approval-system'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
django.setup()

from apps.loans.serializers import LoanEligibilitySerializer

data = {"customer_id": 1, "loan_amount": 500000.00, "interest_rate": 12.0, "tenure": 24}
ser = LoanEligibilitySerializer(data=data)
print("Is valid:", ser.is_valid())
print("Errors:", ser.errors)