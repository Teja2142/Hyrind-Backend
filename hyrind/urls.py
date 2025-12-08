from django.contrib import admin
from django.urls import path, include
from .admin import admin_site
from .views import HomeView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views import AdminLoginView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include

schema_view = get_schema_view(
    openapi.Info(
        title="Hyrind API",
        default_version='v1',
        description="API documentation for Hyrind Recruitment Platform",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Homepage
    path('', HomeView.as_view(), name='home'),
    
    # Admin
    path('admin/', admin_site.urls),
    # Explicit admin login route (helps some tooling and direct links)
    path('admin/login/', admin_site.login, name='admin_login'),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/onboarding/', include('onboarding.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/recruiters/', include('recruiters.urls')),
    # Web (template) pages for recruiter registration and profile
    path('recruiter-registration/', include('recruiters.web_urls')),
    
    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Admin API login (returns JWT) for frontend to authenticate admin actions
    path('api/admin/login/', AdminLoginView.as_view(), name='admin-api-login'),
    
    # API Documentation
    path('swagger(<format>.json|.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
