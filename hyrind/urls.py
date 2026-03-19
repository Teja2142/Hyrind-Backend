from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from .admin import admin_site

urlpatterns = [
    # ── Django admin ──────────────────────────────────────────────────────
    path('admin/', admin_site.urls),

    # ── OpenAPI schema + UI ───────────────────────────────────────────────
    path('api/schema/',         SpectacularAPIView.as_view(),                           name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'),      name='swagger-ui'),
    path('api/schema/redoc/',   SpectacularRedocView.as_view(url_name='schema'),        name='redoc'),

    # ── Application endpoints ─────────────────────────────────────────────
    path('api/auth/',          include('users.urls')),
    path('api/candidates/',    include('candidates.urls')),
    path('api/recruiters/',    include('recruiters.urls')),
    path('api/billing/',       include('billing.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/audit/',         include('audit.urls')),
    path('api/files/',         include('files.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
