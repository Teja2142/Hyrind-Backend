from django.contrib import admin
from .models import SubscriptionPlan, Subscription, PaymentLineItem, Payment, Invoice


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display  = ('plan_name', 'amount', 'currency', 'billing_cycle', 'is_active', 'created_at')
    list_filter   = ('is_active', 'billing_cycle', 'currency')
    search_fields = ('plan_name', 'description')
    raw_id_fields = ('created_by',)
    ordering      = ('-created_at',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ('candidate', 'plan_name', 'status', 'amount', 'currency', 'next_billing_at')
    list_filter   = ('status', 'billing_cycle')
    search_fields = ('candidate__user__email', 'plan_name')
    raw_id_fields = ('candidate',)
    ordering      = ('-created_at',)


@admin.register(PaymentLineItem)
class PaymentLineItemAdmin(admin.ModelAdmin):
    list_display  = ('charge_name', 'candidate', 'amount', 'currency', 'due_date', 'payment_status')
    list_filter   = ('payment_status', 'charge_type')
    search_fields = ('candidate__user__email', 'charge_name')
    raw_id_fields = ('candidate', 'created_by', 'due_date_changed_by')
    ordering      = ('due_date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('candidate', 'amount', 'currency', 'payment_type', 'status', 'payment_date', 'created_at')
    list_filter   = ('status', 'payment_type')
    search_fields = ('candidate__user__email', 'transaction_ref')
    raw_id_fields = ('candidate', 'recorded_by', 'invoice', 'line_item')
    ordering      = ('-created_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display  = ('invoice_number', 'candidate', 'amount', 'currency', 'status', 'period_start', 'period_end', 'paid_at')
    list_filter   = ('status',)
    search_fields = ('candidate__user__email', 'invoice_number', 'payment_reference')
    raw_id_fields = ('candidate', 'subscription')
    readonly_fields = ('invoice_number', 'pdf_path', 'created_at')
    ordering      = ('-created_at',)
