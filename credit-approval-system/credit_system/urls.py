# credit_system/urls.py
from django.contrib import admin
from django.urls import path
from apps.loans import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', views.register_customer, name='register'),
    path('api/check-eligibility/', views.check_eligibility, name='check_eligibility'),
    path('api/create-loan/', views.create_loan, name='create_loan'),
    path('api/view-loan/<int:loan_id>/', views.view_loan, name='view_loan'),
    path('api/view-loans/<int:customer_id>/', views.view_loans, name='view_loans'),
    # Data ingestion endpoints
    path('api/ingest-data/', views.ingest_data, name='ingest_data'),
    path('api/ingestion-status/', views.ingestion_status, name='ingestion_status'),
]
