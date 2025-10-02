from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import stripe
import json
import logging
from .models import Payment, PaymentMethod, Invoice
from events.models import Event

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@method_decorator(login_required, name='dispatch')
class PaymentListView(View):
    """API view for listing user payments"""
    
    def get(self, request):
        try:
            payments = Payment.objects.filter(user=request.user).order_by('-created_at')
            
            payment_data = []
            for payment in payments:
                payment_data.append({
                    'payment_id': payment.payment_id,
                    'amount': float(payment.amount),
                    'currency': payment.currency,
                    'status': payment.status,
                    'payment_method': payment.payment_method.name,
                    'created_at': payment.created_at.isoformat(),
                    'event_title': payment.invoice.event.title,
                    'event_id': payment.invoice.event.id,
                })
            
            return JsonResponse({
                'success': True,
                'payments': payment_data,
                'total_count': len(payment_data)
            })
            
        except Exception as e:
            logger.error(f"Error fetching payments: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch payments'
            }, status=500)

@method_decorator(login_required, name='dispatch')
class ProcessPaymentView(View):
    """API view for processing payments"""
    
    def post(self, request):
        try:
            # Get payment data
            event_id = request.POST.get('event_id')
            amount = Decimal(request.POST.get('amount', '0'))
            payment_method = request.POST.get('payment_method')
            currency = request.POST.get('currency', 'INR')
            
            # Validate required fields
            if not all([event_id, amount, payment_method]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields'
                }, status=400)
            
            # Get event
            event = get_object_or_404(Event, id=event_id)
            
            # Validate amount
            if amount <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid amount'
                }, status=400)
            
            # Get payment method
            try:
                payment_method_obj = PaymentMethod.objects.get(name=payment_method)
            except PaymentMethod.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid payment method'
                }, status=400)
            
            # Create invoice
            invoice = Invoice.objects.create(
                event=event,
                user=request.user,
                issue_date=timezone.now().date(),
                due_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                subtotal=amount,
                tax_amount=amount * Decimal('0.18'),  # 18% GST
                total_amount=amount * Decimal('1.18'),
                currency=currency,
                status='sent'
            )
            
            # Create payment record
            payment = Payment.objects.create(
                invoice=invoice,
                user=request.user,
                amount=invoice.total_amount,
                currency=currency,
                payment_method=payment_method_obj,
                status='pending'
            )
            
            # Process payment based on method
            if payment_method == 'stripe':
                return self.process_stripe_payment(payment)
            elif payment_method == 'razorpay':
                return self.process_razorpay_payment(payment)
            else:
                return self.process_other_payment(payment)
                
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Payment processing failed'
            }, status=500)
    
    def process_stripe_payment(self, payment):
        """Process payment using Stripe"""
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Convert to cents
                currency=payment.currency.lower(),
                metadata={
                    'payment_id': payment.payment_id,
                    'user_id': payment.user.id,
                    'event_id': payment.invoice.event.id
                },
                description=f"Payment for {payment.invoice.event.title}"
            )
            
            # Update payment with Stripe data
            payment.transaction_id = intent.id
            payment.gateway_response = {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': intent.amount,
                'currency': intent.currency
            }
            payment.save()
            
            return JsonResponse({
                'success': True,
                'client_secret': intent.client_secret,
                'payment_id': payment.payment_id,
                'amount': intent.amount,
                'currency': intent.currency
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            payment.status = 'failed'
            payment.gateway_response = {'error': str(e)}
            payment.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Payment processing failed. Please try again.'
            }, status=400)
    
    def process_razorpay_payment(self, payment):
        """Process payment using Razorpay"""
        try:
            import razorpay
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay order
            order_data = {
                'amount': int(payment.amount * 100),  # Convert to paise
                'currency': payment.currency,
                'receipt': payment.payment_id,
                'notes': {
                    'payment_id': payment.payment_id,
                    'user_id': payment.user.id,
                    'event_id': payment.invoice.event.id,
                    'event_title': payment.invoice.event.title
                }
            }
            
            order = client.order.create(data=order_data)
            
            # Update payment with Razorpay data
            payment.transaction_id = order['id']
            payment.gateway_response = {
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'receipt': order['receipt']
            }
            payment.save()
            
            return JsonResponse({
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'payment_id': payment.payment_id
            })
            
        except Exception as e:
            logger.error(f"Razorpay error: {str(e)}")
            payment.status = 'failed'
            payment.gateway_response = {'error': str(e)}
            payment.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Payment processing failed. Please try again.'
            }, status=400)
    
    def process_other_payment(self, payment):
        """Process payment using other methods (bank transfer, cash, etc.)"""
        try:
            # For other payment methods, mark as pending
            payment.status = 'pending'
            payment.save()
            
            return JsonResponse({
                'success': True,
                'payment_id': payment.payment_id,
                'message': 'Payment request submitted successfully. You will receive instructions shortly.'
            })
            
        except Exception as e:
            logger.error(f"Other payment error: {str(e)}")
            payment.status = 'failed'
            payment.gateway_response = {'error': str(e)}
            payment.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Payment processing failed. Please try again.'
            }, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """Handle Stripe webhooks"""
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Handle the event
        try:
            if event['type'] == 'payment_intent.succeeded':
                self.handle_payment_success(event['data']['object'])
            elif event['type'] == 'payment_intent.payment_failed':
                self.handle_payment_failure(event['data']['object'])
            elif event['type'] == 'charge.refunded':
                self.handle_refund_success(event['data']['object'])
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f"Webhook handling error: {str(e)}")
            return JsonResponse({'error': 'Webhook handling failed'}, status=500)
    
    def handle_payment_success(self, payment_intent):
        """Handle successful payment"""
        try:
            payment = Payment.objects.get(transaction_id=payment_intent['id'])
            payment.status = 'completed'
            payment.payment_date = timezone.now()
            payment.gateway_response['success'] = True
            payment.save()
            
            # Update invoice
            invoice = payment.invoice
            invoice.status = 'paid'
            invoice.paid_amount = payment.amount
            invoice.save()
            
            logger.info(f"Payment {payment.payment_id} completed successfully")
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for transaction {payment_intent['id']}")
        except Exception as e:
            logger.error(f"Error handling payment success: {str(e)}")
    
    def handle_payment_failure(self, payment_intent):
        """Handle failed payment"""
        try:
            payment = Payment.objects.get(transaction_id=payment_intent['id'])
            payment.status = 'failed'
            payment.gateway_response['failure_reason'] = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
            payment.save()
            
            logger.info(f"Payment {payment.payment_id} failed")
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for transaction {payment_intent['id']}")
        except Exception as e:
            logger.error(f"Error handling payment failure: {str(e)}")
    
    def handle_refund_success(self, charge):
        """Handle successful refund"""
        try:
            payment = Payment.objects.get(transaction_id=charge['payment_intent'])
            
            # Create refund record
            from .models import Refund
            refund = Refund.objects.create(
                payment=payment,
                user=payment.user,
                amount=Decimal(charge['amount_refunded']) / 100,
                reason='Customer request',
                status='completed',
                transaction_id=charge['id'],
                refund_date=timezone.now()
            )
            
            # Update payment status
            payment.status = 'refunded'
            payment.save()
            
            logger.info(f"Refund {refund.refund_id} completed successfully")
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for charge {charge['id']}")
        except Exception as e:
            logger.error(f"Error handling refund: {str(e)}")

