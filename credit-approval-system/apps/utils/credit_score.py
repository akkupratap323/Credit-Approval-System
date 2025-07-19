from decimal import Decimal
from datetime import date, datetime
from apps.loans.models import Loan
from apps.customers.models import Customer

def calculate_credit_score(customer_id):
    """Calculate credit score based on historical data"""
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        
        if not loans.exists():
            return 50  # Default score for new customers
        
        # Component 1: Past loans paid on time (40 points)
        total_emis = sum(loan.tenure for loan in loans)
        total_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
        
        if total_emis > 0:
            on_time_ratio = total_paid_on_time / total_emis
            on_time_score = min(40, on_time_ratio * 40)
        else:
            on_time_score = 0
        
        # Component 2: Number of loans taken (20 points - fewer loans = higher score)
        num_loans = loans.count()
        if num_loans <= 2:
            loan_count_score = 20
        elif num_loans <= 5:
            loan_count_score = 15
        elif num_loans <= 10:
            loan_count_score = 10
        else:
            loan_count_score = 5
        
        # Component 3: Loan activity in current year (20 points)
        current_year = date.today().year
        current_year_loans = loans.filter(start_date__year=current_year)
        if current_year_loans.count() <= 2:
            current_activity_score = 20
        elif current_year_loans.count() <= 4:
            current_activity_score = 15
        else:
            current_activity_score = 10
        
        # Component 4: Loan approved volume (20 points)
        total_loan_amount = sum(loan.loan_amount for loan in loans)
        if total_loan_amount <= customer.approved_limit * Decimal('0.5'):
            volume_score = 20
        elif total_loan_amount <= customer.approved_limit:
            volume_score = 15
        else:
            volume_score = 5
        
        # Component 5: Check if current loans > approved limit
        active_loans = loans.filter(end_date__gte=date.today())
        current_loan_sum = sum(loan.loan_amount for loan in active_loans)
        
        if current_loan_sum > customer.approved_limit:
            return 0
        
        total_score = on_time_score + loan_count_score + current_activity_score + volume_score
        return min(100, max(0, total_score))
        
    except Customer.DoesNotExist:
        return 0

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    """Calculate monthly installment using compound interest formula"""
    # Convert interest_rate to Decimal for consistent types
    interest_rate = Decimal(str(interest_rate))
    monthly_rate = interest_rate / (Decimal('12') * Decimal('100'))
    
    if monthly_rate == 0:
        return loan_amount / Decimal(str(tenure))
    
    # Convert tenure to Decimal for consistent calculations
    tenure = Decimal(str(tenure))
    
    numerator = loan_amount * monthly_rate * ((Decimal('1') + monthly_rate) ** tenure)
    denominator = ((Decimal('1') + monthly_rate) ** tenure) - Decimal('1')
    
    return numerator / denominator

def get_corrected_interest_rate(credit_score, requested_rate):
    """Get corrected interest rate based on credit score"""
    if credit_score > 50:
        return requested_rate  # No correction needed
    elif credit_score > 30:
        return max(requested_rate, 12.0)
    elif credit_score > 10:
        return max(requested_rate, 16.0)
    else:
        return requested_rate  # Loan will be rejected anyway 