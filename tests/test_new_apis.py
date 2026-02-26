#!/usr/bin/env python
"""
tests/test_new_apis.py

Hyrind Backend – New Feature API Tests
=======================================
Tests the three recently-added feature areas:

  1. Role Suggestions
       Admin creates suggestions → client lists / filters / selects / submits
       Admin views client's suggestions via admin endpoint

  2. Recruiter Assignment & Reassignment
       Multi-recruiter per client, availability flag, reassignment workflow

  3. Private Addon (per-client scoped visibility)
       Admin assigns addon at custom price → only that client sees it

Usage:
    python tests/test_new_apis.py

Pre-requisite:
    python create_test_data.py     (base accounts; script refreshes them automatically)
"""

import os
import sys

# ── Django setup ──────────────────────────────────────────────────────────────
# Add project root to path so 'hyrind.settings' and all apps are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrind.settings')

import django
django.setup()

from django.test import Client as DjangoClient
from django.contrib.auth.models import User
from users.models import Profile
from recruiters.models import Recruiter, Assignment
from subscriptions.models import SubscriptionPlan, UserSubscription
from jobs.models import UserRoleSuggestion
from decimal import Decimal
from datetime import date


# =============================================================================
# Utility helpers
# =============================================================================

def _json(resp):
    try:
        return resp.json()
    except Exception:
        return resp.content.decode()


def check(label, cond, results):
    """Print result and append True/False to results list."""
    if cond:
        print(f"  ✅ {label}")
    else:
        print(f"  ❌ {label}")
    results.append(bool(cond))
    return bool(cond)


def section(title):
    print(f"\n{'=' * 58}")
    print(f"  TEST: {title}")
    print(f"{'=' * 58}")


def get_client(username, password):
    c = DjangoClient()
    ok = c.login(username=username, password=password)
    if not ok:
        print(f"  ⚠️  Login failed for '{username}'")
    return c


