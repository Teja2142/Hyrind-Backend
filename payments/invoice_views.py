"""
Invoice views and API endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Invoice, InvoiceLineItem, Payment
from .invoice_serializers import (
    InvoiceSerializer, InvoiceSummarySerializer, 
    InvoiceCreateSerializer, InvoiceLineItemSerializer
)
from .invoice_utils import InvoiceGenerator
from subscriptions.models import UserSubscription, BillingHistory


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for invoices
    
    Endpoints:
    - GET /api/invoices/ - List all invoices for authenticated user
    - GET /api/invoices/{id}/ - Get invoice detail
    - POST /api/invoices/generate/ - Generate invoice from payment/subscription
    - GET /api/invoices/{id}/download/ - Download invoice PDF
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return invoices for authenticated user"""
        user = self.request.user
        
        # Admin can see all invoices
        if user.is_staff:
            return Invoice.objects.all().select_related('user', 'payment', 'subscription').prefetch_related('line_items')
        
        # Regular users see only their invoices
        return Invoice.objects.filter(user=user).select_related('payment', 'subscription').prefetch_related('line_items')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return InvoiceSummarySerializer
        elif self.action == 'generate':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate an invoice from payment or subscription
        
        POST /api/invoices/generate/
        Body:
        {
            "payment_id": "uuid",  // Optional
            "subscription_id": "uuid",  // Optional
            "billing_history_id": "uuid",  // Optional
            "tax_rate": 0,  // Optional
            "discount_amount": 0,  // Optional
            "notes": "string",  // Optional
            "bill_to_address": "string"  // Optional
        }
        """
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_id = serializer.validated_data.get('payment_id')
        subscription_id = serializer.validated_data.get('subscription_id')
        billing_history_id = serializer.validated_data.get('billing_history_id')
        
        tax_rate = serializer.validated_data.get('tax_rate', 0)
        discount_amount = serializer.validated_data.get('discount_amount', 0)
        notes = serializer.validated_data.get('notes', '')
        address = serializer.validated_data.get('bill_to_address', '')
        
        try:
            # Generate invoice based on source
            if payment_id:
                payment = get_object_or_404(Payment, id=payment_id)
                
                # Verify user has access
                if not request.user.is_staff and payment.user != request.user:
                    return Response(
                        {'error': 'You do not have permission to generate invoice for this payment'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Check if invoice already exists
                if hasattr(payment, 'invoices') and payment.invoices.exists():
                    invoice = payment.invoices.first()
                    return Response(
                        {
                            'message': 'Invoice already exists for this payment',
                            'invoice': InvoiceSerializer(invoice).data
                        },
                        status=status.HTTP_200_OK
                    )
                
                invoice = InvoiceGenerator.create_invoice_from_payment(
                    payment, tax_rate, discount_amount, notes, address
                )
            
            elif subscription_id or billing_history_id:
                if billing_history_id:
                    billing_history = get_object_or_404(BillingHistory, id=billing_history_id)
                    user_subscription = billing_history.user_subscription
                else:
                    user_subscription = get_object_or_404(UserSubscription, id=subscription_id)
                    billing_history = None
                
                # Verify user has access
                if not request.user.is_staff and user_subscription.profile.user != request.user:
                    return Response(
                        {'error': 'You do not have permission to generate invoice for this subscription'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Check if invoice already exists
                if billing_history and hasattr(billing_history, 'invoices') and billing_history.invoices.exists():
                    invoice = billing_history.invoices.first()
                    return Response(
                        {
                            'message': 'Invoice already exists for this billing',
                            'invoice': InvoiceSerializer(invoice).data
                        },
                        status=status.HTTP_200_OK
                    )
                
                invoice = InvoiceGenerator.create_invoice_from_subscription(
                    user_subscription, billing_history, tax_rate, discount_amount, notes, address
                )
            
            return Response(
                {
                    'message': 'Invoice generated successfully',
                    'invoice': InvoiceSerializer(invoice).data
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download invoice as PDF
        
        GET /api/invoices/{id}/download/
        """
        invoice = self.get_object()
        
        # Check if PDF exists
        if not invoice.pdf_file:
            # Generate PDF if not exists
            InvoiceGenerator.generate_pdf(invoice)
        
        if invoice.pdf_file:
            # Serve the PDF file
            response = HttpResponse(invoice.pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            return response
        else:
            return Response(
                {'error': 'PDF generation is not yet implemented. Please contact support.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
    
    @action(detail=False, methods=['get'])
    def my_invoices(self, request):
        """
        Get all invoices for authenticated user with summary
        
        GET /api/invoices/my_invoices/
        """
        invoices = self.get_queryset().filter(user=request.user)
        
        # Calculate statistics
        total_paid = sum(
            inv.total_amount for inv in invoices.filter(status='paid')
        )
        total_pending = sum(
            inv.total_amount for inv in invoices.filter(status='pending')
        )
        
        serializer = InvoiceSummarySerializer(invoices, many=True)
        
        return Response({
            'count': invoices.count(),
            'total_paid': total_paid,
            'total_pending': total_pending,
            'invoices': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """
        Mark invoice as paid (Admin only)
        
        POST /api/invoices/{id}/mark_paid/
        Body: {
            "payment_id": "string",  // Optional
            "order_id": "string"  // Optional
        }
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can mark invoices as paid'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        invoice = self.get_object()
        payment_id = request.data.get('payment_id')
        order_id = request.data.get('order_id')
        
        invoice.mark_as_paid(payment_id, order_id)
        
        return Response(
            {
                'message': 'Invoice marked as paid',
                'invoice': InvoiceSerializer(invoice).data
            }
        )
