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
        fail_silently: bool = True
    ) -> bool:
        """
        Send email with both text and HTML content
        
        Args:
            subject: Email subject
            text_content: Plain text version
            html_content: HTML version
            to_emails: List of recipient emails
            from_email: Sender email (defaults to settings)
            reply_to: Reply-to addresses
            fail_silently: Whether to suppress exceptions
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hyrind.com')
            
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

What You Can Expect:
✓ Access to exclusive job opportunities
✓ Personalized recruiter support
✓ Career guidance and resources
✓ Regular updates on new positions

If you have any questions, feel free to reach out to our support team.

Best regards,
The Hyrind Team

---
This is an automated message. Please do not reply to this email.
For support, contact us at: {settings.OPERATIONS_EMAIL}
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
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .info-box h3 {{
            margin: 0 0 15px 0;
            color: #667eea;
            font-size: 16px;
        }}
        .info-item {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-item:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #495057;
            min-width: 120px;
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
            content: "✓";
            color: #28a745;
            font-weight: bold;
            margin-right: 10px;
        }}
        .cta {{
            text-align: center;
            margin: 30px 0;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 40px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
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
            <p>For support, contact us at: <a href="mailto:{settings.OPERATIONS_EMAIL}">{settings.OPERATIONS_EMAIL}</a></p>
            <p style="margin-top: 15px; font-size: 12px;">
                © {__import__('datetime').datetime.now().year} Hyrind. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content
    
    @staticmethod
    def get_admin_notification_email(user_data: Dict[str, Any]) -> tuple:
        """
        Generate notification email for admin about new user registration
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            tuple: (subject, text_content, html_content)
        """
        subject = f"🎯 New User Registration - {user_data['first_name']} {user_data['last_name']}"
        
        text_content = f"""
New User Registration Received

User Information:
Name: {user_data['first_name']} {user_data['last_name']}
Email: {user_data['email']}
Phone: {user_data.get('phone', 'N/A')}

Education:
University: {user_data.get('university', 'N/A')}
Degree: {user_data.get('degree', 'N/A')}
Major: {user_data.get('major', 'N/A')}
Graduation Date: {user_data.get('graduation_date', 'N/A')}

Visa Status: {user_data.get('visa_status', 'N/A')}
OPT End Date: {user_data.get('opt_end_date', 'N/A')}

Profile ID: {user_data.get('profile_id', 'N/A')}
Registered At: {user_data.get('created_at', 'N/A')}

