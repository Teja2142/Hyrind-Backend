from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id', 'user', 'amount', 'currency', 'provider', 'status',
            'provider_order_id', 'provider_payment_id', 'provider_signature',
            'metadata', 'idempotency_key', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'provider', 'provider_order_id', 'provider_payment_id', 'created_at', 'updated_at')


class CreateRazorpayOrderSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=10, default='INR', required=False)
    receipt = serializers.CharField(max_length=200, required=False)
    notes = serializers.DictField(child=serializers.CharField(), required=False)
    idempotency_key = serializers.CharField(max_length=200, required=False)


class VerifyRazorpayPaymentSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    order_id = serializers.CharField()
    signature = serializers.CharField()
    payment_uuid = serializers.UUIDField(required=False)
