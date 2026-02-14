from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .invoice_views import InvoiceViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', views.PaymentListCreate.as_view(), name='payment-list-create'),
    path('razorpay/create-order/', views.CreateRazorpayOrderView.as_view(), name='razorpay-create-order'),
    path('razorpay/verify/', views.VerifyRazorpayPaymentView.as_view(), name='razorpay-verify'),
    path('razorpay/webhook/', views.RazorpayWebhookView.as_view(), name='razorpay-webhook'),
    
    # Include router URLs for invoices
    path('', include(router.urls)),
]
