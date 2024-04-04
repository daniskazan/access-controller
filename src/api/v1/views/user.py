import uuid
from datetime import datetime, timedelta
from django.db import transaction
from drf_spectacular import openapi
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from core.models import User, InvitationToken
from api.v1.serializers.request.user import (
    UserInviteSerializer,
    GetTokenStatusSerializer,
    UserAcceptInviteSerializer,
)
from api.v1.serializers.response.user import (
    UserRegistrationSerializerOutput,
    UserFullOutputSerializer,
)
from core.services.user import UserInviteService
from core.utils import get_host


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return User.objects.prefetch_related("team", "role", "position").order_by("id")

    def get_permissions(self):
        if self.action in ("get_invite_token_status", "accept_invite", "invite", "tmp"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "get_invite_token_status":
            return GetTokenStatusSerializer
        if self.action == "accept_invite":
            return UserAcceptInviteSerializer
        return UserFullOutputSerializer

    @action(methods=["POST"], detail=False)
    @transaction.atomic
    def invite(self, request: Request, *args, **kwargs):
        serializer: UserInviteSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invited_user = serializer.save()
        invite_token = InvitationToken(
            user=invited_user,
            token=uuid.uuid4(),
            expired_at=datetime.now().utcnow() + timedelta(hours=72),
        )
        invite_token.save()

        invite_service = UserInviteService(
            user=invited_user, request=request, invitation_token=invite_token
        )
        invite_service.send_invitation()

        return Response(data=serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "invite_token", OpenApiTypes.UUID, OpenApiParameter.QUERY, required=True
            )
        ]
    )
    @action(methods=["GET"], detail=False, url_path="invite-token/status")
    def get_invite_token_status(self, request: Request):
        serializer: GetTokenStatusSerializer = self.get_serializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            serializer.to_representation(instance=user), status=status.HTTP_200_OK
        )

    @action(methods=["POST"], detail=False, url_path="invite/accept")
    def accept_invite(self, request: Request):
        serializer: UserAcceptInviteSerializer = self.get_serializer(
            data=request.data, instance=get_object_or_404(User, id=request.data["id"])
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            data=serializer.to_representation(user), status=status.HTTP_200_OK
        )

    @action(methods=["GET"], detail=False)
    def me(self, request: Request):
        return Response(
            data=UserFullOutputSerializer(instance=request.user).data,
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=False)
    def tmp(self, request):
        admin_link = get_host(request, with_protocol=True) + "/admin"
        print(admin_link)
        return Response()
