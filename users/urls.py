from django.urls import path
from . import views
from .views import LoginView

urlpatterns = [
    path('', views.UserList.as_view(), name='user-list'),
    path('profiles/', views.ProfileList.as_view(), name='profile-list'),
    path('profiles/<uuid:id>/', views.ProfileRetrieveUpdateDestroy.as_view(), name='profile-detail'),
    path('register/', views.RegistrationView.as_view(), name='user-register'),
    path('interest/', views.InterestSubmissionCreateView.as_view(), name='interest-submit'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
]
