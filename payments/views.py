from rest_framework import generics
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer

class PaymentListCreate(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class CreatePaymentIntent(generics.CreateAPIView):
    # Placeholder for creating a Stripe PaymentIntent
    def post(self, request, *args, **kwargs):
        return Response({'client_secret': 'test_secret'})
