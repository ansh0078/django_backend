from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Grants access only to users flagged as admin (is_admin_user) or Django
    staff/superusers. Used to gate the React admin dashboard's endpoints.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_admin_user or user.is_staff or user.is_superuser)
        )