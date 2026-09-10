from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('bills/', views.bill_list_view, name='bills'),
    path('bills/<int:pk>/', views.bill_detail_view, name='detail'),
    path('bills/<int:pk>/pay/', views.pay_bill_view, name='pay'),
    path('bills/<int:pk>/delete/', views.delete_bill_view, name='delete_bill'),
    path('receipt/<int:pk>/', views.receipt_view, name='receipt'),
    path('ledger/', views.financial_ledger_view, name='ledger'),
    path('ledger/expense/<int:pk>/delete/', views.delete_expense_view, name='delete_expense'),
    path('generate-batch/', views.generate_batch_bills_view, name='generate_batch'),
    path('generate-bills/', views.generate_batch_bills_view, name='generate_bills'),
]
