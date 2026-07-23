from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Only the task's owner may retrieve/update/delete it.
    Prevents user A from viewing or editing user B's tasks via a guessed ID."""

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id
