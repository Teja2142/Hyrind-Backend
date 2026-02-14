"""
Invoice serializers for API endpoints
"""
from rest_framework import serializers
from .models import Invoice, InvoiceLineItem
from subscriptions.models import SubscriptionPlan


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items"""
    subscription_plan_name = serializers.CharField(source='subscription_plan.name', read_only=True)
    
    class Meta:
        model = InvoiceLineItem
        fields = [
            'id', 'description', 'quantity', 'unit_price', 'amount',
            'subscription_plan', 'subscription_plan_name', 'created_at'
        ]
        read_only_fields = ['id', 'amount', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices"""
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'user', 'user_name', 'payment', 'subscription',
            'billing_history', 'invoice_type', 'status', 'bill_to_name', 'bill_to_email',
            'bill_to_phone', 'bill_to_address', 'subtotal', 'tax_rate', 'tax_amount',
            'discount_amount', 'total_amount', 'currency', 'invoice_date', 'due_date',
            'paid_date', 'description', 'notes', 'internal_notes', 'razorpay_payment_id',
            'razorpay_order_id', 'pdf_file', 'line_items', 'payment_method',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'tax_amount', 'total_amount', 'paid_date',
            'created_at', 'updated_at'
        ]
    
    def get_user_name(self, obj):
        """Get user's full name"""
        if hasattr(obj.user, 'profile'):
            profile = obj.user.profile
            return f"{profile.first_name} {profile.last_name}".strip() or obj.user.username
        return obj.user.username
    
    def get_payment_method(self, obj):
        """Get payment method information"""
        if obj.payment:
            return {
                'provider': obj.payment.provider,
                'status': obj.payment.status,
                'payment_id': obj.payment.provider_payment_id
            }
        return None


class InvoiceCreateSerializer(serializers.Serializer):
    """Serializer for creating invoices from payments or subscriptions"""
    payment_id = serializers.UUIDField(required=False, allow_null=True)
    subscription_id = serializers.UUIDField(required=False, allow_null=True)
    billing_history_id = serializers.UUIDField(required=False, allow_null=True)
    
    # Optional overrides
    bill_to_address = serializers.CharField(required=False, allow_blank=True)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=0)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Ensure at least one source is provided"""
        if not any([data.get('payment_id'), data.get('subscription_id'), data.get('billing_history_id')]):
            raise serializers.ValidationError(
                "At least one of payment_id, subscription_id, or billing_history_id must be provided"
            )
        return data


class InvoiceSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for invoice listing"""
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'user_name', 'invoice_type', 'status',
            'total_amount', 'currency', 'invoice_date', 'due_date', 'paid_date',
            'created_at'
        ]
    
    def get_user_name(self, obj):
        """Get user's full name"""
        if hasattr(obj.user, 'profile'):
            profile = obj.user.profile
            return f"{profile.first_name} {profile.last_name}".strip() or obj.user.username
        return obj.user.username