@method_decorator(login_required, name='dispatch')
class PaymentStatusView(View):
    """Get payment status"""
    
    def get(self, request, payment_id):
        try:
            payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
            
            return JsonResponse({
                'success': True,
                'payment': {
                    'payment_id': payment.payment_id,
                    'amount': float(payment.amount),
                    'currency': payment.currency,
                    'status': payment.status,
                    'payment_method': payment.payment_method.name,
                    'created_at': payment.created_at.isoformat(),
                    'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                    'event_title': payment.invoice.event.title,
                    'event_id': payment.invoice.event.id,
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching payment status: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch payment status'
            }, status=500)

@method_decorator(login_required, name='dispatch')
class PaymentMethodsView(View):
    """Get available payment methods"""
    
    def get(self, request):
        try:
            payment_methods = PaymentMethod.objects.filter(is_active=True)
            
            methods_data = []
            for method in payment_methods:
                methods_data.append({
                    'id': method.id,
                    'name': method.name,
                    'payment_type': method.payment_type,
                    'description': method.description,
                    'processing_fee_percentage': float(method.processing_fee_percentage),
                    'processing_fee_fixed': float(method.processing_fee_fixed),
                })
            
            return JsonResponse({
                'success': True,
                'payment_methods': methods_data
            })
            
        except Exception as e:
            logger.error(f"Error fetching payment methods: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch payment methods'
            }, status=500)

@method_decorator(login_required, name='dispatch')
class CalculateFeesView(View):
    """Calculate payment fees"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            amount = Decimal(data.get('amount', '0'))
            payment_method_id = data.get('payment_method_id')
            
            if amount <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid amount'
                }, status=400)
            
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
            except PaymentMethod.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid payment method'
                }, status=400)
            
            # Calculate fees
            percentage_fee = amount * (payment_method.processing_fee_percentage / 100)
            fixed_fee = payment_method.processing_fee_fixed
            total_fee = percentage_fee + fixed_fee
            total_amount = amount + total_fee
            
            return JsonResponse({
                'success': True,
                'fees': {
                    'base_amount': float(amount),
                    'percentage_fee': float(percentage_fee),
                    'fixed_fee': float(fixed_fee),
                    'total_fee': float(total_fee),
                    'total_amount': float(total_amount),
                    'fee_percentage': float(payment_method.processing_fee_percentage),
                    'fee_fixed': float(payment_method.processing_fee_fixed),
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error calculating fees: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to calculate fees'
            }, status=500) 