from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'currency', 'provider', 'status', 'provider_order_id', 'provider_payment_id', 'created_at')
    search_fields = ('id', 'provider_order_id', 'provider_payment_id', 'user__username', 'user__email')
    list_filter = ('provider', 'status', 'currency')


from .models import WebhookEvent


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'event_type', 'received_at')
    readonly_fields = ('payload', 'received_at')
    search_fields = ('id', 'event_type')
