from rest_framework.permissions import BasePermission


class IsTenantAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_tenant_admin
