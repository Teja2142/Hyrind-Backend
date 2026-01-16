"""
Email Service Module
Handles all email notifications for the Hyrind platform
Following industry best practices with templates, error handling, and logging
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Centralized email service for sending notifications"""
    
    @staticmethod
    def send_email(
        subject: str,
        text_content: str,
        html_content: str,
        to_emails: list,
        from_email: Optional[str] = None,
        reply_to: Optional[list] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send email with both text and HTML content
        
        Args:
            subject: Email subject
            text_content: Plain text version
            html_content: HTML version
            to_emails: List of recipient email addresses
            from_email: Sender email address (optional)
            reply_to: Reply-to email addresses (optional)
            fail_silently: Whether to silently fail on errors
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hyrind.com')
            reply_to = reply_to or [from_email]
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_emails,
                reply_to=reply_to
            )
            
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=fail_silently)
            
            logger.info(f"✓ Email sent successfully: {subject} to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to send email: {subject} - Error: {str(e)}")
            return False


class UserRegistrationEmailTemplate:
    """Email templates for user registration"""
    
    @staticmethod
    def get_welcome_email_to_user(user_data: Dict[str, Any]) -> tuple:
        """
        Generate welcome email for newly registered user
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            tuple: (subject, text_content, html_content)
        """
        subject = f"🎉 Welcome to Hyrind - {user_data['first_name']}!"
        
        text_content = f"""
Welcome to Hyrind!

Dear {user_data['first_name']} {user_data['last_name']},

Thank you for registering with Hyrind! We're excited to have you join our platform.

Your Registration Details:
- Name: {user_data['first_name']} {user_data['last_name']}
- Email: {user_data['email']}
- University: {user_data.get('university', 'N/A')}
- Degree: {user_data.get('degree', 'N/A')}
- Major: {user_data.get('major', 'N/A')}

Next Steps:
1. Your account is currently under review by our team
2. Once approved, you'll receive an activation email
3. After activation, you can log in and access all features
4. Complete your profile to improve your job matching
5. Regular updates on new positions

If you have any questions, feel free to reach out to our support team.

Best regards,
The Hyrind Team

---
This is an automated message. Please do not reply to this email.
For support, contact us at: {getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}
"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 16px;
            opacity: 0.95;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}
        .info-box {{
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
            background-color: #f8f9fa;
        }}
        .info-box h3 {{
            margin: 0 0 15px 0;
            color: #667eea;
            font-size: 16px;
        }}
        .info-item {{
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-item:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            display: inline-block;
            width: 120px;
        }}
        .info-value {{
            color: #333;
        }}
        .steps {{
            margin: 30px 0;
        }}
        .step {{
            display: flex;
            align-items: start;
            margin-bottom: 15px;
        }}
        .step-number {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        .step-text {{
            padding-top: 4px;
            color: #495057;
        }}
        .features {{
            background-color: #f0f4ff;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        .features h3 {{
            margin: 0 0 15px 0;
            color: #667eea;
            font-size: 16px;
        }}
        .feature-item {{
            padding: 8px 0;
            color: #495057;
        }}
        .feature-item::before {{
            content: "✓ ";
            color: #28a745;
            font-weight: bold;
            margin-right: 10px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎉 Welcome to Hyrind!</h1>
            <p>Your journey to the perfect career starts here</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Dear {user_data['first_name']} {user_data['last_name']},
            </div>
            
            <p>
                Thank you for registering with Hyrind! We're thrilled to have you join our growing community 
                of talented professionals. Your account has been successfully created.
            </p>
            
            <div class="info-box">
                <h3>📋 Your Registration Details</h3>
                <div class="info-item">
                    <span class="info-label">Name:</span>
                    <span class="info-value">{user_data['first_name']} {user_data['last_name']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{user_data['email']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">University:</span>
                    <span class="info-value">{user_data.get('university', 'N/A')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Degree:</span>
                    <span class="info-value">{user_data.get('degree', 'N/A')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Major:</span>
                    <span class="info-value">{user_data.get('major', 'N/A')}</span>
                </div>
            </div>
            
            <div class="steps">
                <h3 style="color: #667eea; margin-bottom: 20px;">📝 Next Steps</h3>
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-text">Your account is currently under review by our team</div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-text">You'll receive an activation email once approved</div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-text">Log in and complete your profile for better job matching</div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-text">Start exploring exclusive job opportunities</div>
                </div>
            </div>
            
            <div class="features">
                <h3>🌟 What You Can Expect</h3>
                <div class="feature-item">Access to exclusive job opportunities</div>
                <div class="feature-item">Personalized recruiter support</div>
                <div class="feature-item">Career guidance and resources</div>
                <div class="feature-item">Regular updates on new positions</div>
            </div>
            
            <p style="margin-top: 30px; color: #495057;">
                If you have any questions or need assistance, our support team is here to help!
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>For support, contact us at: <a href="mailto:{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}">{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}</a></p>
            <p style="margin-top: 15px; font-size: 12px;">
                © 2026 Hyrind. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content


class ClientIntakeSheetEmailTemplate:
    """Email templates for client intake sheet submission"""
    
    @staticmethod
    def get_intake_sheet_submission_email(user_data: Dict[str, Any]) -> tuple:
        """Generate confirmation email for intake sheet submission"""
        subject = '✅ Client Intake Form - Submission Confirmed'
        
        first_name = user_data.get('first_name', 'User')
        last_name = user_data.get('last_name', '')
        
        text_content = f"""
