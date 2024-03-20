from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import filters

from api.filters.resource import ResourceFilter
from core.models import Resource
from api.v1.serializers.request.resource import ResourceSerializer


class ResourceViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    filter_backends = [filters.SearchFilter]
    search_fields = ["resource_group__name"]
    queryset = Resource.objects.all().order_by("id")
    serializer_class = ResourceSerializer
