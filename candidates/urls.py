from django.urls import path
from . import views

urlpatterns = [
    # ── Candidate list / detail ─────────────────────────────────────────
    path('',                                       views.candidate_list,          name='candidate-list'),
    path('<uuid:candidate_id>/',                   views.candidate_detail,        name='candidate-detail'),
    path('<uuid:candidate_id>/status/',            views.update_candidate_status, name='candidate-status'),

    # ── Intake ────────────────────────────────────────────────────────
    path('<uuid:candidate_id>/intake/',            views.intake,                  name='candidate-intake'),
    path('<uuid:candidate_id>/intake/reopen/',     views.reopen_intake,           name='candidate-intake-reopen'),

    # ── Roles ─────────────────────────────────────────────────────────
    path('<uuid:candidate_id>/roles/',             views.role_list,               name='candidate-roles'),
    path('<uuid:candidate_id>/roles/add/',         views.add_role,                name='candidate-role-add'),
    path('<uuid:candidate_id>/roles/publish/',     views.publish_roles,           name='candidate-roles-publish'),
    path('<uuid:candidate_id>/roles/confirm/',     views.confirm_roles,           name='candidate-roles-confirm'),  # frontend
    path('<uuid:candidate_id>/roles/respond/',     views.confirm_roles,           name='candidate-roles-respond'),  # legacy alias

    # ── Credentials ────────────────────────────────────────────────
    path('<uuid:candidate_id>/credentials/',        views.credential_list,         name='candidate-credentials'),
    path('<uuid:candidate_id>/credentials/upsert/', views.save_credential,         name='candidate-credential-upsert'),  # frontend
    path('<uuid:candidate_id>/credentials/save/',   views.save_credential,         name='candidate-credential-save'),    # legacy alias

    # ── Referrals ─────────────────────────────────────────────────
    path('<uuid:candidate_id>/referrals/',          views.referrals,               name='candidate-referrals'),

    # ── Interviews ─────────────────────────────────────────────────
    path('<uuid:candidate_id>/interviews/',         views.interviews,              name='candidate-interviews'),

    # ── Placement ──────────────────────────────────────────────────
    path('<uuid:candidate_id>/placement/',          views.placement,               name='candidate-placement'),
]
