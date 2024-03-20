from rest_framework.permissions import IsAuthenticated

from core.models import Application


class ChangeApplicationPermission(IsAuthenticated):
    """
    Подтверждать заявку может  - тимлид того кто создал заявку
    """

    def has_object_permission(self, request, view, obj: Application):
        user = request.user
        has = user.has_perm("core.can_approve_applicationjj")
        return has
        # return obj.confirm_by == request.user