Dear {first_name} {last_name},

Thank you for submitting your client intake form!

We have securely received your intake information and are processing your submission.
A member of our team will review your information and contact you shortly.

Submission Details:
- Submission Date: {user_data.get('submission_timestamp', 'N/A')}
- Form Status: Under Review

Next Steps:
1. We will review your intake information
2. Our team will contact you within 2-3 business days
3. Once verified, your onboarding will begin

Your information is encrypted and secure. You can update your intake form anytime from your dashboard.

Best regards,
The Hyrind Team

---
This is an automated message. Please do not reply to this email.
For support, contact us at: {getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}
"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .info-box {{
            padding: 20px;
            margin: 25px 0;
            background-color: #f0fdf4;
            border-left: 4px solid #28a745;
            border-radius: 4px;
        }}
        .info-box h3 {{
            margin: 0 0 15px 0;
            color: #28a745;
            font-size: 16px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>✅ Intake Form Submitted</h1>
            <p>Thank you for completing your intake form!</p>
        </div>
        
        <div class="content">
            <p>Dear {first_name} {last_name},</p>
            
            <p>
                Thank you for submitting your client intake form! We have securely received your information 
                and are processing your submission.
            </p>
            
            <div class="info-box">
                <h3>📋 Submission Summary</h3>
                <p><strong>Submission Date:</strong> {user_data.get('submission_timestamp', 'N/A')}</p>
                <p><strong>Status:</strong> Under Review</p>
            </div>
            
            <p>
                Our team will review your information and contact you within 2-3 business days to confirm receipt 
                and proceed with the next steps of your onboarding.
            </p>
            
            <p style="margin-top: 30px; color: #495057;">
                Questions? Contact our support team anytime!
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>For support, contact us at: <a href="mailto:{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}">{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}</a></p>
        </div>
    </div>
</body>
</html>
"""
        return subject, text_content, html_content


class CredentialSheetEmailTemplate:
    """Email templates for credential sheet submission"""
    
    @staticmethod
    def get_credential_sheet_submission_email(user_data: Dict[str, Any]) -> tuple:
        """Generate confirmation email for credential sheet submission"""
        subject = '✅ Credential Sheet - Submission Confirmed'
        
        first_name = user_data.get('first_name', 'User')
        last_name = user_data.get('last_name', '')
        
        text_content = f"""
Dear {first_name} {last_name},

Thank you for submitting your credential sheet!

We have securely received your platform credentials and job preferences.
Your login information is encrypted and will only be used to assist with your job search.

Submission Details:
- Submission Date: {user_data.get('submission_timestamp', 'N/A')}
- Form Status: Received

Security Notice:
Your credentials are encrypted with industry-standard security protocols and will only be used 
to assist with your job search on the specified platforms.

You can update your credentials anytime from your dashboard.

Best regards,
The Hyrind Team

---
This is an automated message. Please do not reply to this email.
For support, contact us at: {getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}
"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .security-notice {{
            padding: 20px;
            margin: 25px 0;
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
        }}
        .security-notice strong {{
            color: #856404;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>✅ Credential Sheet Submitted</h1>
            <p>Your credentials are secure and encrypted</p>
        </div>
        
        <div class="content">
            <p>Dear {first_name} {last_name},</p>
            
            <p>
                Thank you for submitting your credential sheet! We have securely received your platform credentials 
                and job preferences.
            </p>
            
            <div class="security-notice">
                <strong>🔒 Security Notice:</strong> Your login credentials are encrypted with industry-standard 
                security protocols and will only be used to assist with your job search.
            </div>
            
            <p>
                Your credentials will be kept secure and confidential. You can update them anytime from your dashboard.
            </p>
            
            <p style="margin-top: 30px; color: #495057;">
                Questions? Contact our support team anytime!
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>For support, contact us at: <a href="mailto:{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}">{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}</a></p>
        </div>
    </div>
</body>
</html>
"""
        return subject, text_content, html_content


class SubscriptionEmailTemplate:
    """Email templates for subscription activation and cancellation"""

    @staticmethod
    def _normalize(obj: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize input to a data dict. Accepts a subscription object or a dict."""
        data: Dict[str, Any] = {}
        try:
            if isinstance(obj, dict):
                data = obj.copy()
            elif hasattr(obj, 'profile'):
                # It's a subscription object
                profile = obj.profile
                user = getattr(profile, 'user', None)
                data['first_name'] = getattr(user, 'first_name', '') if user else ''
                data['last_name'] = getattr(user, 'last_name', '') if user else ''
                data['email'] = getattr(profile, 'email', None) or (getattr(user, 'email', None) if user else None)
                data['plan_name'] = getattr(obj.plan, 'name', '') if hasattr(obj, 'plan') else ''
                data['price'] = getattr(obj, 'price', '')
                data['billing_cycle'] = getattr(obj, 'billing_cycle', 'monthly')
                data['next_billing_date'] = getattr(obj, 'next_billing_date', None)
            else:
                # Fallback: try attribute access
                data['first_name'] = getattr(obj, 'first_name', '')
                data['last_name'] = getattr(obj, 'last_name', '')
                data['email'] = getattr(obj, 'email', None)
                data['plan_name'] = getattr(obj, 'plan_name', '')
                data['price'] = getattr(obj, 'price', '')
                data['billing_cycle'] = getattr(obj, 'billing_cycle', 'monthly')
                data['next_billing_date'] = getattr(obj, 'next_billing_date', None)
        except Exception as e:
            logger.error(f"Error normalizing subscription data: {str(e)}")
        
        return data

    @staticmethod
    def get_activation_email(obj: Dict[str, Any]) -> tuple:
        """Generate subscription activation email"""
        data = SubscriptionEmailTemplate._normalize(obj)
        subject = f"Your subscription is active: {data.get('plan_name', '')}"
        
        text_content = f"""
Hello {data.get('first_name', '')} {data.get('last_name', '')},

Your subscription "{data.get('plan_name', '')}" is now active.

Details:
- Plan: {data.get('plan_name', '')}
- Price: {data.get('price', '')}
- Billing Cycle: {data.get('billing_cycle', '')}
- Next Billing Date: {data.get('next_billing_date', '')}

You can manage your subscriptions from your dashboard.

Thanks,
Hyrind Team
"""
        
        dashboard_url = getattr(settings, 'FRONTEND_URL', 'https://hyrind.com/dashboard')
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .info-box {{
            padding: 20px;
            margin: 25px 0;
            background-color: #f0f4ff;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>✅ Subscription Active</h1>
            <p>Your plan is now active</p>
        </div>
        
        <div class="content">
            <p>Hello {data.get('first_name', '')} {data.get('last_name', '')},</p>
            
            <p>Your subscription <strong>{data.get('plan_name', '')}</strong> is now <strong>active</strong>!</p>
            
            <div class="info-box">
                <p><strong>Plan:</strong> {data.get('plan_name', '')}</p>
                <p><strong>Price:</strong> {data.get('price', '')}</p>
                <p><strong>Billing Cycle:</strong> {data.get('billing_cycle', '')}</p>
                <p><strong>Next Billing Date:</strong> {data.get('next_billing_date', '')}</p>
            </div>
            
            <p>Manage your subscriptions on your <a href="{dashboard_url}">dashboard</a>.</p>
            
            <p>— The Hyrind Team</p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>For support, contact us at: <a href="mailto:{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}">{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}</a></p>
        </div>
    </div>
</body>
</html>
"""
        return subject, text_content, html_content

    @staticmethod
    def get_cancellation_email(obj: Dict[str, Any]) -> tuple:
        """Generate subscription cancellation email"""
        data = SubscriptionEmailTemplate._normalize(obj)
        subject = f"Subscription cancelled: {data.get('plan_name', '')}"
        
        text_content = f"""
Hello {data.get('first_name', '')} {data.get('last_name', '')},

Your subscription "{data.get('plan_name', '')}" has been cancelled.

Cancellation Details:
- Plan: {data.get('plan_name', '')}
- Cancelled on: {data.get('cancellation_date', 'N/A')}

You will retain access until the end of your current billing cycle.

If you'd like to reactivate your subscription, you can do so from your dashboard anytime.

Thanks,
Hyrind Team
"""
        
        dashboard_url = getattr(settings, 'FRONTEND_URL', 'https://hyrind.com/dashboard')
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .info-box {{
            padding: 20px;
            margin: 25px 0;
            background-color: #ffe6e6;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Subscription Cancelled</h1>
            <p>We're sorry to see you go</p>
        </div>
        
        <div class="content">
            <p>Hello {data.get('first_name', '')} {data.get('last_name', '')},</p>
            
            <p>Your subscription <strong>{data.get('plan_name', '')}</strong> has been cancelled.</p>
            
            <div class="info-box">
                <p><strong>Plan:</strong> {data.get('plan_name', '')}</p>
                <p><strong>Cancelled on:</strong> {data.get('cancellation_date', 'N/A')}</p>
            </div>
            
            <p>You will retain access until the end of your current billing cycle. If you'd like to reactivate your subscription, 
            you can do so anytime from your <a href="{dashboard_url}">dashboard</a>.</p>
            
            <p>We'd love to hear your feedback on how we can improve!</p>
            
            <p>— The Hyrind Team</p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>For support, contact us at: <a href="mailto:{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}">{getattr(settings, 'OPERATIONS_EMAIL', 'support@hyrind.com')}</a></p>
        </div>
    </div>
</body>
</html>
"""
        return subject, text_content, html_content