Action Required:
Please review and activate this user's account in the admin panel.
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
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 700px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 25px;
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
        }}
        td {{
            padding: 10px;
            border: 1px solid #e0e0e0;
        }}
        td:first-child {{
            font-weight: 600;
            background-color: #f8f9fa;
            width: 40%;
        }}
        .action-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎯 New User Registration</h1>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">👤 User Information</div>
                <table>
                    <tr>
                        <td>Name</td>
                        <td>{user_data['first_name']} {user_data['last_name']}</td>
                    </tr>
                    <tr>
                        <td>Email</td>
                        <td>{user_data['email']}</td>
                    </tr>
                    <tr>
                        <td>Phone</td>
                        <td>{user_data.get('phone', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">🎓 Education</div>
                <table>
                    <tr>
                        <td>University</td>
                        <td>{user_data.get('university', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Degree</td>
                        <td>{user_data.get('degree', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Major</td>
                        <td>{user_data.get('major', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Graduation Date</td>
                        <td>{user_data.get('graduation_date', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">🌍 Visa Status</div>
                <table>
                    <tr>
                        <td>Visa Status</td>
                        <td>{user_data.get('visa_status', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>OPT End Date</td>
                        <td>{user_data.get('opt_end_date', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            
            <div class="action-box">
                <strong>⚠️ Action Required:</strong><br>
                Please review and activate this user's account in the admin panel.<br>
                <strong>Profile ID:</strong> {user_data.get('profile_id', 'N/A')}
            </div>
        </div>
        
        <div class="footer">
            <p>Automated notification from Hyrind Registration System</p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content


class RecruiterRegistrationEmailTemplate:
    """Email templates for recruiter registration"""
    
    @staticmethod
    def get_welcome_email_to_recruiter(recruiter_data: Dict[str, Any]) -> tuple:
        """
        Generate welcome email for newly registered recruiter
        
        Args:
            recruiter_data: Dictionary containing recruiter information
            
        Returns:
            tuple: (subject, text_content, html_content)
        """
        subject = f"🎉 Welcome to Hyrind Team - {recruiter_data['name']}!"
        
        text_content = f"""
Welcome to the Hyrind Team!

Dear {recruiter_data['name']},

Thank you for joining Hyrind as an Internal Recruiter! We're excited to have you on our team.

Your Registration Details:
- Employee ID: {recruiter_data['employee_id']}
- Name: {recruiter_data['name']}
- Email: {recruiter_data['email']}
- Department: {recruiter_data.get('department_display', 'N/A')}
- Specialization: {recruiter_data.get('specialization_display', 'N/A')}
- Date of Joining: {recruiter_data.get('date_of_joining', 'N/A')}

Account Status:
Your account is currently pending admin approval. Once approved, you'll be able to:
✓ Access the recruiter dashboard
✓ Manage client assignments
✓ Track job applications
✓ View performance metrics

Next Steps:
1. Wait for admin approval notification
2. Complete your profile after activation
3. Review our recruiter guidelines
4. Start managing your assigned clients

If you have any questions about the onboarding process, feel free to reach out to the admin team.

Best regards,
The Hyrind Admin Team

---
This is an automated message. Please do not reply to this email.
For support, contact: {settings.OPERATIONS_EMAIL}
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
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
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
        .badge {{
            display: inline-block;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin: 10px 0;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #2c3e50;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .info-box h3 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 16px;
        }}
        .info-item {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-item:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #495057;
            min-width: 150px;
        }}
        .info-value {{
            color: #333;
        }}
        .status-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .features {{
            background-color: #e8f5e9;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        .features h3 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 16px;
        }}
        .feature-item {{
            padding: 8px 0;
            color: #495057;
        }}
        .feature-item::before {{
            content: "✓";
            color: #28a745;
            font-weight: bold;
            margin-right: 10px;
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
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
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
        .footer {{
            background-color: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        .footer a {{
            color: #2c3e50;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎉 Welcome to Hyrind Team!</h1>
            <p>Internal Recruiter Registration</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Dear {recruiter_data['name']},
            </div>
            
            <p>
                Thank you for joining Hyrind as an Internal Recruiter! We're excited to have you on our team 
                and look forward to working together to connect talented professionals with great opportunities.
            </p>
            
            <div class="badge">Employee ID: {recruiter_data['employee_id']}</div>
            
            <div class="info-box">
                <h3>📋 Your Registration Details</h3>
                <div class="info-item">
                    <span class="info-label">Employee ID:</span>
                    <span class="info-value">{recruiter_data['employee_id']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Name:</span>
                    <span class="info-value">{recruiter_data['name']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{recruiter_data['email']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Department:</span>
                    <span class="info-value">{recruiter_data.get('department_display', 'N/A')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Specialization:</span>
                    <span class="info-value">{recruiter_data.get('specialization_display', 'N/A')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Date of Joining:</span>
                    <span class="info-value">{recruiter_data.get('date_of_joining', 'N/A')}</span>
                </div>
            </div>
            
            <div class="status-box">
                <strong>⏳ Account Status: Pending Approval</strong><br>
                Your account is currently pending admin approval. You'll receive another email once your account is activated.
            </div>
            
            <div class="features">
                <h3>🌟 Once Activated, You'll Be Able To:</h3>
                <div class="feature-item">Access the recruiter dashboard</div>
                <div class="feature-item">Manage client assignments (up to {recruiter_data.get('max_clients', 3)} clients)</div>
                <div class="feature-item">Track job applications and placements</div>
                <div class="feature-item">View performance metrics and analytics</div>
                <div class="feature-item">Communicate with candidates and clients</div>
            </div>
            
            <div class="steps">
                <h3 style="color: #2c3e50; margin-bottom: 20px;">📝 Next Steps</h3>
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-text">Wait for admin approval notification</div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-text">Complete your profile after activation</div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-text">Review our recruiter guidelines and best practices</div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-text">Start managing your assigned clients</div>
                </div>
            </div>
            
            <p style="margin-top: 30px; color: #495057;">
                If you have any questions about the onboarding process or need assistance, 
                feel free to reach out to the admin team.
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>For support, contact: <a href="mailto:{settings.OPERATIONS_EMAIL}">{settings.OPERATIONS_EMAIL}</a></p>
            <p style="margin-top: 15px; font-size: 12px;">
                © {__import__('datetime').datetime.now().year} Hyrind. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content
    
    @staticmethod
    def get_admin_notification_email(recruiter_data: Dict[str, Any]) -> tuple:
        """
        Generate notification email for admin about new recruiter registration
        
        Args:
            recruiter_data: Dictionary containing recruiter information
            
        Returns:
            tuple: (subject, text_content, html_content)
        """
        subject = f"👔 New Recruiter Registration - {recruiter_data['name']}"
        
        text_content = f"""
New Recruiter Registration Received

Recruiter Information:
Employee ID: {recruiter_data['employee_id']}
Name: {recruiter_data['name']}
Email: {recruiter_data['email']}
Phone: {recruiter_data.get('phone', 'N/A')}

Employment Details:
Department: {recruiter_data.get('department_display', 'N/A')}
Specialization: {recruiter_data.get('specialization_display', 'N/A')}
Date of Joining: {recruiter_data.get('date_of_joining', 'N/A')}
Max Clients: {recruiter_data.get('max_clients', 3)}

Status: {recruiter_data.get('status', 'Pending')}
Recruiter ID: {recruiter_data.get('id', 'N/A')}
Registered At: {recruiter_data.get('created_at', 'N/A')}

Action Required:
Please review and activate this recruiter's account in the admin panel.
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
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            max-width: 700px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        td {{
            padding: 10px;
            border: 1px solid #e0e0e0;
        }}
        td:first-child {{
            font-weight: 600;
            background-color: #f8f9fa;
            width: 40%;
        }}
        .action-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>👔 New Recruiter Registration</h1>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">👤 Recruiter Information</div>
                <table>
                    <tr>
                        <td>Employee ID</td>
                        <td><strong>{recruiter_data['employee_id']}</strong></td>
                    </tr>
                    <tr>
                        <td>Name</td>
                        <td>{recruiter_data['name']}</td>
                    </tr>
                    <tr>
                        <td>Email</td>
                        <td>{recruiter_data['email']}</td>
                    </tr>
                    <tr>
                        <td>Phone</td>
                        <td>{recruiter_data.get('phone', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">💼 Employment Details</div>
                <table>
                    <tr>
                        <td>Department</td>
                        <td>{recruiter_data.get('department_display', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Specialization</td>
                        <td>{recruiter_data.get('specialization_display', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Date of Joining</td>
                        <td>{recruiter_data.get('date_of_joining', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Max Clients</td>
                        <td>{recruiter_data.get('max_clients', 3)}</td>
                    </tr>
                    <tr>
                        <td>Status</td>
                        <td><strong>{recruiter_data.get('status', 'Pending')}</strong></td>
                    </tr>
                </table>
            </div>
            
            <div class="action-box">
                <strong>⚠️ Action Required:</strong><br>
                Please review and activate this recruiter's account in the admin panel.<br>
                <strong>Recruiter ID:</strong> {recruiter_data.get('id', 'N/A')}
            </div>
        </div>
        
        <div class="footer">
            <p>Automated notification from Hyrind Recruiter Registration System</p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content


class UserActivationEmailTemplate:
    """Email templates for user account activation"""
    
    @staticmethod
    def get_activation_email(user_data: Dict[str, Any]) -> tuple:
        """
        Generate activation email for user when admin activates their account
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            tuple: (subject, text_content, html_content)
        """
        subject = f"✅ Your Hyrind Account is Now Active - {user_data['first_name']}!"
        
        # Generate login URL (you can customize this based on your frontend URL)
        login_url = user_data.get('login_url', 'https://hyrind.com/login')
        
        text_content = f"""
Your Hyrind Account Has Been Activated!

Dear {user_data['first_name']} {user_data['last_name']},

Great news! Your Hyrind account has been reviewed and approved by our team. You can now log in and start exploring opportunities!

Account Details:
- Name: {user_data['first_name']} {user_data['last_name']}
- Email: {user_data['email']}
- Status: ACTIVE ✓

What You Can Do Now:
✓ Log in to your account
✓ Complete your profile
✓ Browse job opportunities
✓ Connect with recruiters
✓ Track your applications
✓ Access career resources

Login Instructions:
1. Visit: {login_url}
2. Use your registered email: {user_data['email']}
3. Enter your password
4. Start exploring opportunities!

Getting Started Tips:
• Complete your profile with detailed information
• Upload an updated resume
• Set your job preferences
• Enable job alerts for relevant positions
• Keep your profile updated regularly

Need Help?
If you have any questions or need assistance getting started, our support team is here to help!

Best regards,
The Hyrind Team

---
Login URL: {login_url}
Support: {settings.OPERATIONS_EMAIL}
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
        .header p {{
            margin: 10px 0 0 0;
            font-size: 16px;
            opacity: 0.95;
        }}
        .success-icon {{
            font-size: 60px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}
        .status-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            margin: 15px 0;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .info-box h3 {{
            margin: 0 0 15px 0;
            color: #28a745;
            font-size: 16px;
        }}
        .info-item {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-item:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #495057;
            min-width: 100px;
        }}
        .info-value {{
            color: #333;
        }}
        .features {{
            background-color: #d4edda;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        .features h3 {{
            margin: 0 0 15px 0;
            color: #28a745;
            font-size: 16px;
        }}
        .feature-item {{
            padding: 8px 0;
            color: #495057;
        }}
        .feature-item::before {{
            content: "✓";
            color: #28a745;
            font-weight: bold;
            margin-right: 10px;
        }}
        .cta-section {{
            text-align: center;
            margin: 35px 0;
            padding: 30px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 16px 50px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(40, 167, 69, 0.3);
            transition: transform 0.2s;
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(40, 167, 69, 0.4);
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
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
        .tips {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .tips h3 {{
            margin: 0 0 15px 0;
            color: #856404;
            font-size: 16px;
        }}
        .tip-item {{
            padding: 6px 0;
            color: #856404;
        }}
        .tip-item::before {{
            content: "•";
            color: #ffc107;
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
            color: #28a745;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="success-icon">✅</div>
            <h1>Account Activated!</h1>
            <p>You're ready to get started</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Dear {user_data['first_name']} {user_data['last_name']},
            </div>
            
            <p>
                <strong>Great news!</strong> Your Hyrind account has been reviewed and approved by our team. 
                You can now log in and start exploring exciting career opportunities!
            </p>
            
            <div class="status-badge">✓ ACCOUNT ACTIVE</div>
            
            <div class="info-box">
                <h3>📋 Your Account Details</h3>
                <div class="info-item">
                    <span class="info-label">Name:</span>
                    <span class="info-value">{user_data['first_name']} {user_data['last_name']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{user_data['email']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Status:</span>
                    <span class="info-value" style="color: #28a745; font-weight: 600;">ACTIVE ✓</span>
                </div>
            </div>
            
            <div class="cta-section">
                <h3 style="margin-top: 0; color: #333;">Ready to Get Started?</h3>
                <p style="margin-bottom: 25px; color: #6c757d;">Log in now and explore opportunities</p>
                <a href="{login_url}" class="cta-button">Log In to Your Account</a>
                <p style="margin-top: 20px; font-size: 13px; color: #6c757d;">
                    Login Email: <strong>{user_data['email']}</strong>
                </p>
            </div>
            
            <div class="steps">
                <h3 style="color: #28a745; margin-bottom: 20px;">🚀 Quick Start Guide</h3>
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-text">Visit <strong>{login_url}</strong></div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-text">Enter your email and password</div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-text">Complete your profile with detailed information</div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-text">Start exploring job opportunities</div>
                </div>
            </div>
            
            <div class="features">
                <h3>🌟 What You Can Do Now</h3>
                <div class="feature-item">Browse thousands of job opportunities</div>
                <div class="feature-item">Connect with dedicated recruiters</div>
                <div class="feature-item">Track your job applications</div>
                <div class="feature-item">Access career resources and tips</div>
                <div class="feature-item">Set up personalized job alerts</div>
                <div class="feature-item">Build your professional profile</div>
            </div>
            
            <div class="tips">
                <h3>💡 Tips for Success</h3>
                <div class="tip-item">Complete your profile with detailed work experience</div>
                <div class="tip-item">Upload an updated, professional resume</div>
                <div class="tip-item">Set your job preferences and desired locations</div>
                <div class="tip-item">Enable job alerts to stay updated on new opportunities</div>
                <div class="tip-item">Keep your profile and resume updated regularly</div>
                <div class="tip-item">Respond promptly to recruiter messages</div>
            </div>
            
            <p style="margin-top: 30px; color: #495057; text-align: center;">
                Need help getting started? Our support team is ready to assist you!<br>
                <a href="mailto:{settings.OPERATIONS_EMAIL}" style="color: #28a745; text-decoration: none;">
                    Contact Support
                </a>
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>Your journey to the perfect career starts now!</p>
            <p style="margin-top: 15px;">
                <a href="{login_url}">Login</a> | 
                <a href="mailto:{settings.OPERATIONS_EMAIL}">Support</a>
            </p>
            <p style="margin-top: 15px; font-size: 12px;">
                © {__import__('datetime').datetime.now().year} Hyrind. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content


class RecruiterActivationEmailTemplate:
    """Email templates for recruiter account activation"""
    
    @staticmethod
    def get_activation_email(recruiter_data: Dict[str, Any]) -> tuple:
        """
        Generate activation email for recruiter when admin activates their account
        
        Args:
            recruiter_data: Dictionary containing recruiter information
            
        Returns:
            tuple: (subject, text_content, html_content)
        """
        subject = f"✅ Your Hyrind Recruiter Account is Now Active - {recruiter_data['name']}!"
        
        # Generate login URL (you can customize this based on your frontend URL)
        login_url = recruiter_data.get('login_url', 'https://hyrind.com/recruiter/login')
        dashboard_url = recruiter_data.get('dashboard_url', 'https://hyrind.com/recruiter/dashboard')
        
        text_content = f"""
Your Hyrind Recruiter Account Has Been Activated!

Dear {recruiter_data['name']},

Congratulations! Your Hyrind recruiter account has been approved and activated by our admin team. You can now log in and start managing client assignments!

Account Details:
- Employee ID: {recruiter_data['employee_id']}
- Name: {recruiter_data['name']}
- Email: {recruiter_data['email']}
- Department: {recruiter_data.get('department_display', 'N/A')}
- Specialization: {recruiter_data.get('specialization_display', 'N/A')}
- Max Clients: {recruiter_data.get('max_clients', 3)}
- Status: ACTIVE ✓

What You Can Do Now:
✓ Access your recruiter dashboard
✓ View and manage client assignments
✓ Track job applications and placements
✓ Monitor performance metrics
✓ Communicate with candidates
✓ Update client progress and notes

Login Instructions:
1. Visit: {login_url}
2. Use your email: {recruiter_data['email']}
3. Enter your password
4. Access your dashboard!

Getting Started:
• Review your assigned clients (if any)
• Familiarize yourself with the dashboard
• Set up your recruiter profile
• Review company policies and guidelines
• Start tracking your placements

Dashboard: {dashboard_url}

Need Help?
If you have any questions or need assistance, reach out to the admin team!

Best regards,
The Hyrind Admin Team

---
Login URL: {login_url}
Support: {settings.OPERATIONS_EMAIL}
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
        .header p {{
            margin: 10px 0 0 0;
            font-size: 16px;
            opacity: 0.95;
        }}
        .success-icon {{
            font-size: 60px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}
        .employee-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            margin: 10px 0;
        }}
        .status-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            margin: 10px 0 10px 10px;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .info-box h3 {{
            margin: 0 0 15px 0;
            color: #28a745;
            font-size: 16px;
        }}
        .info-item {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-item:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #495057;
            min-width: 140px;
        }}
        .info-value {{
            color: #333;
        }}
        .features {{
            background-color: #d4edda;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        .features h3 {{
            margin: 0 0 15px 0;
            color: #28a745;
            font-size: 16px;
        }}
        .feature-item {{
            padding: 8px 0;
            color: #495057;
        }}
        .feature-item::before {{
            content: "✓";
            color: #28a745;
            font-weight: bold;
            margin-right: 10px;
        }}
        .cta-section {{
            text-align: center;
            margin: 35px 0;
            padding: 30px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 16px 50px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(40, 167, 69, 0.3);
            transition: transform 0.2s;
            margin: 5px;
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(40, 167, 69, 0.4);
        }}
        .cta-button.secondary {{
            background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
            box-shadow: 0 4px 6px rgba(108, 117, 125, 0.3);
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
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
        .tips {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .tips h3 {{
            margin: 0 0 15px 0;
            color: #856404;
            font-size: 16px;
        }}
        .tip-item {{
            padding: 6px 0;
            color: #856404;
        }}
        .tip-item::before {{
            content: "•";
            color: #ffc107;
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
            color: #28a745;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="success-icon">✅</div>
            <h1>Account Activated!</h1>
            <p>Welcome to the Hyrind Team</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Dear {recruiter_data['name']},
            </div>
            
            <p>
                <strong>Congratulations!</strong> Your Hyrind recruiter account has been approved and activated. 
                You're now officially part of our team and ready to start managing client assignments!
            </p>
            
            <div style="text-align: center;">
                <span class="employee-badge">Employee ID: {recruiter_data['employee_id']}</span>
                <span class="status-badge">✓ ACCOUNT ACTIVE</span>
            </div>
            
            <div class="info-box">
                <h3>📋 Your Account Details</h3>
                <div class="info-item">
                    <span class="info-label">Employee ID:</span>
                    <span class="info-value"><strong>{recruiter_data['employee_id']}</strong></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Name:</span>
                    <span class="info-value">{recruiter_data['name']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{recruiter_data['email']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Department:</span>
                    <span class="info-value">{recruiter_data.get('department_display', 'N/A')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Specialization:</span>
                    <span class="info-value">{recruiter_data.get('specialization_display', 'N/A')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Max Clients:</span>
                    <span class="info-value">{recruiter_data.get('max_clients', 3)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Status:</span>
                    <span class="info-value" style="color: #28a745; font-weight: 600;">ACTIVE ✓</span>
                </div>
            </div>
            
            <div class="cta-section">
                <h3 style="margin-top: 0; color: #333;">Ready to Start?</h3>
                <p style="margin-bottom: 25px; color: #6c757d;">Access your recruiter dashboard now</p>
                <a href="{login_url}" class="cta-button">Log In Now</a>
                <a href="{dashboard_url}" class="cta-button secondary">View Dashboard</a>
                <p style="margin-top: 20px; font-size: 13px; color: #6c757d;">
                    Login Email: <strong>{recruiter_data['email']}</strong>
                </p>
            </div>
            
            <div class="steps">
                <h3 style="color: #28a745; margin-bottom: 20px;">🚀 Quick Start Guide</h3>
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-text">Visit <strong>{login_url}</strong></div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-text">Enter your email and password to log in</div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-text">Explore your dashboard and assigned clients</div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-text">Start managing applications and placements</div>
                </div>
            </div>
            
            <div class="features">
                <h3>🌟 What You Can Do Now</h3>
                <div class="feature-item">Access your personalized recruiter dashboard</div>
                <div class="feature-item">View and manage your client assignments</div>
                <div class="feature-item">Track job applications and candidate progress</div>
                <div class="feature-item">Monitor your performance metrics and statistics</div>
                <div class="feature-item">Communicate with candidates and clients</div>
                <div class="feature-item">Update client notes and progress reports</div>
            </div>
            
            <div class="tips">
                <h3>💡 Getting Started Tips</h3>
                <div class="tip-item">Review your assigned clients and their requirements</div>
                <div class="tip-item">Familiarize yourself with the dashboard features</div>
                <div class="tip-item">Complete your recruiter profile information</div>
                <div class="tip-item">Review company policies and recruitment guidelines</div>
                <div class="tip-item">Set up your communication preferences</div>
                <div class="tip-item">Track your placements and performance metrics</div>
            </div>
            
            <p style="margin-top: 30px; color: #495057; text-align: center;">
                Need help or have questions? The admin team is here to assist you!<br>
                <a href="mailto:{settings.OPERATIONS_EMAIL}" style="color: #28a745; text-decoration: none;">
                    Contact Admin Support
                </a>
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Hyrind Recruitment Services</strong></p>
            <p>Welcome to the team! Let's make great placements together.</p>
            <p style="margin-top: 15px;">
                <a href="{login_url}">Login</a> | 
                <a href="{dashboard_url}">Dashboard</a> | 
                <a href="mailto:{settings.OPERATIONS_EMAIL}">Support</a>
            </p>
            <p style="margin-top: 15px; font-size: 12px;">
                © {__import__('datetime').datetime.now().year} Hyrind. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content
