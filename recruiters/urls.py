from django.urls import path
from . import views

urlpatterns = [
    path('me/',            views.recruiter_me,             name='recruiter-me'),
    path('me/update/',     views.update_recruiter_me,      name='recruiter-me-update'),
    path('me/bank/',       views.bank_details,             name='recruiter-bank'),
    path('dashboard/',     views.recruiter_dashboard,      name='recruiter-dashboard'),
    path('my-candidates/', views.my_candidates,            name='recruiter-my-candidates'),
    path('all/',                       views.recruiter_list,            name='recruiter-list'),
    path('<uuid:recruiter_id>/',       views.recruiter_detail,          name='recruiter-detail'),
    path('<uuid:recruiter_id>/bank/',  views.admin_bank_details,        name='recruiter-admin-bank'),
    path('assign/',                              views.assign_recruiter,          name='recruiter-assign'),
    path('unassign/<uuid:assignment_id>/',       views.unassign_recruiter,        name='recruiter-unassign'),
    path('assignments/',                         views.assignment_list,           name='assignment-list'),
    path('<uuid:candidate_id>/assignments/',     views.candidate_assignment_list, name='candidate-assignment-list'),
    path('<uuid:candidate_id>/daily-logs/',      views.daily_logs,                name='recruiter-daily-logs'),
    path('jobs/<uuid:job_id>/status/',           views.update_job_status,         name='job-status-update'),
    path('logs/entries/<uuid:log_id>/add/',      views.add_job_entry,             name='job-entry-add'),
    path('logs/entries/<uuid:entry_id>/update/', views.update_job_entry,          name='job-entry-update'),
]
