from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('<int:pk>/', views.SubscriptionRetrieveUpdateView.as_view(), name='subscription-detail'),
]
