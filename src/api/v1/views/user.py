from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from core.models import User
from api.v1.serializers.request.user import UserRegistrationSerializer
from api.v1.serializers.response.user import (
    UserRegistrationSerializerOutput,
    UserFullOutputSerializer,
)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return User.objects.prefetch_related("team", "role", "position").order_by("id")

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        return UserFullOutputSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            data=UserRegistrationSerializerOutput(instance=user).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["POST"], detail=False)
    def invite(self, request: Request, *args, **kwargs):
        return Response()

    @action(methods=["GET"], detail=False)
    def me(self, request: Request):
        return Response(
            data=UserFullOutputSerializer(instance=request.user).data,
            status=status.HTTP_200_OK,
        )
