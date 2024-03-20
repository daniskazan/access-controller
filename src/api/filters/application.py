from django_filters import rest_framework as filter

from core.models import Application


class ApplicationFilter(filter.FilterSet):
    user = filter.CharFilter(field_name="user__first_name", lookup_expr="icontains")

    class Meta:
        model = Application
        fields = (
            "status",
            "user",
        )
