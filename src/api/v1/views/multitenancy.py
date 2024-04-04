from django.db import transaction
from django.template.loader import render_to_string
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from api.permissions.tenant import IsTenantAdminPermission
from api.v1.serializers.request.multitenancy import (
    TenantCreateCommand,
    TenantAfterCreateCommandSerializer,
    TenantCreationRequestCommandOutput,
    TenantCreationRequestCommand,
    TenantCreationRequestValidateTokenCommand,
    TenantFullOutputSerializer,
)
from core.models import TenantCreationRequest, Tenant
from core.services.mailing import EmailService
from core.services.multitenancy import send_confirm_email_tenant_creation_request


class TenantCreationRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    http_method_names = ["post", "delete"]
    permission_classes = [
        AllowAny,
    ]
    queryset = TenantCreationRequest.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return TenantCreationRequestCommand
        if self.action == "validate_token":
            return TenantCreationRequestValidateTokenCommand
        return TenantCreationRequestCommand

    def create(self, request: Request, *args, **kwargs):
        serializer: serializers.ModelSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        creation_tenant_request: TenantCreationRequest = serializer.save()
        send_confirm_email_tenant_creation_request(
            creation_tenant_request=creation_tenant_request
        )
        return Response(
            data=TenantCreationRequestCommandOutput(
                instance=creation_tenant_request
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                required=True,
            )
        ]
    )
    @action(methods=["GET"], detail=False, url_path="status")
    def validate_token(self, request: Request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class TenantViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return Tenant.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return TenantCreateCommand
        return TenantFullOutputSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsTenantAdminPermission()]
        return [AllowAny()]

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()
        return Response(data=TenantAfterCreateCommandSerializer(instance=tenant).data)
