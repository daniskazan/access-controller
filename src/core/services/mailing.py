from django.core.mail import send_mail as django_send_email
from django.conf import settings


class EmailService:
    @classmethod
    def send_email(cls, subject: str, message: str, recipients_email: list[str]) -> str:
        django_send_email(
            subject=subject,
            message=None,
            html_message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipients_email,
        )
        return f"Отправлено на email: {recipients_email}"
