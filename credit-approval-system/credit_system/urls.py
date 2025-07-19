# credit_system/urls.py
from django.contrib import admin
from django.urls import path, include
from apps.loans import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add 'api/' prefix to all your endpoints
    path('api/register/', views.register_customer, name='register'),
    path('api/check-eligibility/', views.check_eligibility, name='check_eligibility'),
    path('api/create-loan/', views.create_loan, name='create_loan'),
    path('api/view-loan/<int:loan_id>/', views.view_loan, name='view_loan'),
    path('api/view-loans/<int:customer_id>/', views.view_loans, name='view_loans'),
]
