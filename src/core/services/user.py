from typing import Type
from django.template.loader import render_to_string
from rest_framework.request import Request
from core.models import User
from core.models import InvitationToken
from core.services.mailing import EmailService
from core.utils import get_frontend_host


class UserInviteService:
    def __init__(
        self,
        *,
        user: User,
        request: Request,
        invitation_token: InvitationToken,
    ):
        self.user: User = user
        self.request: Request = request
        self.invitation_token: InvitationToken = invitation_token
        self.__mailing_service: Type[EmailService] = EmailService

    def generate_invite_link(self):
        frontend_host = get_frontend_host(self.request)
        return f"{frontend_host}/app/accept-invite/{self.invitation_token.token}"

    def send_invitation(self):
        invite_link = self.generate_invite_link()
        self.__mailing_service.send_email(
            subject="Welcome",
            message=render_to_string(
                "mailing/send_invite.html",
                context={"user": self.user, "invitation_link": invite_link},
            ),
            recipients_email=[self.user.email],
        )
