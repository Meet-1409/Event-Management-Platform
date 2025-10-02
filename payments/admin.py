from django.contrib import admin
from .models import (
    PaymentMethod, Invoice, InvoiceItem, Payment, 
    Refund, PaymentGateway, Subscription, PaymentLog
)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment_type', 'is_active', 'processing_fee_percentage', 'processing_fee_fixed')
    list_filter = ('payment_type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name',)
    fieldsets = (
        ('Method Info', {
            'fields': ('name', 'payment_type', 'is_active'),
            'description': 'Basic payment method information.'
        }),
        ('Fees', {
            'fields': ('processing_fee_percentage', 'processing_fee_fixed'),
            'description': 'Processing fees for this payment method.'
        }),
        ('Configuration', {
            'fields': ('description', 'config'),
            'description': 'Method description and configuration settings.'
        }),
    )

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'event', 'user', 'status', 'total_amount', 'paid_amount', 'due_date', 'is_overdue')
    list_filter = ('status', 'currency', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'event__title', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Invoice Info', {
            'fields': ('invoice_number', 'event', 'user', 'status'),
            'description': 'Basic invoice information.'
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date'),
            'description': 'Invoice issue and due dates.'
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount'),
            'description': 'Invoice amounts and payments.'
        }),
        ('Currency', {
            'fields': ('currency',),
            'description': 'Invoice currency.'
        }),
        ('Notes', {
            'fields': ('notes', 'terms_conditions'),
            'description': 'Invoice notes and terms.'
        }),
    )

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total_price', 'item_type')
    list_filter = ('item_type',)
    search_fields = ('invoice__invoice_number', 'description')
    ordering = ('invoice', 'id')
    fieldsets = (
        ('Item Info', {
            'fields': ('invoice', 'description', 'item_type', 'item_id'),
            'description': 'Basic item information.'
        }),
        ('Pricing', {
            'fields': ('quantity', 'unit_price', 'total_price'),
            'description': 'Item pricing details.'
        }),
        ('Tax & Discount', {
            'fields': ('tax_rate', 'tax_amount', 'discount_percentage', 'discount_amount'),
            'description': 'Tax and discount information.'
        }),
        ('Notes', {
            'fields': ('notes',),
            'description': 'Additional notes for this item.'
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'invoice', 'amount', 'currency', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'currency', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'user__username', 'invoice__invoice_number', 'transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('payment_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Payment Info', {
            'fields': ('payment_id', 'invoice', 'user', 'amount', 'currency'),
            'description': 'Basic payment information.'
        }),
        ('Method & Status', {
            'fields': ('payment_method', 'status', 'transaction_id'),
            'description': 'Payment method and processing status.'
        }),
        ('Processing', {
            'fields': ('gateway_response', 'processing_fee', 'gateway_fee'),
            'description': 'Payment processing details.'
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'created_at', 'updated_at'),
            'description': 'Payment timeline.'
        }),
    )

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('refund_id', 'payment', 'user', 'amount', 'status', 'refund_date', 'created_at')
    list_filter = ('status', 'refund_date', 'created_at')
    search_fields = ('refund_id', 'payment__payment_id', 'user__username', 'transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('refund_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Refund Info', {
            'fields': ('refund_id', 'payment', 'user', 'amount'),
            'description': 'Basic refund information.'
        }),
        ('Details', {
            'fields': ('reason', 'status', 'transaction_id'),
            'description': 'Refund reason and processing status.'
        }),
        ('Processing', {
            'fields': ('gateway_response',),
            'description': 'Gateway response details.'
        }),
        ('Timestamps', {
            'fields': ('refund_date', 'created_at', 'updated_at'),
            'description': 'Refund timeline.'
        }),
    )

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'gateway_type', 'is_active', 'is_test_mode', 'created_at')
    list_filter = ('gateway_type', 'is_active', 'is_test_mode')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Gateway Info', {
            'fields': ('name', 'gateway_type', 'is_active'),
            'description': 'Basic gateway information.'
        }),
        ('Configuration', {
            'fields': ('api_key', 'secret_key', 'webhook_secret', 'config'),
            'description': 'Gateway configuration settings.'
        }),
        ('Environment', {
            'fields': ('is_test_mode',),
            'description': 'Test or production environment.'
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscription_id', 'user', 'plan_type', 'name', 'price', 'status', 'start_date', 'end_date')
    list_filter = ('plan_type', 'status', 'billing_cycle', 'start_date', 'end_date')
    search_fields = ('subscription_id', 'user__username', 'name')
    ordering = ('-created_at',)
    readonly_fields = ('subscription_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Subscription Info', {
            'fields': ('subscription_id', 'user', 'plan_type', 'status'),
            'description': 'Basic subscription information.'
        }),
        ('Plan Details', {
            'fields': ('name', 'description', 'price', 'currency'),
            'description': 'Subscription plan details.'
        }),
        ('Billing', {
            'fields': ('billing_cycle',),
            'description': 'Billing cycle information.'
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'trial_end_date'),
            'description': 'Subscription start, end, and trial dates.'
        }),
        ('Features', {
            'fields': ('features', 'limits'),
            'description': 'Subscription features and limits.'
        }),
    )

@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('payment', 'user', 'level', 'message', 'ip_address', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('payment__payment_id', 'user__username', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Log Info', {
            'fields': ('payment', 'user', 'level'),
            'description': 'Basic log information.'
        }),
        ('Details', {
            'fields': ('message', 'details'),
            'description': 'Log message and additional details.'
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent'),
            'description': 'Request context information.'
        }),
    )
