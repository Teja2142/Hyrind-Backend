# Field Validations, Choices, and Security

## Client Intake Sheet Field Validations

- **first_name, last_name**: Required, max 100 chars
- **date_of_birth**: Required, valid date (YYYY-MM-DD)
- **phone_number**: Required, max 20 chars
- **email**: Required, valid email
- **alternate_email**: Optional, valid email
- **current_address, mailing_address**: Required, text
- **visa_status**: Required, choices: F1-OPT, H1B, H4 EAD, Green Card, US Citizen, Other
- **first_entry_us**: Required, valid date
- **total_years_in_us**: Required, integer
- **skilled_in, experienced_with**: Required, text
- **currently_learning, learning_tools, non_technical_skills**: Optional, text
- **job_1/job_2/job_3 fields**: Optional, text/date, job_type choices: Full-time, Part-time, Internship
- **highest_degree, bachelors_degree**: Optional, choices: Bachelor's, Master's, PhD, Diploma, Other
- **certification_name, issuing_organization, issued_date**: Optional, text/date
- **passport_file, government_id_file, visa_file, work_authorization_file, resume_file**: Optional, file upload (PDF, DOCX, JPG, PNG recommended)
- **desired_job_role, desired_years_experience**: Optional, text
- **is_editable**: Boolean, default True

## Credential Sheet Field Validations

- **full_name, personal_email, phone_number, location**: Required, valid formats
- **bachelor_graduation_date, first_entry_us**: Required, valid date
- **masters_graduation_date, opt_start_date**: Optional, valid date
- **opt_offer_letter_submitted**: Optional, choices: Yes, No
- **opt_offer_letter_file**: Optional, file upload (PDF, DOCX, JPG, PNG recommended)
- **preferred_job_roles, preferred_locations**: Required, text
- **platform_username/password fields**: Optional, max 100/255 chars, passwords masked in API responses
- **other_job_platform_accounts**: Optional, text
- **is_editable**: Boolean, default True

## Security Practices

- **Authentication**: All endpoints require JWT authentication
- **Authorization**: Users can only access their own forms; admins can access all
- **Password Masking**: All credential passwords are masked as "••••••" in API responses
- **Password Storage**: Passwords are stored as plain text (recommend encryption in future)
- **File Uploads**: Files are stored in organized directories; recommend virus scanning and file type validation
- **Data Integrity**: One form per user (OneToOne with Profile)
- **Edit Locking**: Forms can be locked (is_editable=False) to prevent further edits

## Choices Reference

- **Visa Status**: F1-OPT, H1B, H4 EAD, Green Card, US Citizen, Other
- **Job Type**: Full-time, Part-time, Internship
- **Degree**: Bachelor's, Master's, PhD, Diploma, Other
- **OPT Offer Letter Submitted**: Yes, No

---

For more details, see the model docstrings in users/models.py and the API documentation in help_docs/CLIENT_FORMS_API.md.
