"""
Test scripts for Client Intake Sheet and Credential Sheet APIs
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = 'http://localhost:8000/api'
ADMIN_EMAIL = 'admin@hyrind.com'
ADMIN_PASSWORD = 'admin_password'
CLIENT_EMAIL = 'client@example.com'
CLIENT_PASSWORD = 'client_password'

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def get_token(email, password):
    """Get JWT token for user"""
    response = requests.post(
        f'{BASE_URL}/token/',
        json={'email': email, 'password': password}
    )
    if response.status_code == 200:
        return response.json()['access']
    return None

def test_intake_sheet_create(token):
    """Test creating a Client Intake Sheet"""
    print(f"\n{Colors.BLUE}Testing Client Intake Sheet Creation...{Colors.END}")
    
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0123",
        "current_employment_status": "employed",
        "current_company": "Tech Corp",
        "current_job_title": "Senior Software Engineer",
        "total_experience_years": 7,
        "highest_degree": "Bachelor's",
        "university": "Stanford University",
        "graduation_date": "2019-05-15",
        "desired_role": "software_engineer",
        "desired_location": "San Francisco, CA",
        "willing_to_relocate": True,
        "salary_expectation": "150k_200k",
        "notice_period_days": 14,
        "available_to_start": future_date,
        "key_skills": "Python, JavaScript, Docker, Kubernetes",
        "programming_languages": "Python, JavaScript, Go, Rust",
        "frameworks_tools": "Django, React, FastAPI, Spring Boot",
        "portfolio_url": "https://johndoe.com",
        "github_url": "https://github.com/johndoe",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "job_type_preferences": "Full-time",
        "remote_preference": "hybrid",
        "visa_status": "Citizen",
        "can_sponsor_required": False,
        "additional_notes": "Looking for growth opportunities in AI/ML and cloud architecture"
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'{BASE_URL}/clients/intake-sheets/',
        json=payload,
        headers=headers
    )
    
    if response.status_code == 201:
        print(f"{Colors.GREEN}✓ Client Intake Sheet created successfully{Colors.END}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return response.json()['id']
    else:
        print(f"{Colors.RED}✗ Failed to create intake sheet{Colors.END}")
        print(f"  Status: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_intake_sheet_retrieve(token, sheet_id):
    """Test retrieving a Client Intake Sheet"""
    print(f"\n{Colors.BLUE}Testing Client Intake Sheet Retrieval...{Colors.END}")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/clients/intake-sheets/{sheet_id}/',
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"{Colors.GREEN}✓ Client Intake Sheet retrieved successfully{Colors.END}")
        data = response.json()
        print(f"  Name: {data.get('full_name')}")
        print(f"  Email: {data.get('email')}")
        print(f"  Desired Role: {data.get('desired_role')}")
        print(f"  Status: {data.get('current_employment_status')}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to retrieve intake sheet{Colors.END}")
        print(f"  Status: {response.status_code}")
        return False

def test_intake_sheet_update(token, sheet_id):
    """Test updating a Client Intake Sheet"""
    print(f"\n{Colors.BLUE}Testing Client Intake Sheet Update...{Colors.END}")
    
    payload = {
        "desired_location": "New York, NY",
        "salary_expectation": "120k_150k",
        "remote_preference": "remote"
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.patch(
        f'{BASE_URL}/clients/intake-sheets/{sheet_id}/',
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"{Colors.GREEN}✓ Client Intake Sheet updated successfully{Colors.END}")
        data = response.json()
        print(f"  Updated Location: {data.get('desired_location')}")
        print(f"  Updated Salary: {data.get('salary_expectation')}")
        print(f"  Updated Remote: {data.get('remote_preference')}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to update intake sheet{Colors.END}")
        print(f"  Status: {response.status_code}")
        return False

def test_credential_sheet_create(token):
    """Test creating a Credential Sheet"""
    print(f"\n{Colors.BLUE}Testing Credential Sheet Creation...{Colors.END}")
    
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0123",
        "certifications": "AWS Certified Solutions Architect, Kubernetes Certified Application Developer",
        "certification_details": "AWS SAA - Issued by Amazon, Valid until 2027-06-15; CKAD - Issued by CNCF, Valid until 2027-03-20",
        "professional_licenses": "None",
        "has_security_clearance": False,
        "clearance_level": "none",
        "degrees_held": "Bachelor's in Computer Science, Stanford University, 2019",
        "major_field": "Computer Science",
        "gpa": "3.85",
        "cloud_certifications": "AWS Solutions Architect Associate, AWS Solutions Architect Professional, Azure Administrator Certified",
        "database_certifications": "MongoDB Certified Developer",
        "programming_certifications": "Oracle Java Programmer Associate",
        "background_check_status": "Pending",
        "work_authorization_status": "US Citizen",
        "i9_verification_status": "pending",
        "professional_references": "Jane Smith - CTO at Tech Corp, jane@techcorp.com, 555-0456; Bob Johnson - VP Engineering at StartupCo, bob@startup.com, 555-7890",
        "reference_count": 2,
        "publications": "None",
        "patents": "None",
        "awards_recognition": "Employee of the Year 2024 - Tech Corp, Outstanding Performance Award 2023",
        "background_check_consent": True,
        "reference_check_consent": True,
        "credential_verification_consent": True,
        "notes": "Ready for immediate background check and reference verification"
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'{BASE_URL}/clients/credential-sheets/',
        json=payload,
        headers=headers
    )
    
    if response.status_code == 201:
        print(f"{Colors.GREEN}✓ Credential Sheet created successfully{Colors.END}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return response.json()['id']
    else:
        print(f"{Colors.RED}✗ Failed to create credential sheet{Colors.END}")
        print(f"  Status: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_credential_sheet_retrieve(token, sheet_id):
    """Test retrieving a Credential Sheet"""
    print(f"\n{Colors.BLUE}Testing Credential Sheet Retrieval...{Colors.END}")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/clients/credential-sheets/{sheet_id}/',
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"{Colors.GREEN}✓ Credential Sheet retrieved successfully{Colors.END}")
        data = response.json()
        print(f"  Name: {data.get('full_name')}")
        print(f"  Email: {data.get('email')}")
        print(f"  Security Clearance: {data.get('has_security_clearance')}")
        print(f"  I-9 Status: {data.get('i9_verification_status')}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to retrieve credential sheet{Colors.END}")
        print(f"  Status: {response.status_code}")
        return False

def test_credential_sheet_update(token, sheet_id):
    """Test updating a Credential Sheet"""
    print(f"\n{Colors.BLUE}Testing Credential Sheet Update...{Colors.END}")
    
    payload = {
        "has_security_clearance": True,
        "clearance_level": "secret",
        "i9_verification_status": "verified",
        "background_check_status": "Completed"
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.patch(
        f'{BASE_URL}/clients/credential-sheets/{sheet_id}/',
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"{Colors.GREEN}✓ Credential Sheet updated successfully{Colors.END}")
        data = response.json()
        print(f"  Updated Clearance: {data.get('has_security_clearance')}")
        print(f"  Updated Level: {data.get('clearance_level')}")
        print(f"  Updated I-9: {data.get('i9_verification_status')}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to update credential sheet{Colors.END}")
        print(f"  Status: {response.status_code}")
        return False

def test_list_intake_sheets(token):
    """Test listing Client Intake Sheets"""
    print(f"\n{Colors.BLUE}Testing List Client Intake Sheets...{Colors.END}")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/clients/intake-sheets/',
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"{Colors.GREEN}✓ Client Intake Sheets listed successfully{Colors.END}")
        data = response.json()
        if isinstance(data, list):
            print(f"  Total Forms: {len(data)}")
        else:
            print(f"  Total Forms: {data.get('count', 0)}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to list intake sheets{Colors.END}")
        print(f"  Status: {response.status_code}")
        return False

def test_list_credential_sheets(token):
    """Test listing Credential Sheets"""
    print(f"\n{Colors.BLUE}Testing List Credential Sheets...{Colors.END}")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/clients/credential-sheets/',
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"{Colors.GREEN}✓ Credential Sheets listed successfully{Colors.END}")
        data = response.json()
        if isinstance(data, list):
            print(f"  Total Forms: {len(data)}")
        else:
            print(f"  Total Forms: {data.get('count', 0)}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to list credential sheets{Colors.END}")
        print(f"  Status: {response.status_code}")
        return False

def run_all_tests():
    """Run all API tests"""
    print(f"\n{Colors.YELLOW}{'='*60}")
    print(f"Client Intake & Credential Sheet API Tests")
    print(f"{'='*60}{Colors.END}")
    
    # Get token
    print(f"\n{Colors.BLUE}Authenticating...{Colors.END}")
    token = get_token(CLIENT_EMAIL, CLIENT_PASSWORD)
    
    if not token:
        print(f"{Colors.RED}✗ Failed to authenticate{Colors.END}")
        return
    
    print(f"{Colors.GREEN}✓ Authentication successful{Colors.END}")
    
    # Test Intake Sheet
    intake_id = test_intake_sheet_create(token)
    if intake_id:
        test_intake_sheet_retrieve(token, intake_id)
        test_intake_sheet_update(token, intake_id)
    
    test_list_intake_sheets(token)
    
    # Test Credential Sheet
    credential_id = test_credential_sheet_create(token)
    if credential_id:
        test_credential_sheet_retrieve(token, credential_id)
        test_credential_sheet_update(token, credential_id)
    
    test_list_credential_sheets(token)
    
    print(f"\n{Colors.YELLOW}{'='*60}")
    print(f"Tests Complete")
    print(f"{'='*60}{Colors.END}\n")

if __name__ == '__main__':
    run_all_tests()
