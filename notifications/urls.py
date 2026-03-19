from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.my_notifications, name='notifications-list'),
    path('<uuid:notification_id>/read/', views.mark_read,       name='notification-read'),
    path('read-all/',                   views.mark_all_read,    name='notifications-read-all'),
]
