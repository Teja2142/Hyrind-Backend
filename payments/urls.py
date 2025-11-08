from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListCreate.as_view(), name='payment-list-create'),
    path('create-intent/', views.CreatePaymentIntent.as_view(), name='create-payment-intent'),
]
