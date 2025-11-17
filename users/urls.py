from django.urls import path
from . import views
from .views import LoginView

urlpatterns = [
    path('', views.UserList.as_view(), name='user-list'),
    path('profiles/', views.ProfileList.as_view(), name='profile-list'),
        path('profiles/<uuid:public_id>/', views.ProfileRetrieveUpdateDestroy.as_view(), name='profile-detail'),
    path('register/', views.RegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
]
