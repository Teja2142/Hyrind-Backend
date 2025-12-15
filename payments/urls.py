from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListCreate.as_view(), name='payment-list-create'),
    path('razorpay/create-order/', views.CreateRazorpayOrderView.as_view(), name='razorpay-create-order'),
    path('razorpay/verify/', views.VerifyRazorpayPaymentView.as_view(), name='razorpay-verify'),
    path('razorpay/webhook/', views.RazorpayWebhookView.as_view(), name='razorpay-webhook'),
]
