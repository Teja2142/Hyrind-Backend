"""
Invoice generation utilities and PDF generation
"""
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from .models import Invoice, InvoiceLineItem, Payment
from subscriptions.models import UserSubscription, BillingHistory


class InvoiceGenerator:
    """
    Utility class for generating invoices from various sources
    Follows industry best practices for invoice generation
    """
    
    @staticmethod
    def create_invoice_from_payment(payment, tax_rate=Decimal('0.00'), discount=Decimal('0.00'), 
                                   notes='', address=''):
        """
        Create an invoice from a payment transaction
        
        Args:
            payment: Payment object
            tax_rate: Tax rate percentage (default: 0%)
            discount: Discount amount (default: 0)
            notes: Additional notes for customer
            address: Billing address
        
        Returns:
            Invoice object
        """
        user = payment.user
        profile = getattr(user, 'profile', None)
        
        # Get customer information
        if profile:
            bill_to_name = f"{profile.first_name} {profile.last_name}".strip() or user.username
            bill_to_email = profile.email or user.email
            bill_to_phone = getattr(profile, 'phone', '')
        else:
            bill_to_name = user.username
            bill_to_email = user.email
            bill_to_phone = ''
        
        # Determine invoice status based on payment status
        if payment.status in [Payment.STATUS_CAPTURED, Payment.STATUS_AUTHORIZED]:
            invoice_status = 'paid'
            paid_date = payment.processed_at or timezone.now()
        elif payment.status == Payment.STATUS_FAILED:
            invoice_status = 'failed'
            paid_date = None
        elif payment.status == Payment.STATUS_REFUNDED:
            invoice_status = 'refunded'
            paid_date = payment.processed_at
        else:
            invoice_status = 'pending'
            paid_date = None
        
        # Create invoice
        invoice = Invoice.objects.create(
            user=user,
            payment=payment,
            invoice_type='payment',
            status=invoice_status,
            bill_to_name=bill_to_name,
            bill_to_email=bill_to_email,
            bill_to_phone=bill_to_phone,
            bill_to_address=address,
            subtotal=payment.amount,
            tax_rate=tax_rate,
            discount_amount=discount,
            currency=payment.currency,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date(),  # Immediate payment
            paid_date=paid_date,
            description=f"Payment for transaction {payment.id}",
            notes=notes,
            razorpay_payment_id=payment.provider_payment_id,
            razorpay_order_id=payment.provider_order_id,
        )
        
        # Create line item
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description=payment.metadata.get('description', 'Service Payment') if payment.metadata else 'Service Payment',
            quantity=1,
            unit_price=payment.amount,
        )
        
        return invoice
    
    @staticmethod
    def create_invoice_from_subscription(user_subscription, billing_history=None, 
                                        tax_rate=Decimal('0.00'), discount=Decimal('0.00'),
                                        notes='', address=''):
        """
        Create an invoice from a subscription billing
        
        Args:
            user_subscription: UserSubscription object
            billing_history: Optional BillingHistory object
            tax_rate: Tax rate percentage
            discount: Discount amount
            notes: Additional notes
            address: Billing address
        
        Returns:
            Invoice object
        """
        user = user_subscription.profile.user
        profile = user_subscription.profile
        
        # Get customer information
        bill_to_name = f"{profile.first_name} {profile.last_name}".strip() or user.username
        bill_to_email = profile.email or user.email
        bill_to_phone = getattr(profile, 'phone', '')
        
        # Determine invoice status
        if billing_history:
            if billing_history.status == 'success':
                invoice_status = 'paid'
                paid_date = billing_history.created_at
                razorpay_payment_id = billing_history.razorpay_payment_id
                razorpay_order_id = billing_history.razorpay_order_id
            elif billing_history.status == 'failed':
                invoice_status = 'failed'
                paid_date = None
                razorpay_payment_id = None
                razorpay_order_id = None
            elif billing_history.status == 'refunded':
                invoice_status = 'refunded'
                paid_date = billing_history.created_at
                razorpay_payment_id = billing_history.razorpay_payment_id
                razorpay_order_id = billing_history.razorpay_order_id
            else:
                invoice_status = 'pending'
                paid_date = None
                razorpay_payment_id = None
                razorpay_order_id = None
        else:
            invoice_status = 'draft' if user_subscription.status != 'active' else 'pending'
            paid_date = None
            razorpay_payment_id = None
            razorpay_order_id = None
        
        # Calculate due date (typically 7 days for subscription)
        due_date = timezone.now().date() + timedelta(days=7)
        
        # Create invoice
        invoice = Invoice.objects.create(
            user=user,
            subscription=user_subscription,
            billing_history=billing_history,
            invoice_type='subscription',
            status=invoice_status,
            bill_to_name=bill_to_name,
            bill_to_email=bill_to_email,
            bill_to_phone=bill_to_phone,
            bill_to_address=address,
            subtotal=user_subscription.price,
            tax_rate=tax_rate,
            discount_amount=discount,
            currency='INR',  # Default currency for subscriptions
            invoice_date=timezone.now().date(),
            due_date=due_date,
            paid_date=paid_date,
            description=f"Subscription: {user_subscription.plan.name}",
            notes=notes,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
        )
        
        # Create line item
        billing_cycle_display = dict(UserSubscription._meta.get_field('billing_cycle').choices).get(
            user_subscription.billing_cycle, user_subscription.billing_cycle
        )
        
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description=f"{user_subscription.plan.name} ({billing_cycle_display})",
            quantity=1,
            unit_price=user_subscription.price,
            subscription_plan=user_subscription.plan,
        )
        
        return invoice
    
    @staticmethod
    def generate_pdf(invoice):
        """
        Generate PDF for an invoice
        
        This is a placeholder for PDF generation. In production, you would use:
        - ReportLab
        - WeasyPrint
        - xhtml2pdf
        - Or a third-party service like DocRaptor
        
        Args:
            invoice: Invoice object
        
        Returns:
            File path or None
        """
        # TODO: Implement PDF generation
        # Example using ReportLab:
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from django.core.files.base import ContentFile
        import io
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add invoice content
        p.drawString(100, 750, f"Invoice #{invoice.invoice_number}")
        p.drawString(100, 730, f"Date: {invoice.invoice_date}")
        p.drawString(100, 710, f"Bill To: {invoice.bill_to_name}")
        p.drawString(100, 690, f"Email: {invoice.bill_to_email}")
        
        # Add line items
        y_position = 650
        for item in invoice.line_items.all():
            p.drawString(100, y_position, f"{item.description}: ${item.amount}")
            y_position -= 20
        
        # Add totals
        p.drawString(100, y_position - 40, f"Subtotal: ${invoice.subtotal}")
        p.drawString(100, y_position - 60, f"Tax: ${invoice.tax_amount}")
        p.drawString(100, y_position - 80, f"Total: ${invoice.total_amount}")
        
        p.showPage()
        p.save()
        
        # Save to invoice
        buffer.seek(0)
        invoice.pdf_file.save(
            f"invoice_{invoice.invoice_number}.pdf",
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        return invoice.pdf_file.url
        """
        pass


def auto_generate_invoice_for_payment(payment):
    """
    Automatically generate invoice when payment is successful
    This can be called from payment webhook handlers
    
    Args:
        payment: Payment object
    
    Returns:
        Invoice object or None
    """
    if payment.status in [Payment.STATUS_CAPTURED, Payment.STATUS_AUTHORIZED]:
        # Check if invoice already exists
        if not hasattr(payment, 'invoices') or not payment.invoices.exists():
            invoice = InvoiceGenerator.create_invoice_from_payment(payment)
            return invoice
    return None


def auto_generate_invoice_for_subscription(user_subscription, billing_history):
    """
    Automatically generate invoice for subscription billing
    This can be called from subscription billing handlers
    
    Args:
        user_subscription: UserSubscription object
        billing_history: BillingHistory object
    
    Returns:
        Invoice object or None
    """
    if billing_history.status == 'success':
        # Check if invoice already exists for this billing history
        if not hasattr(billing_history, 'invoices') or not billing_history.invoices.exists():
            invoice = InvoiceGenerator.create_invoice_from_subscription(
                user_subscription, 
                billing_history
            )
            return invoice
    return None
