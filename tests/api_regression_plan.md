# API Regression Plan (Backend)

## Goal
Validate all critical endpoints after recent changes:
- Private add-on subscriptions (per-client visibility)
- Multi-recruiter assignments per client
- Existing subscription and recruiter flows continue to work

## Environments
- Local dev: http://127.0.0.1:8000
- Admin credentials: admin@hyrind.com / admin123
- Candidate credentials: candidate@test.com / test123
- Recruiter credentials: recruiter@test.com / test123
- Team lead credentials: teamlead@test.com / test123

## Test Data Setup
Run test data script (creates admin/candidate/recruiter/team lead, plans, subscriptions, assignments):
- create_test_data.py

Expected data:
- Base plan + public add-on + private add-on
- Candidate has base + public add-on + private add-on (discounted)
- Private add-on allowed_profiles includes candidate
- Candidate assigned to two recruiters (recruiter + team lead)

## Auth Tokens
- Obtain JWT/token using your auth endpoint (see API docs). Save:
  - ADMIN_TOKEN
  - CANDIDATE_TOKEN
  - RECRUITER_TOKEN
  - TEAMLEAD_TOKEN

## Subscription Plans (Public + Private Visibility)
1) Public plans (anonymous)
- GET /api/subscriptions/plans/
  - Expect: base + public add-on only
- GET /api/subscriptions/plans/addons/
  - Expect: public add-ons only (private excluded)

2) Authenticated candidate
- GET /api/subscriptions/plans/
  - Expect: base + public add-on + private add-on (allowed)
- GET /api/subscriptions/plans/addons/
  - Expect: public add-ons + private add-on

3) Authenticated non-allowed user (any other client)
- GET /api/subscriptions/plans/addons/
  - Expect: private add-on NOT included

## Admin Subscription Management
- POST /api/subscriptions/admin/subscriptions/
  - Create add-on for candidate with custom price
  - Verify created and price stored
- GET /api/subscriptions/admin/subscriptions/?profile_id=<candidate_profile_id>
  - Expect multiple subscriptions (base + add-ons)

## My Subscriptions (Candidate)
- GET /api/subscriptions/my-subscriptions/
  - Expect base + add-ons
- GET /api/subscriptions/my-subscriptions/summary/
  - Expect base_subscription + addons list

## Assignments
1) Admin assigns multiple recruiters
- POST /api/recruiters/assign/
  - Assign candidate to recruiter
  - Assign same candidate to team lead
  - Expect 201 both times

2) Prevent duplicates
- POST /api/recruiters/assign/ with same recruiter
  - Expect 409 (already actively assigned)

3) Capacity check
- Assign recruiter beyond max_clients
  - Expect 400 (capacity reached)

## Client Lists / Profiles
- GET /api/clients/?has_recruiter=true
  - Expect candidate included
- GET /api/clients/?has_recruiter=false
  - Expect candidate excluded
- GET /api/clients/profiles/?has_recruiter=true
  - Expect candidate included

## Recruiter Dashboard
- GET /api/recruiters/dashboard/
  - Expect assigned candidates list includes candidate

## Regression Notes
- Ensure existing endpoints still work with new assignment relationship.
- Validate `assignment_statuses` and `recruiter_infos` appear in client profile APIs.

## Reporting
Log results with:
- Endpoint
- Method
- Auth
- Status code
- Key assertions (include/omit private add-on, multi-assignments)
