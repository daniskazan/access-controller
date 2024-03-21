from django_filters import rest_framework as filter


from core.models import Resource


class ResourceFilter(filter.FilterSet):
    resource_group = filter.CharFilter(
        field_name="resource_group__name", lookup_expr="icontains"
    )

    class Meta:
        model = Resource
        fields = ("resource_group",)
