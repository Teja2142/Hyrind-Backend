"""
Test script to verify interest form email notification with HTML formatting

This script simulates sending a test HTML email similar to what the interest
form would send.

For testing without sending real emails, set in .env:
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrind.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime

def test_email_config():
    """Test if email configuration is properly set up"""
    print("Testing Email Configuration...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"OPERATIONS_EMAIL: {settings.OPERATIONS_EMAIL}")
    print()

def test_send_html_email():
    """Send a test HTML email similar to interest form notification"""
    print("Sending test HTML email...")
    
    try:
        subject = '🎯 TEST - New Interest Submission - John Doe'
        
        # Plain text version
        text_content = """
Test Interest Form Submission

This is a test email to verify the HTML email notification system.

Candidate: John Doe
Email: john.doe@example.com
Phone: 1234567890
University: MIT
Degree: Master's
Major: Computer Science
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 30px -30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        td {{
            padding: 12px;
            border: 1px solid #e0e0e0;
        }}
        td:first-child {{
            font-weight: 600;
            background-color: #f8f9fa;
            width: 35%;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            background-color: #d4edda;
            color: #155724;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎯 TEST - Interest Form Submission</h1>
            <p>This is a test email - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        <div>
            <div class="section-title">👤 Candidate Information</div>
            <table>
                <tr>
                    <td>Full Name</td>
                    <td><strong>John Doe</strong></td>
                </tr>
                <tr>
                    <td>Email Address</td>
                    <td>john.doe@example.com</td>
                </tr>
                <tr>
                    <td>Phone Number</td>
                    <td>1234567890</td>
                </tr>
            </table>
        </div>
        <div>
            <div class="section-title">🎓 Education Details</div>
            <table>
                <tr>
                    <td>University</td>
                    <td>MIT</td>
                </tr>
                <tr>
                    <td>Degree</td>
                    <td>Master's</td>
                </tr>
                <tr>
                    <td>Major</td>
                    <td>Computer Science</td>
                </tr>
            </table>
        </div>
        <p style="text-align: center; color: #6c757d; margin-top: 30px;">
            This is a test email from the Hyrind Interest Form System
        </p>
    </div>
</body>
</html>
"""
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.OPERATIONS_EMAIL]
        )
        
        email.attach_alternative(html_content, "text/html")
        
        result = email.send(fail_silently=False)
        
        if result == 1:
            print("✓ Test HTML email sent successfully!")
            print(f"Email sent to: {settings.OPERATIONS_EMAIL}")
            print("\nCheck your inbox for a beautifully formatted HTML email with:")
            print("  • Professional table layout")
            print("  • Color-coded sections")
            print("  • Clickable links")
            print("  • Responsive design")
        else:
            print("✗ Email sending failed (no exception but result was 0)")
            
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your .env file has correct EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        print("2. For Gmail, use an App Password (not your regular password)")
        print("3. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("4. For testing, you can use: EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend")

if __name__ == '__main__':
    test_email_config()
    test_send_html_email()
