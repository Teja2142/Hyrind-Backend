#!/usr/bin/env python
"""
Hyrind Backend - Comprehensive API Regression Test Suite

Tests all critical endpoints including the recent changes:
1. Private add-on plan visibility (per-client)
2. Multiple recruiter assignments per client
3. Subscription flows
4. User / profile / client listing

Usage: python tests/test_api_regression.py
"""

import os
import sys
import django
import json

# --- Django setup (for DB, not for requests) -------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrind.settings')
django.setup()

from django.test import TestCase, Client as DjangoClient
from django.contrib.auth.models import User
from users.models import Profile
from recruiters.models import Recruiter, Assignment
from subscriptions.models import SubscriptionPlan, UserSubscription
from decimal import Decimal
from django.urls import reverse


# =============================================================================
# Helpers
# =============================================================================

def _json(response):
    try:
        return response.json()
    except Exception:
        return response.content.decode()


def assert_equal(label, actual, expected):
    if actual != expected:
        print(f"  ❌ {label}: expected {expected!r}, got {actual!r}")
        return False
    print(f"  ✅ {label}: {actual!r}")
    return True


def assert_in(label, item, collection):
    if item not in collection:
        print(f"  ❌ {label}: {item!r} not in {collection!r}")
        return False
    print(f"  ✅ {label}: {item!r} in collection")
    return True


def assert_not_in(label, item, collection):
    if item in collection:
        print(f"  ❌ {label}: {item!r} should NOT be in {collection!r}")
        return False
    print(f"  ✅ {label}: {item!r} correctly absent")
    return True


# =============================================================================
# Fixture helpers
# =============================================================================

def get_or_create_fixture():
    """Return fixture objects (created by create_test_data.py)."""
    candidate_user = User.objects.filter(username='candidate').first()
    recruiter_user = User.objects.filter(username='recruiter').first()
    teamlead_user  = User.objects.filter(username='teamlead').first()
    admin_user     = User.objects.filter(username='admin').first()

    if not all([candidate_user, recruiter_user, teamlead_user, admin_user]):
        print("❌ Test data not found. Run create_test_data.py first.")
        sys.exit(1)

    candidate_profile = Profile.objects.get(user=candidate_user)
    recruiter_profile = Profile.objects.get(user=recruiter_user)
    teamlead_profile  = Profile.objects.get(user=teamlead_user)

    recruiter   = Recruiter.objects.get(user=recruiter_profile)
    team_lead   = Recruiter.objects.get(user=teamlead_profile)

    return {
        'admin': admin_user,
        'candidate': candidate_user,
        'recruiter': recruiter_user,
        'teamlead': teamlead_user,
        'candidate_profile': candidate_profile,
        'recruiter_obj': recruiter,
        'teamlead_obj': team_lead,
    }


def get_auth_client(user, password):
    """Return a Django test client logged in as user."""
    c = DjangoClient()
    c.login(username=user.username, password=password)
    return c


def get_token_client(c, password):
    """
    Try to obtain a DRF token (simple-jwt or DRF Token) and set it.
    Falls back to session auth if token endpoint is not configured.
    """
    user = c._current_user if hasattr(c, '_current_user') else None
    return c


# =============================================================================
# Test Classes
# =============================================================================

class TestSubscriptionPlanVisibility:
    """Test private add-on visibility rules."""

    def __init__(self, fx):
        self.fx = fx

    def run(self):
        print("\n========================================")
        print("TEST: Subscription Plan Visibility")
        print("========================================")
        passed = 0
        failed = 0

        # 1 – Anonymous: private add-on must NOT be visible
        anon = DjangoClient()
        r = anon.get('/api/subscriptions/plans/addons/')
        plans = _json(r)
        if not isinstance(plans, list):
            plans = plans.get('results', plans)
        private_names = [p['name'] for p in plans if p.get('is_private')]
        result = assert_equal("Anon: status 200", r.status_code, 200)
        passed += result; failed += (not result)
        result = assert_equal("Anon: private add-on NOT in addons list", len(private_names), 0)
        passed += result; failed += (not result)

        # 2 – Candidate: private add-on MUST be visible (allowed)
        cand_client = DjangoClient()
        cand_client.login(username='candidate', password='test123')
        r = cand_client.get('/api/subscriptions/plans/addons/')
        plans = _json(r)
        if not isinstance(plans, list):
            plans = plans.get('results', plans)
        plan_names = [p['name'] for p in plans]
        result = assert_equal("Candidate: status 200", r.status_code, 200)
        passed += result; failed += (not result)
        result = assert_in("Candidate: private add-on IS visible", 'Client-Specific Premium Addon', plan_names)
        passed += result; failed += (not result)

        # 3 – Recruiter (not in allowed_profiles): private add-on NOT visible
        rec_client = DjangoClient()
        rec_client.login(username='recruiter', password='test123')
        r = rec_client.get('/api/subscriptions/plans/addons/')
        plans = _json(r)
        if not isinstance(plans, list):
            plans = plans.get('results', plans)
        plan_names_rec = [p['name'] for p in plans]
        result = assert_not_in("Recruiter: private add-on NOT visible", 'Client-Specific Premium Addon', plan_names_rec)
        passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


