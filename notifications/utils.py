import logging
from django.conf import settings
from .models import EmailLog

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html: str, email_type: str = 'transactional'):
    """
    Send an email via the configured backend and log the result.
    Uses Django's built-in email backend (SMTP / console) configured in settings.
    """
    try:
        from django.core.mail import send_mail
        import html as html_lib
        # Send via Django mail
        send_mail(
            subject=subject,
            message=html_lib.unescape(
                html.replace('<p>', '').replace('</p>', '\n')
                    .replace('<br>', '\n').replace('<br/>', '\n')
                    .replace('<strong>', '').replace('</strong>', '')
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            html_message=html,
            fail_silently=False,
        )
        EmailLog.objects.create(
            recipient_email=to,
            email_type=email_type,
            status='sent',
        )
    except Exception as exc:
        logger.error('Email send failed to %s (%s): %s', to, email_type, exc)
        EmailLog.objects.create(
            recipient_email=to,
            email_type=email_type,
            status='failed',
            error_message=str(exc),
        )


def create_notification(user, title: str, message: str, link: str = None):
    """Create an in-app notification for a user."""
    from .models import Notification
    return Notification.objects.create(user=user, title=title, message=message, link=link)
