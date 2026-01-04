from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for ViewSets
router = DefaultRouter()
router.register(r'plans', views.SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'my-subscriptions', views.UserSubscriptionViewSet, basename='user-subscription')
router.register(r'billing-history', views.BillingHistoryViewSet, basename='billing-history')
router.register(r'admin/subscriptions', views.AdminUserSubscriptionViewSet, basename='admin-subscription')
router.register(r'admin/billing-history', views.AdminBillingHistoryViewSet, basename='admin-billing-history')

urlpatterns = [
    # New subscription system (recommended)
    path('', include(router.urls)),
    
    # Payment webhook
    path('webhook/payment/', views.SubscriptionPaymentWebhookView.as_view(), name='subscription-payment-webhook'),
    
    # Legacy endpoints (deprecated - kept for backward compatibility)
    path('legacy/', views.SubscriptionListCreateView.as_view(), name='subscription-list-create-legacy'),
    path('legacy/<uuid:pk>/', views.SubscriptionRetrieveUpdateView.as_view(), name='subscription-detail-legacy'),
]
