from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


class RegistrationAndInterestTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.interest_url = reverse('interest-submit')

    def _make_resume(self, name='resume.pdf', size=100):
        return SimpleUploadedFile(name, b"a" * size, content_type='application/pdf')

    def test_registration_success(self):
        data = {
            'email': 'cand1@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'phone': '+1-555-555-5555',
            'university': 'Example University',
            'degree': "Bachelor's",
            'major': 'Computer Science',
            'visa_status': 'F1-CPT',
            'graduation_date': '05/2026',
                'consent_to_terms': True,
                'referral_source': 'Google',
                'linkedin_url': 'https://www.linkedin.com/in/alice',
                'github_url': 'https://github.com/alice',
                'additional_notes': 'Excited to apply!'
        }
        files = {'resume_file': self._make_resume()}
        resp = self.client.post(self.register_url, data, format='multipart', files=files)
        self.assertEqual(resp.status_code, 201)
        self.assertIn('profile_id', resp.data)
        self.assertTrue(User.objects.filter(username='cand1@example.com').exists())

    def test_registration_requires_opt_end_date_on_f1_opt(self):
        data = {
            'email': 'cand2@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'phone': '+1-555-555-5555',
            'university': 'Example University',
            'degree': "Master's",
            'major': 'EE',
            'visa_status': 'F1-OPT',
            'graduation_date': '06/2025',
            'consent_to_terms': True,
            'referral_source': 'LinkedIn'
        }
        files = {'resume_file': self._make_resume()}
        resp = self.client.post(self.register_url, data, format='multipart', files=files)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('opt_end_date', resp.data)

    def test_interest_submission_success(self):
        data = {
            'first_name': 'Charlie',
            'last_name': 'Brown',
            'email': 'charlie@example.com',
            'phone': '+1-333-333-3333',
            'university': 'State U',
            'degree': "Master's",
            'major': 'Data Science',
            'visa_status': 'H1B',
            'graduation_date': '12/2023',
            'consent_to_terms': True,
        }
        files = {'resume_file': self._make_resume('resume.docx')}
        resp = self.client.post(self.interest_url, data, format='multipart', files=files)
        self.assertEqual(resp.status_code, 201)
