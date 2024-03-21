import uuid
from datetime import datetime, timedelta
from django.db import transaction
from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from core.models import User, InvitationToken
from api.v1.serializers.request.user import (
    UserInviteSerializer,
    UserAcceptInviteSerializer
)
from api.v1.serializers.response.user import (
    UserRegistrationSerializerOutput,
    UserFullOutputSerializer,
)
from core.services.user import UserInviteService


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return User.objects.prefetch_related("team", "role", "position").order_by("id")

    def get_permissions(self):
        if self.action in (
                "accept_invite",
                "invite"
        ):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "invite":
            return UserInviteSerializer
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

    @action(
        methods=["POST"],
        detail=False
    )
    def accept_invite(self, request: Request):
        serializer: UserAcceptInviteSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.to_representation(instance=user), status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False)
    def me(self, request: Request):
        return Response(
            data=UserFullOutputSerializer(instance=request.user).data,
            status=status.HTTP_200_OK,
        )
