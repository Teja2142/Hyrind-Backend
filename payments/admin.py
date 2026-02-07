from django.contrib import admin
from .models import Payment, WebhookEvent, Invoice, InvoiceLineItem


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'currency', 'provider', 'status', 'provider_order_id', 'provider_payment_id', 'created_at')
    search_fields = ('id', 'provider_order_id', 'provider_payment_id', 'user__username', 'user__email')
    list_filter = ('provider', 'status', 'currency')


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'event_type', 'received_at')
    readonly_fields = ('payload', 'received_at')
    search_fields = ('id', 'event_type')


# Invoice Admin
class InvoiceLineItemInline(admin.TabularInline):
    """Inline admin for invoice line items"""
    model = InvoiceLineItem
    extra = 1
    readonly_fields = ['amount', 'created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for Invoice model"""
    list_display = [
        'invoice_number', 'bill_to_name', 'user', 'invoice_type',
        'status', 'total_amount', 'currency', 'invoice_date', 'created_at'
    ]
    list_filter = ['invoice_type', 'status', 'currency', 'invoice_date']
    search_fields = ['invoice_number', 'bill_to_name', 'bill_to_email', 'user__username']
    readonly_fields = [
        'id', 'invoice_number', 'subtotal', 'tax_amount', 'total_amount',
        'paid_date', 'created_at', 'updated_at'
    ]
    inlines = [InvoiceLineItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('id', 'invoice_number', 'invoice_type', 'status', 'invoice_date', 'due_date')
        }),
        ('Relations', {
            'fields': ('user', 'payment', 'subscription', 'billing_history')
        }),
        ('Billing Details', {
            'fields': (
                'bill_to_name', 'bill_to_email', 'bill_to_phone', 'bill_to_address'
            )
        }),
        ('Financial Details', {
            'fields': (
                'subtotal', 'tax_rate', 'tax_amount', 'discount_amount',
                'total_amount', 'currency'
            )
        }),
        ('Payment Information', {
            'fields': ('razorpay_payment_id', 'razorpay_order_id', 'paid_date')
        }),
        ('Additional Information', {
            'fields': ('description', 'notes', 'internal_notes', 'pdf_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['user', 'payment', 'subscription', 'billing_history', 'invoice_type'])
        return readonly


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    """Admin for InvoiceLineItem model"""
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['invoice__invoice_number', 'description']
    readonly_fields = ['id', 'amount', 'created_at']
