from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.audit_log_list,       name='audit-log-list'),
    path('<uuid:candidate_id>/', views.audit_candidate_logs, name='audit-candidate-logs'),
]