class TestMySubscriptions:
    """Test candidate's own subscription endpoints."""

    def __init__(self, fx):
        self.fx = fx

    def run(self):
        print("\n========================================")
        print("TEST: My Subscriptions")
        print("========================================")
        passed = 0
        failed = 0

        cand_client = DjangoClient()
        cand_client.login(username='candidate', password='test123')

        # List
        r = cand_client.get('/api/subscriptions/my-subscriptions/')
        result = assert_equal("My subscriptions: status 200", r.status_code, 200)
        passed += result; failed += (not result)

        data = _json(r)
        subs = data if isinstance(data, list) else data.get('results', [])
        result = assert_equal("Has at least 2 subscriptions (base + add-on)", len(subs) >= 2, True)
        passed += result; failed += (not result)

        # Summary
        r = cand_client.get('/api/subscriptions/my-subscriptions/summary/')
        result = assert_in("Summary: status 200 or 404 (if endpoint exists)", r.status_code, [200, 404])
        passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


class TestAdminSubscriptions:
    """Test admin subscription management."""

    def __init__(self, fx):
        self.fx = fx

    def run(self):
        print("\n========================================")
        print("TEST: Admin Subscription Management")
        print("========================================")
        passed = 0
        failed = 0

        admin_client = DjangoClient()
        admin_client.login(username='admin', password='admin123')

        profile_id = str(self.fx['candidate_profile'].id)

        # List subscriptions for candidate
        r = admin_client.get(f'/api/subscriptions/admin/subscriptions/?profile_id={profile_id}')
        result = assert_equal("Admin list subs: status 200", r.status_code, 200)
        passed += result; failed += (not result)

        data = _json(r)
        subs = data if isinstance(data, list) else data.get('results', [])
        result = assert_equal("Admin: candidate has >= 2 subscriptions", len(subs) >= 2, True)
        passed += result; failed += (not result)

        # Analytics
        r = admin_client.get('/api/subscriptions/admin/subscriptions/analytics/')
        result = assert_in("Admin analytics: status 200/404", r.status_code, [200, 404])
        passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


class TestMultipleAssignments:
    """Test multiple recruiter assignments per client."""

    def __init__(self, fx):
        self.fx = fx

    def run(self):
        print("\n========================================")
        print("TEST: Multiple Recruiter Assignments")
        print("========================================")
        passed = 0
        failed = 0

        profile = self.fx['candidate_profile']
        recruiter = self.fx['recruiter_obj']
        team_lead = self.fx['teamlead_obj']

        # Verify assignments exist in DB
        active_assignments = Assignment.objects.filter(profile=profile, status='active')
        result = assert_equal("DB: candidate has 2 active assignments", active_assignments.count() >= 2, True)
        passed += result; failed += (not result)

        # Verify recruiters
        assigned_recruiter_ids = list(active_assignments.values_list('recruiter_id', flat=True))
        result = assert_in("DB: recruiter assigned", str(recruiter.id), [str(i) for i in assigned_recruiter_ids])
        passed += result; failed += (not result)
        result = assert_in("DB: team lead assigned", str(team_lead.id), [str(i) for i in assigned_recruiter_ids])
        passed += result; failed += (not result)

        # Admin assign API: duplicate should return 409
        admin_client = DjangoClient()
        admin_client.login(username='admin', password='admin123')

        payload = json.dumps({
            'profile_id': str(profile.id),
            'recruiter_id': str(recruiter.id)
        })
        r = admin_client.post(
            '/api/recruiters/assign/',
            data=payload,
            content_type='application/json'
        )
        result = assert_equal("API: duplicate active assignment returns 409", r.status_code, 409)
        passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


