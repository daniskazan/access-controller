from typing import Literal

from django.db.models import QuerySet, Q
from django_filters import rest_framework as filter

from core.models import Application


class ApplicationFilter(filter.FilterSet):
    user = filter.CharFilter(field_name="user__first_name", lookup_expr="icontains")
    to_confirm = filter.BooleanFilter(
        field_name="confirm_by",
        method="get_applications_to_confirm",
        label=" Return applications waiting for confirm by current user",
    )

    class Meta:
        model = Application
        fields = (
            "status",
            "user",
        )

    def get_applications_to_confirm(
        self, queryset: QuerySet, field_name: Literal["confirm_by"], value: bool
    ):
        if value:
            return queryset.filter(Q(confirm_by=self.request.user))
        return queryset
