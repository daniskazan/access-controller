from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.request import Request

from producer import producer, EventType
from core.models import Application
from api.permissions.application import ChangeApplicationPermission
from api.v1.serializers.request.application import (
    CreateApplicationSerializer,
    FullApplicationSerializer,
)
from core.services.application import change_application_status_to_confirm
from api.filters.application import ApplicationFilter

from dataclasses import dataclass, asdict


@dataclass
class ApplicationApprovedEvent:
    application_id: int
    user_id: int
    resource_id: int
    scope: int


@dataclass
class GrantActivatedEvent:
    application_id: int


class ApplicationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    filterset_class = ApplicationFilter
    permission_classes = [ChangeApplicationPermission]

    def get_queryset(self):
        return (
            Application.objects.select_related("confirm_by", "resource")
            .order_by("created_at")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CreateApplicationSerializer
        if self.action == "confirm":
            return None
        return FullApplicationSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(
            data=FullApplicationSerializer(instance=application).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["PATCH"], detail=True, url_path="confirm")
    def confirm(self, request: Request, *args, **kwargs):
        application = self.get_object()
        application = change_application_status_to_confirm(application=application)
        producer.publish(
            routing_key=EventType.APPLICATION_APPROVED,
            message=asdict(
                ApplicationApprovedEvent(
                    user_id=application.user.pk,
                    application_id=application.pk,
                    resource_id=application.resource.pk,
                    scope=application.scope,
                )
            ),
        )
        return Response(status=status.HTTP_200_OK)
