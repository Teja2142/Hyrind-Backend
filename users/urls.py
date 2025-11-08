from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserList.as_view(), name='user-list'),
    path('profiles/', views.ProfileList.as_view(), name='profile-list'),
]
