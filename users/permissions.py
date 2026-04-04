from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSuperAdmin(BasePermission):
    """Only superadmin."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'superadmin'
        )

class IsAdminOrAbove(BasePermission):
    """Admin + Superadmin — can manage transactions."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('admin', 'superadmin')
        )

class IsAnalystOrAbove(BasePermission):
    """Analyst + Admin + Superadmin — can view dashboard."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('analyst', 'admin', 'superadmin')
        )

class IsViewerOrAbove(BasePermission):
    """All authenticated roles — can view transactions."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('viewer', 'analyst', 'admin', 'superadmin')
        )