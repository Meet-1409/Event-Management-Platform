from django.urls import path
from . import api_views

app_name = 'payments_api'

urlpatterns = [
    # Payment listing and management
    path('payments/', api_views.PaymentListView.as_view(), name='payment_list'),
    path('payments/process/', api_views.ProcessPaymentView.as_view(), name='process_payment'),
    path('payments/<str:payment_id>/status/', api_views.PaymentStatusView.as_view(), name='payment_status'),
    
    # Payment methods and fees
    path('payment-methods/', api_views.PaymentMethodsView.as_view(), name='payment_methods'),
    path('calculate-fees/', api_views.CalculateFeesView.as_view(), name='calculate_fees'),
    
    # Webhooks
    path('webhooks/stripe/', api_views.StripeWebhookView.as_view(), name='stripe_webhook'),
] 