from rest_framework import serializers
from .models import Customer, Loan

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_income']
    
    def create(self, validated_data):
        monthly_income = validated_data.pop('monthly_income')
        # Calculate approved limit as 36 times monthly salary
        approved_limit = monthly_income * 36
        customer = Customer.objects.create(
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            **validated_data
        )
        return customer

class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

class LoanSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer_id', 'loan_amount', 'tenure', 'interest_rate', 'monthly_payment', 'start_date', 'end_date']
        read_only_fields = ['loan_id'] 