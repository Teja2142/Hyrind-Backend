"""
Password Reset Utilities
Handles password reset token generation and email sending
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.conf import settings
from utils.email_service import EmailService
import secrets


class TokenGenerator(PasswordResetTokenGenerator):
    """Custom token generator for password reset"""
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.password)


password_reset_token = TokenGenerator()


def generate_reset_token(user):
    """Generate password reset token for user"""
    token = password_reset_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token


def verify_reset_token(uidb64, token):
    """Verify password reset token and return user"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None
    
    if password_reset_token.check_token(user, token):
        return user
    return None


def send_password_reset_email(user, reset_link):
    """Send password reset email to user"""
    user_name = ""
    if hasattr(user, 'profile'):
        user_name = f"{user.profile.first_name} {user.profile.last_name}".strip()
    
    if not user_name:
        user_name = user.email.split('@')[0].title()
    
    subject = "Reset Your Password - Hyrind"
    
    # Text content
    text_content = f"""
Hello {user_name},

We received a request to reset your password for your Hyrind account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours for security reasons.

If you didn't request a password reset, please ignore this email or contact support if you have concerns.

Best regards,
Hyrind Team
"""
    
    # HTML content
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Password Reset Request</h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px; color: #333333; font-size: 16px; line-height: 1.5;">
                                Hello <strong>{user_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 20px; color: #333333; font-size: 16px; line-height: 1.5;">
                                We received a request to reset your password for your Hyrind account.
                            </p>
                            
                            <p style="margin: 0 0 30px; color: #333333; font-size: 16px; line-height: 1.5;">
                                Click the button below to reset your password:
                            </p>
                            
                            <table role="presentation" style="margin: 0 auto;">
                                <tr>
                                    <td style="border-radius: 4px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                                        <a href="{reset_link}" style="display: inline-block; padding: 16px 36px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold;">
                                            Reset My Password
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 30px 0 20px; color: #666666; font-size: 14px; line-height: 1.5;">
                                Or copy and paste this link into your browser:
                            </p>
                            
                            <p style="margin: 0 0 30px; padding: 12px; background-color: #f8f9fa; border-left: 4px solid #667eea; word-break: break-all; font-size: 14px; color: #667eea;">
                                {reset_link}
                            </p>
                            
                            <div style="margin: 30px 0; padding: 20px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.5;">
                                    <strong>⚠️ Important:</strong> This link will expire in 24 hours for security reasons.
                                </p>
                            </div>
                            
                            <p style="margin: 20px 0 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                If you didn't request a password reset, please ignore this email or contact our support team if you have concerns about your account security.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; background-color: #f8f9fa; text-align: center; border-top: 1px solid #dee2e6;">
                            <p style="margin: 0 0 10px; color: #666666; font-size: 14px;">
                                Best regards,<br>
                                <strong>Hyrind Team</strong>
                            </p>
                            <p style="margin: 10px 0 0; color: #999999; font-size: 12px;">
                                This is an automated message, please do not reply to this email.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    try:
        EmailService.send_email(
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            to_emails=[user.email]
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False
