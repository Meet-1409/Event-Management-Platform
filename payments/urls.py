from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('process/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('refund/<int:payment_id>/', views.request_refund, name='request_refund'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('download-invoice/<int:invoice_id>/', views.download_invoice, name='download_invoice'),
    
    # Paytm Payment URLs
    path('paytm/<int:payment_id>/', views.paytm_payment, name='paytm_payment'),
    path('paytm-confirmation/<int:payment_id>/', views.paytm_payment_confirmation, name='paytm_payment_confirmation'),
    
    # Export functionality
    path('export/', views.export_payments, name='export_payments'),
] 