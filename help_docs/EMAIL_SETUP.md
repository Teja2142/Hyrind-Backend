# Email Notification Setup

## Overview
The system sends email notifications to `hyrind.operations@gmail.com` whenever someone submits an interest form.

## Configuration

### 1. Set up Gmail App Password

Since Gmail requires 2-factor authentication, you need to create an **App Password**:

1. Go to your Google Account: https://myaccount.google.com/
2. Select **Security** from the left menu
3. Under "How you sign in to Google," select **2-Step Verification** (set it up if not already enabled)
4. At the bottom of the page, select **App passwords**
5. Select "Mail" as the app and choose your device
6. Click **Generate**
7. Copy the 16-character password (it will look like: `xxxx xxxx xxxx xxxx`)

### 2. Create .env file

Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

### 3. Update .env with your credentials

Edit the `.env` file and add your email credentials:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # The app password from step 1
DEFAULT_FROM_EMAIL=your-email@gmail.com
OPERATIONS_EMAIL=hyrind.operations@gmail.com
```

### 4. Load environment variables

Make sure your Django settings loads the `.env` file. If using `python-dotenv`:

```python
# In settings.py
from dotenv import load_dotenv
load_dotenv()
```

Or install it:
```bash
pip install python-dotenv
```

## Email Content

When an interest form is submitted, the operations team receives an email with:
- Candidate's full name, email, and phone
- Education details (university, degree, major, graduation date)
- Visa status and OPT end date
- Referral source, LinkedIn, GitHub URLs
- Any additional notes provided
- Resume file indication
- Submission timestamp

## Testing Email Setup

### Option 1: Console Backend (Development)
For local testing without sending real emails, use the console backend:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails will be printed to the console instead of being sent.

### Option 2: Send Test Email (Production)

Run this in Django shell:
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test Email - Hyrind Interest Form',
    message='This is a test email from the Hyrind backend.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[settings.OPERATIONS_EMAIL],
    fail_silently=False,
)
```

## Troubleshooting

### Email not sending
1. **Check Gmail settings**: Ensure 2FA is enabled and App Password is created
2. **Check credentials**: Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env`
3. **Check firewall**: Ensure port 587 is not blocked
4. **Check spam folder**: First emails may go to spam

### Error: "Username and Password not accepted"
- You're likely using your regular Gmail password instead of an App Password
- Generate a new App Password following step 1 above

### Error: "SMTPAuthenticationError"
- Double-check your email and app password
- Make sure there are no extra spaces in the `.env` file
- Try regenerating the app password

### Using other email providers

#### SendGrid:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

#### AWS SES:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-aws-access-key
EMAIL_HOST_PASSWORD=your-aws-secret-key
```

## Error Handling

The email notification is designed to **fail silently** (`fail_silently=True`). This means:
- If email sending fails, the interest form submission will still succeed
- Users won't see an error even if email fails
- Errors are logged to console for debugging
- This ensures the user experience is not affected by email issues

To see email errors in production, check your application logs.