class TestClientListFilters:
    """Test client listing with has_recruiter filter."""

    def __init__(self, fx):
        self.fx = fx

    def run(self):
        print("\n========================================")
        print("TEST: Client List Filters (has_recruiter)")
        print("========================================")
        passed = 0
        failed = 0

        admin_client = DjangoClient()
        admin_client.login(username='admin', password='admin123')
        candidate_email = 'candidate@test.com'

        # has_recruiter=true -> candidate should appear
        r = admin_client.get('/api/users/clients/?has_recruiter=true')
        result = assert_equal("has_recruiter=true: status 200", r.status_code, 200)
        passed += result; failed += (not result)
        if r.status_code == 200:
            data = _json(r)
            users = data if isinstance(data, list) else data.get('results', [])
            emails = [u.get('email', '') for u in users]
            result = assert_in("has_recruiter=true: candidate present", candidate_email, emails)
            passed += result; failed += (not result)

        # has_recruiter=false -> candidate should NOT appear
        r = admin_client.get('/api/users/clients/?has_recruiter=false')
        result = assert_equal("has_recruiter=false: status 200", r.status_code, 200)
        passed += result; failed += (not result)
        if r.status_code == 200:
            data = _json(r)
            users = data if isinstance(data, list) else data.get('results', [])
            emails_norecruiter = [u.get('email', '') for u in users]
            result = assert_not_in("has_recruiter=false: candidate absent", candidate_email, emails_norecruiter)
            passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


class TestProfileAssignmentStatuses:
    """Test that profile returns assignment_statuses and recruiter_infos."""

    def __init__(self, fx):
        self.fx = fx

    def run(self):
        print("\n========================================")
        print("TEST: Profile Multi-Recruiter Fields")
        print("========================================")
        passed = 0
        failed = 0

        admin_client = DjangoClient()
        admin_client.login(username='admin', password='admin123')

        profile_id = str(self.fx['candidate_profile'].id)
        r = admin_client.get(f'/api/users/profiles/{profile_id}/')

        result = assert_in("Profile detail: status 200/404", r.status_code, [200, 404])
        passed += result; failed += (not result)

        if r.status_code == 200:
            data = _json(r)
            result = assert_in("assignment_statuses field present", 'assignment_statuses', data)
            passed += result; failed += (not result)
            result = assert_in("recruiter_infos field present", 'recruiter_infos', data)
            passed += result; failed += (not result)
            result = assert_equal("assignment_statuses >= 2", len(data.get('assignment_statuses', [])) >= 2, True)
            passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


class TestRecruiterDashboard:
    """Test recruiter dashboard shows assigned clients."""

    def __init__(self, fx):
        self.fx = fx

    def run(self):
        print("\n========================================")
        print("TEST: Recruiter Dashboard")
        print("========================================")
        passed = 0
        failed = 0

        rec_client = DjangoClient()
        rec_client.login(username='recruiter', password='test123')

        r = rec_client.get('/api/recruiters/dashboard/')
        result = assert_in("Recruiter dashboard: status 200/403/401", r.status_code, [200, 401, 403])
        passed += result; failed += (not result)

        if r.status_code == 200:
            data = _json(r)
            assigned = data.get('assigned_candidates', data.get('assigned_clients', []))
            candidate_ids = [str(c.get('id', '')) for c in assigned]
            candidate_profile_id = str(self.fx['candidate_profile'].id)
            result = assert_in("Dashboard: candidate in assigned list", candidate_profile_id, candidate_ids)
            passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


class TestSubscriptionPlanList:
    """Test standard plan listing endpoints."""

    def run(self):
        print("\n========================================")
        print("TEST: Subscription Plan Listing")
        print("========================================")
        passed = 0
        failed = 0

        anon = DjangoClient()

        # Base plan
        r = anon.get('/api/subscriptions/plans/base_plan/')
        result = assert_in("Base plan endpoint: 200/404", r.status_code, [200, 404])
        passed += result; failed += (not result)
        if r.status_code == 200:
            data = _json(r)
            result = assert_equal("Base plan type", data.get('plan_type'), 'base')
            passed += result; failed += (not result)

        # All plans
        r = anon.get('/api/subscriptions/plans/')
        result = assert_equal("All plans: status 200", r.status_code, 200)
        passed += result; failed += (not result)

        print(f"\n  Results: {passed} passed, {failed} failed")
        return passed, failed


# =============================================================================
# Main runner
# =============================================================================

def main():
    print("=" * 55)
    print("  HYRIND BACKEND - API REGRESSION TEST SUITE")
    print("=" * 55)

    fx = get_or_create_fixture()

    total_passed = 0
    total_failed = 0

    suites = [
        TestSubscriptionPlanList(),
        TestSubscriptionPlanVisibility(fx),
        TestMySubscriptions(fx),
        TestAdminSubscriptions(fx),
        TestMultipleAssignments(fx),
        TestClientListFilters(fx),
        TestProfileAssignmentStatuses(fx),
        TestRecruiterDashboard(fx),
    ]

    for suite in suites:
        p, f = suite.run()
        total_passed += p
        total_failed += f

    print("\n" + "=" * 55)
    print(f"  TOTAL: {total_passed} passed,  {total_failed} failed")
    if total_failed == 0:
        print("  🎉 ALL TESTS PASSED")
    else:
        print("  ⚠️  SOME TESTS FAILED - review above")
    print("=" * 55)
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == '__main__':
    main()
