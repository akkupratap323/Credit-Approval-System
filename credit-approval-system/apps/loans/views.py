from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Customer, Loan
from .serializers import CustomerRegistrationSerializer, LoanEligibilitySerializer, LoanSerializer

def calculate_credit_score(customer):
    """Calculate credit score based on loan history"""
    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 50  # Default score for new customers
    
    # Component 1: Past loans paid on time (35% weight)
    total_emis = sum(loan.tenure for loan in loans)
    paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
    
    if total_emis > 0:
        on_time_percentage = (paid_on_time / total_emis) * 100
        if on_time_percentage > 95:
            component1 = 35
        elif on_time_percentage > 90:
            component1 = 25
        else:
            component1 = 15
    else:
        component1 = 20
    
    # Component 2: Number of loans (20% weight)
    loan_count = loans.count()
    if loan_count <= 2:
        component2 = 20
    elif loan_count <= 5:
        component2 = 15
    else:
        component2 = 10
    
    # Component 3: Current year activity (20% weight)
    current_year = datetime.now().year
    current_year_loans = loans.filter(start_date__year=current_year).count()
    if current_year_loans <= 2:
        component3 = 20
    else:
        component3 = 10
    
    # Component 4: Loan volume (15% weight)
    total_amount = sum(loan.loan_amount for loan in loans)
    if total_amount <= customer.approved_limit * Decimal('0.5'):
        component4 = 15
    else:
        component4 = 10
    
    # Component 5: Current debt (10% weight)
    if customer.current_debt <= customer.approved_limit * Decimal('0.3'):
        component5 = 10
    else:
        component5 = 5
    
    return min(component1 + component2 + component3 + component4 + component5, 100)

@api_view(['POST'])
def register_customer(request):
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        return Response({
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    serializer = LoanEligibilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    credit_score = calculate_credit_score(customer)
    loan_amount = data['loan_amount']
    tenure = data['tenure']
    interest_rate = data['interest_rate']
    
    # Calculate EMI
    monthly_rate = interest_rate / (12 * 100)
    if monthly_rate == 0:
        monthly_emi = loan_amount / tenure
    else:
        monthly_emi = (loan_amount * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
    
    monthly_emi = round(float(monthly_emi), 2)
    
    # Determine approval
    approval = False
    corrected_interest_rate = interest_rate
    
    if credit_score > 50:
        if monthly_emi <= customer.monthly_salary * Decimal('0.5'):
            approval = True
            if credit_score > 75:
                corrected_interest_rate = 10.0
            elif credit_score > 50:
                corrected_interest_rate = 12.0
            else:
                corrected_interest_rate = 16.0
    elif credit_score > 30:
        corrected_interest_rate = 16.0
        if monthly_emi <= customer.monthly_salary * Decimal('0.5'):
            approval = True
    
    return Response({
        'customer_id': customer.customer_id,
        'approval': approval,
        'interest_rate': float(interest_rate),
        'corrected_interest_rate': float(corrected_interest_rate),
        'tenure': tenure,
        'monthly_installment': monthly_emi
    })

@api_view(['POST'])
def create_loan(request):
    serializer = LoanEligibilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    credit_score = calculate_credit_score(customer)
    
    if credit_score <= 30:
        return Response({
            'loan_id': None,
            'customer_id': customer.customer_id,
            'loan_approved': False,
            'message': 'Credit score too low'
        })
    
    # Calculate EMI and check eligibility
    loan_amount = data['loan_amount']
    tenure = data['tenure']
    interest_rate = data['interest_rate']
    
    monthly_rate = interest_rate / (12 * 100)
    if monthly_rate == 0:
        monthly_emi = loan_amount / tenure
    else:
        monthly_emi = (loan_amount * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
    
    if monthly_emi > customer.monthly_salary * Decimal('0.5'):
        return Response({
            'loan_id': None,
            'customer_id': customer.customer_id,
            'loan_approved': False,
            'message': 'EMI exceeds 50% of monthly salary'
        })
    
    # Create loan
    loan = Loan.objects.create(
        loan_id=Loan.objects.count() + 1,
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=interest_rate,
        monthly_payment=round(float(monthly_emi), 2),
        start_date=datetime.now().date(),
        end_date=datetime.now().date() + timedelta(days=30 * tenure)
    )
    
    return Response({
        'loan_id': loan.loan_id,
        'customer_id': customer.customer_id,
        'loan_approved': True,
        'message': 'Loan approved successfully',
        'monthly_installment': loan.monthly_payment
    })

@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'loan_id': loan.loan_id,
        'customer': {
            'id': loan.customer.customer_id,
            'first_name': loan.customer.first_name,
            'last_name': loan.customer.last_name,
            'phone_number': loan.customer.phone_number,
            'age': loan.customer.age
        },
        'loan_amount': loan.loan_amount,
        'interest_rate': loan.interest_rate,
        'monthly_installment': loan.monthly_payment,
        'tenure': loan.tenure
    })

@api_view(['GET'])
def view_loans(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)
    
    loans = Loan.objects.filter(customer=customer)
    loan_data = []
    
    for loan in loans:
        loan_data.append({
            'loan_id': loan.loan_id,
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_payment,
            'repayments_left': max(0, loan.tenure - loan.emis_paid_on_time)
        })
    
    return Response(loan_data) 