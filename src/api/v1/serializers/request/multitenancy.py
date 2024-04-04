from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request as DRFRequest

from core.models import Tenant, Domain, User
from core.models import TenantCreationRequest
from core.services.mailing import EmailService
from core.services.multitenancy import CreationTenantRequestTokenService, TenantService
from core.utils import get_host


class TenantCreationRequestCommandOutput(serializers.ModelSerializer):
    class Meta:
        model = TenantCreationRequest
        fields = "__all__"


class TenantCreationRequestCommand(serializers.ModelSerializer):
    class Meta:
        model = TenantCreationRequest
        fields = ("tenant_name", "domain", "admin_email")

    def validate(self, attrs: dict):
        self.__validate_request_host()
        self.__validate_domain(attrs["domain"])
        return attrs

    def __validate_request_host(self):
        request: DRFRequest = self.context["request"]
        if request.tenant.schema_name != "public":
            raise ValidationError(
                str(_("Нельзя создавать организации внутри другой организации"))
            )

    def __validate_domain(self, value: str):
        third_level_domain, main_domain, domain_zone = value.split(sep=".")
        if main_domain != "access":
            raise ValidationError(str(_("Основной домен должен быть равен access")))


class TenantCreationRequestValidateTokenCommand(serializers.Serializer):
    token = serializers.CharField()
    is_valid = serializers.SerializerMethodField()

    def get_is_valid(self, obj) -> bool:
        service = CreationTenantRequestTokenService(token=obj.get("token"))
        content: dict = service.validate_token()
        return bool(content)


class TenantCreateCommand(serializers.Serializer):
    tenant_admin_first_name = serializers.CharField(required=True)
    tenant_admin_last_name = serializers.CharField(required=True)
    tenant_admin_password = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def create(self, validated_data: dict) -> Tenant:
        conf_token = CreationTenantRequestTokenService(token=validated_data["token"])
        content = conf_token.validate_token()
        tenant_creation_request: TenantCreationRequest = (
            TenantCreationRequest.objects.get(id=content["tenant_request_id"])
        )

        # user params
        tenant_admin_first_name: str = validated_data["tenant_admin_first_name"]
        tenant_admin_last_name: str = validated_data["tenant_admin_last_name"]
        tenant_admin_password: str = validated_data["tenant_admin_password"]

        tenant_service = TenantService(
            request=tenant_creation_request,
            tenant_admin_first_name=tenant_admin_first_name,
            tenant_admin_last_name=tenant_admin_last_name,
            tenant_admin_password=tenant_admin_password,
        )
        new_tenant = tenant_service.create_tenant()
        tenant_admin: User = tenant_service.finish_registration(new_tenant=new_tenant)
        EmailService.send_email(
            subject="Добро пожаловать в Access Controller!",
            message=render_to_string(
                "mailing/tenant_registration_completed.html",
                context={
                    "user": tenant_admin,
                    "app_link": tenant_creation_request.domain,
                    "admin_link": get_host(
                        request=self.context["request"],
                        domain=tenant_creation_request.domain,
                        with_protocol=True,
                    )
                    + "/admin",
                },
            ),
            recipients_email=[tenant_admin.email],
        )
        return new_tenant


class TenantFullOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = "__all__"


class TenantAfterCreateCommandSerializer(serializers.ModelSerializer):
    domain_url = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = ["name", "admin_email", "domain_url"]

    def get_domain_url(self, instance: Tenant):
        domain: Domain = Domain.objects.get(tenant=instance)
        return f"https://{domain.domain}"
