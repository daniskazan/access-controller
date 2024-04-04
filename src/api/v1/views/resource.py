from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import filters
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from api.filters.resource import ResourceFilter
from core.models import Resource, ResourceGroup
from api.v1.serializers.request.resource import ResourceSerializer


class ResourceViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    filter_backends = [filters.SearchFilter]
    search_fields = ["resource_group__name", "name"]
    queryset = Resource.objects.all().order_by("id")
    serializer_class = ResourceSerializer

    @staticmethod
    def get_available_resource_names() -> list[dict[str, str]]:
        resource_names = ResourceGroup.objects.distinct("name").values("name")
        return resource_names

    @action(methods=["GET"], detail=False)
    def types(self, request: Request):
        data = self.get_available_resource_names()
        return Response(data, status=status.HTTP_200_OK)
