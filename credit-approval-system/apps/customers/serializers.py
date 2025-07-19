from rest_framework import serializers
from .models import Customer
from decimal import Decimal

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'phone_number', 'monthly_income']
    
    def create(self, validated_data):
        monthly_income = validated_data.pop('monthly_income')
        approved_limit = round(36 * monthly_income / 100000) * 100000  # Round to nearest lakh
        
        customer = Customer.objects.create(
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            **validated_data
        )
        return customer

class CustomerRegistrationResponseSerializer(serializers.ModelSerializer):
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, source='monthly_salary')
    name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

class CustomerDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='customer_id')
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age'] 