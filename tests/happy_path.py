import requests
import os
BASE = 'http://127.0.0.1:8000'

# 1) Register
password = 'TestPass123!'
files = {'resume': open('tests/sample_resume.txt','rb')}
data = {
    'email': 'test@example.com',
    'password': password,
    'confirm_password': password,
    'first_name': 'Test',
    'last_name': 'User',
    'phone': '1234567890',
    'terms_accepted': 'true'
}
print('Registering...')
r = requests.post(BASE + '/api/users/register/', data=data, files=files)
print('Status', r.status_code, r.text)

# 2) Login
print('Logging in...')
r = requests.post(BASE + '/api/users/login/', json={'email': 'test@example.com', 'password': password})
print('Status', r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit('Login failed')
access = r.json()['access']
headers = {'Authorization': f'Bearer {access}'}

# Grab profile_id returned from registration
profile_id = None
try:
    profile_id = r = requests.post(BASE + '/api/users/register/', data=data, files=files).json().get('profile_id')
except Exception:
    pass
if not profile_id:
    # try to parse from earlier response
    try:
        import json
        profile_id = json.loads(r.text).get('profile_id')
    except Exception:
        pass
if not profile_id:
    print('Warning: profile_id not found; defaulting to 1')
    profile_id = 1

# 3) Create onboarding
print('Creating onboarding...')
r = requests.post(BASE + '/api/onboarding/', json={'profile': profile_id}, headers=headers)
print('Status', r.status_code, r.text)

# 4) Mark onboarding step complete
print('Marking onboarding step complete...')
r = requests.patch(BASE + "/api/onboarding/1/", json={'step': 'profile'}, headers=headers)
print('Status', r.status_code, r.text)

# 5) Create subscription (mock)
print('Creating subscription...')
r = requests.post(BASE + '/api/subscriptions/', json={'profile': profile_id, 'plan': 'basic'}, headers=headers)
print('Status', r.status_code, r.text)

# 6) Assign recruiter (admin) - requires admin token, skipping here
print('Happy path test complete')