def _list(data):
    """Normalise paginated or plain-list API response to a Python list."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('results', list(data.values()) if data else [])
    return []


# =============================================================================
# Fixture loader
# =============================================================================

def load_fixture():
    admin_user     = User.objects.filter(username='admin').first()
    candidate_user = User.objects.filter(username='candidate').first()
    recruiter_user = User.objects.filter(username='recruiter').first()
    teamlead_user  = User.objects.filter(username='teamlead').first()

    if not all([admin_user, candidate_user, recruiter_user, teamlead_user]):
        print("❌  Base test data missing. Run: python create_test_data.py")
        sys.exit(1)

    candidate_profile = Profile.objects.get(user=candidate_user)
    recruiter_obj     = Recruiter.objects.get(user__user=recruiter_user)
    teamlead_obj      = Recruiter.objects.get(user__user=teamlead_user)

    # Make sure recruiters start as available (previous test run may have left them absent)
    Recruiter.objects.filter(id__in=[recruiter_obj.id, teamlead_obj.id]).update(
        availability_status='available'
    )
    recruiter_obj.refresh_from_db()
    teamlead_obj.refresh_from_db()

    return {
        'admin':             admin_user,
        'candidate':         candidate_user,
        'recruiter':         recruiter_user,
        'teamlead':          teamlead_user,
        'candidate_profile': candidate_profile,
        'recruiter_obj':     recruiter_obj,
        'teamlead_obj':      teamlead_obj,
    }


# =============================================================================
# Isolated test-data helpers
# =============================================================================

def create_candidate2():
    """Second candidate used only by the reassignment test."""
    user, created = User.objects.get_or_create(
        username='candidate2_test',
        defaults={
            'email': 'candidate2@test.local',
            'first_name': 'Test',
            'last_name': 'Candidate2',
        }
    )
    user.set_password('test123')
    user.is_active = True
    user.save(update_fields=['password', 'is_active'])

    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            'first_name': 'Test', 'last_name': 'Candidate2',
            'email': 'candidate2@test.local', 'phone': '1112223333',
            'active': True, 'registration_status': 'approved',
        }
    )
    return user, profile


def cleanup_candidate2():
    try:
        User.objects.get(username='candidate2_test').delete()
    except User.DoesNotExist:
        pass


def create_test_addon_plan(name='__Test-Private-Addon__'):
    # Clean any leftover from a previous crashed run
    old = SubscriptionPlan.objects.filter(name=name)
    UserSubscription.objects.filter(plan__in=old).delete()
    old.delete()
    return SubscriptionPlan.objects.create(
        name=name,
        plan_type='addon',
        description='Test-only private addon (auto-deleted after test)',
        base_price=Decimal('99.00'),
        is_mandatory=False,
        is_active=True,
        billing_cycle='monthly',
        features=['Test feature A', 'Test feature B'],
        is_private=False,   # starts public; assign-addon endpoint makes it private
    )


def cleanup_test_addon_plan(name='__Test-Private-Addon__'):
    # Must delete UserSubscriptions first (plan FK is PROTECT)
    plans = SubscriptionPlan.objects.filter(name=name)
    UserSubscription.objects.filter(plan__in=plans).delete()
    plans.delete()


# =============================================================================
# TEST 1 – ROLE SUGGESTIONS FLOW
# =============================================================================

def test_role_suggestions(fx):
    section("ROLE SUGGESTIONS FLOW")
    results = []

    candidate_user    = fx['candidate']
    candidate_profile = fx['candidate_profile']
    admin_user        = fx['admin']

    # Clean slate: remove existing suggestions for this candidate
    UserRoleSuggestion.objects.filter(user=candidate_user).delete()

    admin_client     = get_client('admin', 'admin123')
    candidate_client = get_client('candidate', 'test123')

    # ── Step 1: Admin bulk-creates 4 role suggestions ────────────────────────
    print("\n── Step 1: Admin bulk-creates 4 role suggestions for candidate")
    resp = admin_client.post(
        '/api/jobs/suggestions/bulk_create/',
        data={
            'user_id': candidate_user.id,
            'role_titles': [
                'Software Engineer',
                'Backend Developer',
                'Data Analyst',
                'DevOps Engineer',
            ],
            'role_category': 'Engineering',
            'admin_notes': 'Matched to your profile skills',
        },
        content_type='application/json',
    )
    d = _json(resp)
    check("bulk_create → 201 Created",       resp.status_code == 201, results)
    check("created count == 4",              d.get('summary', {}).get('created') == 4, results)
    check("skipped count == 0",              d.get('summary', {}).get('skipped') == 0, results)
    check("category = Engineering",          d.get('summary', {}).get('category') == 'Engineering', results)
    check("user info returned",              d.get('user', {}).get('email') == candidate_user.email, results)

    # ── Step 2: Duplicate bulk_create → skipped ───────────────────────────────
    print("\n── Step 2: Duplicate bulk_create → skipped (not duplicated)")
    resp = admin_client.post(
        '/api/jobs/suggestions/bulk_create/',
        data={
            'user_id': candidate_user.id,
            'role_titles': ['Software Engineer', 'New Role Title'],
            'role_category': 'Engineering',
        },
        content_type='application/json',
    )
    d = _json(resp)
    check("second bulk_create → 201 or 200", resp.status_code in (200, 201), results)
    check("existing role skipped",           d.get('summary', {}).get('skipped') == 1, results)
    check("new role created",                d.get('summary', {}).get('created') == 1, results)

    # Total suggestions now = 5 (4 + 1 new)
    # Clean back to 4 for predictable counts
    UserRoleSuggestion.objects.filter(user=candidate_user, role_title='New Role Title').delete()

    # ── Step 3: Candidate lists suggestions ──────────────────────────────────
    print("\n── Step 3: Candidate lists all suggestions")
    resp = candidate_client.get('/api/jobs/suggestions/')
    d = _json(resp)
    check("list → 200 OK",                   resp.status_code == 200, results)
    suggestions = d.get('suggestions', [])
    check("4 suggestions visible",           len(suggestions) == 4, results)
    check("summary.total == 4",              d.get('summary', {}).get('total') == 4, results)
    check("summary.selected == 0 initially", d.get('summary', {}).get('selected') == 0, results)
    check("grouped_by_category present",     'Engineering' in d.get('grouped_by_category', {}), results)

    suggestion_ids = [s['id'] for s in suggestions]

    # ── Step 4: by_category endpoint ─────────────────────────────────────────
    print("\n── Step 4: Candidate views suggestions by category")
    resp = candidate_client.get('/api/jobs/suggestions/by_category/')
    d = _json(resp)
    check("by_category → 200",               resp.status_code == 200, results)
    check("Engineering group present",       'Engineering' in d, results)
    check("Engineering has 4 roles",         len(d.get('Engineering', [])) == 4, results)

    # ── Step 5: categories endpoint ──────────────────────────────────────────
    print("\n── Step 5: Candidate views available categories")
    resp = candidate_client.get('/api/jobs/suggestions/categories/')
    d = _json(resp)
    check("categories → 200",               resp.status_code == 200, results)
    check("Engineering in categories list", 'Engineering' in d.get('categories', []), results)

    # ── Step 6: Filter by status=pending ─────────────────────────────────────
    print("\n── Step 6: Filter suggestions by status=pending")
    resp = candidate_client.get('/api/jobs/suggestions/?status=pending')
    d = _json(resp)
    check("pending filter → 200",           resp.status_code == 200, results)
    check("all 4 are pending",              d.get('summary', {}).get('total') == 4, results)

    # ── Step 7: Toggle (select) first suggestion ──────────────────────────────
    first_id = suggestion_ids[0] if suggestion_ids else None
    print(f"\n── Step 7: Candidate selects suggestion {str(first_id)[:8]}...")
    resp = candidate_client.patch(
        f'/api/jobs/suggestions/{first_id}/toggle/',
        data={'is_selected': True},
        content_type='application/json',
    )
    d = _json(resp)
    check("toggle select → 200",            resp.status_code == 200, results)
    check("is_selected becomes True",       d.get('suggestion', {}).get('is_selected') is True, results)
    check("selected_at timestamp set",      d.get('suggestion', {}).get('selected_at') is not None, results)

    # ── Step 8: Toggle (deselect) same suggestion ─────────────────────────────
    print("\n── Step 8: Candidate deselects the same suggestion")
    resp = candidate_client.patch(
        f'/api/jobs/suggestions/{first_id}/toggle/',
        data={'is_selected': False},
        content_type='application/json',
    )
    d = _json(resp)
    check("toggle deselect → 200",          resp.status_code == 200, results)
    check("is_selected becomes False",      d.get('suggestion', {}).get('is_selected') is False, results)

    # ── Step 9: Bulk-select first 3 suggestions ───────────────────────────────
    print("\n── Step 9: Candidate bulk-selects first 3 suggestions")
    resp = candidate_client.post(
        '/api/jobs/suggestions/bulk_select/',
        data={'suggestion_ids': suggestion_ids[:3]},
        content_type='application/json',
    )
    d = _json(resp)
    check("bulk_select → 200",              resp.status_code == 200, results)
    check("3 suggestions updated",          d.get('updated_count') == 3, results)

    # Verify via list
    resp = candidate_client.get('/api/jobs/suggestions/')
    d = _json(resp)
    check("3 suggestions now selected",     d.get('summary', {}).get('selected') == 3, results)

    # ── Step 10: Filter by status=selected ───────────────────────────────────
    print("\n── Step 10: Filter by status=selected")
    resp = candidate_client.get('/api/jobs/suggestions/?status=selected')
    d = _json(resp)
    check("selected filter → 200",          resp.status_code == 200, results)
    check("3 in selected filter",           d.get('summary', {}).get('total') == 3, results)

    # ── Step 11: Submit selected roles ────────────────────────────────────────
    print("\n── Step 11: Candidate submits selected roles")
    resp = candidate_client.post('/api/jobs/suggestions/submit/')
    d = _json(resp)
    check("submit → 200",                   resp.status_code == 200, results)
    check("3 roles submitted",              d.get('count') == 3, results)
    check("submitted_at returned",          d.get('submitted_at') is not None, results)

    # Verify submitted count in list
    resp = candidate_client.get('/api/jobs/suggestions/?status=submitted')
    d = _json(resp)
    check("3 in submitted filter",          d.get('summary', {}).get('submitted') == 3, results)

    # ── Step 12: Admin views client's suggestions via profile endpoint ─────────
    print(f"\n── Step 12: Admin views suggestions for profile {str(candidate_profile.id)[:8]}...")
    resp = admin_client.get(f'/api/users/profiles/{candidate_profile.id}/role-suggestions/')
    d = _json(resp)
    check("admin profile suggestions → 200", resp.status_code == 200, results)
    check("admin sees total == 4",           d.get('summary', {}).get('total') == 4, results)
    check("admin sees selected == 3",        d.get('summary', {}).get('selected') == 3, results)
    check("admin sees submitted == 3",       d.get('summary', {}).get('submitted') == 3, results)
    check("profile_id matches",              d.get('user', {}).get('profile_id') == str(candidate_profile.id), results)
    check("suggestions list present",        len(d.get('suggestions', [])) == 4, results)

    # ── Step 13: Submit with nothing selected → 400 ───────────────────────────
    print("\n── Step 13: Submit with no selected roles → 400")
    UserRoleSuggestion.objects.filter(user=candidate_user).update(is_selected=False, selected_at=None)
    resp = candidate_client.post('/api/jobs/suggestions/submit/')
    check("submit with 0 selected → 400",   resp.status_code == 400, results)

    # ── Step 14: Recruiter cannot access another user's suggestions ───────────
    print("\n── Step 14: Recruiter cannot bulk_create (admin-only endpoint)")
    recruiter_client = get_client('recruiter', 'test123')
    resp = recruiter_client.post(
        '/api/jobs/suggestions/bulk_create/',
        data={'user_id': candidate_user.id, 'role_titles': ['PM']},
        content_type='application/json',
    )
    check("non-admin bulk_create → 403",    resp.status_code == 403, results)

    passed = sum(results)
    total  = len(results)
    print(f"\n  Results: {passed} passed, {total - passed} failed")
    return passed, total - passed


# =============================================================================
# TEST 2 – RECRUITER ASSIGNMENT & REASSIGNMENT FLOW
# =============================================================================

def test_recruiter_assignment(fx):
    section("RECRUITER ASSIGNMENT & REASSIGNMENT FLOW")
    results = []

    recruiter_obj = fx['recruiter_obj']
    teamlead_obj  = fx['teamlead_obj']
    admin_client  = get_client('admin', 'admin123')

    candidate2_user, candidate2_profile = create_candidate2()

    try:
        # ── Step 1: Assign candidate2 to recruiter ───────────────────────────
        print(f"\n── Step 1: Admin assigns candidate2 to {recruiter_obj.name}")
        resp = admin_client.post(
            '/api/recruiters/assign/',
            data={
                'profile_id':   str(candidate2_profile.id),
                'recruiter_id': str(recruiter_obj.id),
                'status':       'active',
                'priority':     'high',
            },
            content_type='application/json',
        )
        d = _json(resp)
        check("first assignment → 201",     resp.status_code == 201, results)
        assignment1_id = d.get('id')
        check("assignment id returned",     assignment1_id is not None, results)
        check("status == active",           d.get('status') == 'active', results)
        check("role defaults to primary",   d.get('role') == 'primary', results)
        check("profile matches",            str(d.get('profile')) == str(candidate2_profile.id), results)

        # ── Step 2: Duplicate assignment → 409 ───────────────────────────────
        print("\n── Step 2: Duplicate assignment (same client + same recruiter) → 409")
        resp = admin_client.post(
            '/api/recruiters/assign/',
            data={
                'profile_id':   str(candidate2_profile.id),
                'recruiter_id': str(recruiter_obj.id),
            },
            content_type='application/json',
        )
        check("duplicate → 409 Conflict",   resp.status_code == 409, results)

        # ── Step 3: Assign candidate2 to team lead (multi-assign) ────────────
        print(f"\n── Step 3: Assign same client to team lead ({teamlead_obj.name}) — multi-recruit")
        resp = admin_client.post(
            '/api/recruiters/assign/',
            data={
                'profile_id':   str(candidate2_profile.id),
                'recruiter_id': str(teamlead_obj.id),
                'priority':     'medium',
            },
            content_type='application/json',
        )
        d = _json(resp)
        check("second recruiter → 201",     resp.status_code == 201, results)
        assignment2_id = d.get('id')
        check("different assignment id",    assignment2_id != assignment1_id, results)

        # ── Step 4: List assignments for candidate2 ───────────────────────────
        print(f"\n── Step 4: List all assignments for candidate2")
        resp = admin_client.get(f'/api/recruiters/assignments/?profile_id={candidate2_profile.id}')
        d = _json(resp)
        check("list assignments → 200",     resp.status_code == 200, results)
        all_assign = _list(d)
        active = [a for a in all_assign if a.get('status') == 'active']
        check("candidate2 has 2 active",    len(active) == 2, results)
        r_ids = [str(a.get('recruiter', {}).get('id', '')) for a in active]
        check("recruiter in list",          str(recruiter_obj.id) in r_ids, results)
        check("teamlead in list",           str(teamlead_obj.id) in r_ids, results)

        # ── Step 5: Filter by recruiter_id ────────────────────────────────────
        print(f"\n── Step 5: Filter assignments by recruiter_id")
        resp = admin_client.get(
            f'/api/recruiters/assignments/?recruiter_id={recruiter_obj.id}&status=active'
        )
        d = _json(resp)
        check("filter by recruiter_id → 200", resp.status_code == 200, results)
        filtered = _list(d)
        check("at least 1 result",          len(filtered) >= 1, results)
        # Confirm candidate2's assignment is in the results
        profiles_in_result = [str(a.get('profile')) for a in filtered]
        check("candidate2 in filtered list", str(candidate2_profile.id) in profiles_in_result, results)

        # ── Step 6: Filter by role ────────────────────────────────────────────
        print("\n── Step 6: Filter assignments by role=primary")
        resp = admin_client.get('/api/recruiters/assignments/?role=primary&status=active')
        d = _json(resp)
        check("filter by role → 200",       resp.status_code == 200, results)
        role_filtered = _list(d)
        check("all returned are primary",   all(a.get('role') == 'primary' for a in role_filtered), results)

        # ── Step 7: Mark recruiter as absent ──────────────────────────────────
        print(f"\n── Step 7: Admin marks {recruiter_obj.name} as absent via PATCH /api/recruiters/<id>/")
        resp = admin_client.patch(
            f'/api/recruiters/{recruiter_obj.id}/',
            data={'availability_status': 'absent'},
            content_type='application/json',
        )
        d = _json(resp)
        check("PATCH recruiter → 200",                  resp.status_code == 200, results)
        check("availability_status = absent",            d.get('availability_status') == 'absent', results)

        # Confirm DB
        recruiter_obj.refresh_from_db()
        check("DB: availability_status = absent",        recruiter_obj.availability_status == 'absent', results)

        # ── Step 8: Absent recruiter cannot be assigned new clients ──────────
        print("\n── Step 8: Absent recruiter rejected for new assignment → 400")
        # Create a temporary third candidate
        temp_user, created = User.objects.get_or_create(
            username='cand_temp_test',
            defaults={'email': 'candtemp@test.local', 'first_name': 'Temp', 'last_name': 'Cand'}
        )
        temp_user.set_password('test123')
        temp_user.is_active = True
        temp_user.save(update_fields=['password', 'is_active'])
        temp_profile, _ = Profile.objects.get_or_create(
            user=temp_user,
            defaults={
                'first_name': 'Temp', 'last_name': 'Cand',
                'email': 'candtemp@test.local', 'phone': '9998887776',
                'active': True, 'registration_status': 'approved',
            }
        )

        resp = admin_client.post(
            '/api/recruiters/assign/',
            data={
                'profile_id':   str(temp_profile.id),
                'recruiter_id': str(recruiter_obj.id),
            },
            content_type='application/json',
        )
        check("absent recruiter → 400 Bad Request", resp.status_code == 400, results)
        temp_user.delete()  # Cleanup temporary user

        # ── Step 9: Mark recruiter available again ────────────────────────────
        print(f"\n── Step 9: Admin marks {recruiter_obj.name} available again")
        resp = admin_client.patch(
            f'/api/recruiters/{recruiter_obj.id}/',
            data={'availability_status': 'available'},
            content_type='application/json',
        )
        d = _json(resp)
        check("recruiter marked available",  d.get('availability_status') == 'available', results)

        # ── Step 10: Reassign candidate2 from recruiter to teamlead ──────────
        # First, put the existing teamlead assignment on hold so UniqueConstraint isn't violated
        # (candidate2 already has active assignment to teamlead from step 3)
        tl_assign = Assignment.objects.filter(
            profile=candidate2_profile, recruiter=teamlead_obj, status='active'
        ).first()
        if tl_assign:
            tl_assign.status = 'on_hold'
            tl_assign.save(update_fields=['status'])

        recruiter_assign = Assignment.objects.get(
            profile=candidate2_profile, recruiter=recruiter_obj, status='active'
        )

        print(f"\n── Step 10: Reassign candidate2 from {recruiter_obj.name} → {teamlead_obj.name}")
        resp = admin_client.post(
            f'/api/recruiters/assignments/{recruiter_assign.id}/reassign/',
            data={
                'new_recruiter_id': str(teamlead_obj.id),
                'reason': 'Recruiter overloaded — transferring to team lead for specialist handling',
                'role': 'primary',
            },
            content_type='application/json',
        )
        d = _json(resp)
        check("reassign → 201 Created",     resp.status_code == 201, results)
        new_assign_id = d.get('id')
        check("new assignment id returned", new_assign_id is not None, results)
        check("new recruiter is teamlead",  str(d.get('recruiter', {}).get('id')) == str(teamlead_obj.id), results)
        check("new assignment status=active", d.get('status') == 'active', results)
        check("reassigned_from_id set",     d.get('reassigned_from_id') is not None, results)
        check("reassignment_reason stored", bool(d.get('reassignment_reason')), results)

        # Verify old assignment is now 'reassigned'
        recruiter_assign.refresh_from_db()
        check("old assignment → reassigned", recruiter_assign.status == 'reassigned', results)
        check("reason saved on old assign", bool(recruiter_assign.reassignment_reason), results)

        # ── Step 11: Verify all statuses in list ──────────────────────────────
        print("\n── Step 11: Verify assignment history for candidate2")
        resp = admin_client.get(f'/api/recruiters/assignments/?profile_id={candidate2_profile.id}')
        d = _json(resp)
        all_statuses = [a.get('status') for a in _list(d)]
        check("'reassigned' in statuses",    'reassigned' in all_statuses, results)
        check("'active' in statuses",        'active' in all_statuses, results)

        # ── Step 12: Re-reassign an already-reassigned assignment → 400 ────────
        print("\n── Step 12: Attempt to re-reassign an already-reassigned assignment → 400")
        resp = admin_client.post(
            f'/api/recruiters/assignments/{recruiter_assign.id}/reassign/',
            data={
                'new_recruiter_id': str(teamlead_obj.id),
                'reason': 'Trying to re-reassign',
            },
            content_type='application/json',
        )
        check("re-reassign closed assign → 400", resp.status_code == 400, results)

    finally:
        cleanup_candidate2()
        # Ensure recruiter is always restored to available
        Recruiter.objects.filter(id=recruiter_obj.id).update(availability_status='available')

    passed = sum(results)
    total  = len(results)
    print(f"\n  Results: {passed} passed, {total - passed} failed")
    return passed, total - passed


# =============================================================================
# TEST 3 – PRIVATE ADDON (PER-CLIENT SCOPED VISIBILITY)
# =============================================================================

def test_private_addon(fx):
    section("PRIVATE ADDON – PER-CLIENT SCOPED VISIBILITY")
    results = []

    candidate_profile = fx['candidate_profile']
    admin_client      = get_client('admin', 'admin123')
    candidate_client  = get_client('candidate', 'test123')
    recruiter_client  = get_client('recruiter', 'test123')

    new_plan = create_test_addon_plan()

    try:
        # ── Step 1: Plan is publicly visible before it's made private ─────────
        print(f"\n── Step 1: '{new_plan.name}' is public (not private yet)")
        resp = recruiter_client.get('/api/subscriptions/plans/?plan_type=addon')
        d = _json(resp)
        names = [p.get('name') for p in _list(d)]
        check("plan visible to all before assign", new_plan.name in names, results)

        # ── Step 2: Admin assigns addon to candidate at custom price ──────────
        print(f"\n── Step 2: Admin assigns '{new_plan.name}' to candidate at custom price $49.99")
        resp = admin_client.post(
            '/api/subscriptions/admin/subscriptions/assign-addon/',
            data={
                'profile_id':          str(candidate_profile.id),
                'plan_id':             str(new_plan.id),
                'custom_price':        '49.99',
                'billing_cycle':       'monthly',
                'admin_notes':         'Special discounted addon for this client only',
                'activate_immediately': True,
            },
            content_type='application/json',
        )
        d = _json(resp)
        check("assign-addon → 201 Created", resp.status_code == 201, results)
        subscription_id = d.get('id')
        check("subscription id returned",   subscription_id is not None, results)
        check("custom price = 49.99",       str(d.get('price', '')) == '49.99', results)
        check("status = active",            d.get('status') == 'active', results)

        # Verify DB state
        new_plan.refresh_from_db()
        check("plan is now is_private=True",
              new_plan.is_private is True, results)
        check("candidate in allowed_profiles",
              new_plan.allowed_profiles.filter(id=candidate_profile.id).exists(), results)

        # ── Step 3: Candidate sees the private plan in their addon list ────────
        print(f"\n── Step 3: Candidate sees '{new_plan.name}' in their addon list")
        resp = candidate_client.get('/api/subscriptions/plans/?plan_type=addon')
        d = _json(resp)
        names = [p.get('name') for p in _list(d)]
        check("candidate sees private addon", new_plan.name in names, results)

        # ── Step 4: Recruiter does NOT see the private plan ────────────────────
        print(f"\n── Step 4: Recruiter does NOT see '{new_plan.name}'")
        resp = recruiter_client.get('/api/subscriptions/plans/?plan_type=addon')
        d = _json(resp)
        names = [p.get('name') for p in _list(d)]
        check("recruiter cannot see private addon", new_plan.name not in names, results)

        # ── Step 5: Anonymous user does NOT see it ────────────────────────────
        print(f"\n── Step 5: Anonymous user does NOT see '{new_plan.name}'")
        anon_client = DjangoClient()
        resp = anon_client.get('/api/subscriptions/plans/?plan_type=addon')
        d = _json(resp)
        names = [p.get('name') for p in _list(d)]
        check("anonymous cannot see private addon", new_plan.name not in names, results)

        # ── Step 6: Custom price in candidate's my-subscriptions ──────────────
        print("\n── Step 6: Custom price stored correctly on candidate's subscription")
        resp = candidate_client.get('/api/subscriptions/my-subscriptions/')
        d = _json(resp)
        subs = _list(d) if isinstance(d, list) else d.get('results', [])
        matched_sub = next(
            (s for s in subs
             if isinstance(s, dict)
             and s.get('plan_details', {}).get('name') == new_plan.name),
            None
        )
        check("addon appears in my-subscriptions", matched_sub is not None, results)
        check("price = 49.99 (custom, not base 99.00)",
              str((matched_sub or {}).get('price', '')) == '49.99', results)
        check("subscription status = active",
              (matched_sub or {}).get('status') == 'active', results)

        # ── Step 7: Admin can see the subscription in admin subscriptions ───────
        print("\n── Step 7: Admin sees new subscription in admin list")
        resp = admin_client.get(
            f'/api/subscriptions/admin/subscriptions/?profile={candidate_profile.id}'
        )
        d = _json(resp)
        admin_subs = d if isinstance(d, list) else d.get('results', [])
        matched_admin_sub = next(
            (s for s in admin_subs
             if isinstance(s, dict)
             and s.get('plan_details', {}).get('name') == new_plan.name),
            None
        )
        check("admin can see the new subscription", matched_admin_sub is not None, results)

        # ── Step 8: Duplicate assign-addon for same client + same plan → 400 ───
        print("\n── Step 8: Duplicate assign-addon (same client + same plan) → 400")
        resp = admin_client.post(
            '/api/subscriptions/admin/subscriptions/assign-addon/',
            data={
                'profile_id':   str(candidate_profile.id),
                'plan_id':      str(new_plan.id),
                'custom_price': '79.99',
            },
            content_type='application/json',
        )
        check("duplicate assign-addon → 400", resp.status_code == 400, results)

        # ── Step 9: Invalid profile_id → 400 ─────────────────────────────────
        print("\n── Step 9: assign-addon with invalid profile_id → 400")
        import uuid
        resp = admin_client.post(
            '/api/subscriptions/admin/subscriptions/assign-addon/',
            data={
                'profile_id':   str(uuid.uuid4()),
                'plan_id':      str(new_plan.id),
                'custom_price': '49.99',
            },
            content_type='application/json',
        )
        check("unknown profile_id → 400", resp.status_code == 400, results)

        # ── Step 10: Non-addon plan type → 400 ───────────────────────────────
        print("\n── Step 10: assign-addon with a base plan (not addon) → 400")
        base_plan = SubscriptionPlan.objects.filter(plan_type='base', is_active=True).first()
        if base_plan:
            resp = admin_client.post(
                '/api/subscriptions/admin/subscriptions/assign-addon/',
                data={
                    'profile_id':   str(candidate_profile.id),
                    'plan_id':      str(base_plan.id),
                    'custom_price': '49.99',
                },
                content_type='application/json',
            )
            check("base plan type → 400", resp.status_code == 400, results)
        else:
            print("  ⚠️  No base plan found — skipping step 10")

    finally:
        cleanup_test_addon_plan()

    passed = sum(results)
    total  = len(results)
    print(f"\n  Results: {passed} passed, {total - passed} failed")
    return passed, total - passed


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 58)
    print("  HYRIND – NEW FEATURE API TEST SUITE")
    print("=" * 58)
    print("  Covers: Role Suggestions · Recruiter Assignment · Private Addon")

    # Refresh base test data
    print("\n🔄  Refreshing base test data via create_test_data.py ...")
    import create_test_data as ctd
    ctd.main()

    fx = load_fixture()

    totals = []
    totals.append(test_role_suggestions(fx))
    totals.append(test_recruiter_assignment(fx))
    totals.append(test_private_addon(fx))

    total_passed = sum(t[0] for t in totals)
    total_failed = sum(t[1] for t in totals)
    grand_total  = total_passed + total_failed

    print(f"\n{'=' * 58}")
    print(f"  GRAND TOTAL: {total_passed} passed,  {total_failed} failed  (of {grand_total})")
    if total_failed == 0:
        print("  🎉 ALL TESTS PASSED")
    else:
        print(f"  ⚠️   {total_failed} TESTS FAILED — see ❌ lines above")
    print(f"{'=' * 58}")

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == '__main__':
    main()
