from datetime import datetime, timezone, timedelta

import jwt
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.conf import settings
from django.template.loader import render_to_string

from django_tenants.utils import tenant_context

from core.enums.user import UserInvitationStatusChoice
from core.models import TenantCreationRequest, Tenant, Domain
from core.models.user import User
from core.services.mailing import EmailService


class CreationTenantRequestTokenService:
    def __init__(self, *, token: str = None):
        self.token = token

    @classmethod
    def create_token(cls, *, tenant_creation_request_id: int):
        return jwt.encode(
            {
                "tenant_request_id": tenant_creation_request_id,
                "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

    def validate_token(self) -> dict | None:
        try:
            return jwt.decode(self.token, settings.SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidSignatureError):
            return


class TenantService:
    def __init__(
        self,
        *,
        request: TenantCreationRequest,
        tenant_admin_first_name: str,
        tenant_admin_last_name: str,
        tenant_admin_password: str,
    ):
        self._request: TenantCreationRequest = request
        self._tenant_admin_first_name = tenant_admin_first_name
        self._tenant_admin_last_name = tenant_admin_last_name
        self._tenant_admin_password = tenant_admin_password

    def create_tenant(self) -> Tenant:
        tenant = Tenant(
            schema_name=self._request.domain,
            name=self._request.tenant_name,
            admin_email=self._request.admin_email,
        )
        tenant.save()
        self.__create_tenant_domain(tenant=tenant)
        return tenant

    def __create_tenant_domain(self, *, tenant: Tenant) -> Domain:
        domain: Domain = Domain(domain=self._request.domain, tenant=tenant)
        domain.save()
        return domain

    def __create_tenant_site(self) -> None:
        try:
            Site.objects.get(id=settings.SITE_ID)
        except ObjectDoesNotExist:
            Site.objects.create(
                id=settings.SITE_ID,
                domain=self._request.domain,
                name=self._request.domain,
            )

    def __create_tenant_admin(
        self,
    ) -> User:
        tenant_admin = User(
            email=self._request.admin_email,
            username=self._request.admin_email,
            first_name=self._tenant_admin_first_name,
            last_name=self._tenant_admin_last_name,
            invite_status=UserInvitationStatusChoice.SUCCESS,
            is_tenant_admin=True,
            is_staff=True,
            is_superuser=True,
        )
        tenant_admin.set_password(raw_password=self._tenant_admin_password)
        tenant_admin.save()
        return tenant_admin

    @transaction.atomic
    def finish_registration(self, *, new_tenant: Tenant) -> User:
        new_tenant.create_schema(check_if_exists=True)
        with tenant_context(new_tenant):
            tenant_admin = self.__create_tenant_admin()
            self.__create_tenant_site()
        return tenant_admin


def send_confirm_email_tenant_creation_request(
    *, creation_tenant_request: TenantCreationRequest
):
    base_url = settings.BASE_FRONTEND_HOST
    token = CreationTenantRequestTokenService.create_token(
        tenant_creation_request_id=creation_tenant_request.id
    )
    link = f"{base_url}/tenant-registration/{token}"
    EmailService.send_email(
        subject="Добро пожаловать в Access Controller. Почти готово!",
        message=render_to_string(
            "mailing/confirm_tenant_creation_request.html", context={"link": link}
        ),
        recipients_email=[creation_tenant_request.admin_email],
    )
