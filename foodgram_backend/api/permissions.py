from rest_framework.permissions import SAFE_METHODS
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission that allows only the authors of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or obj.author == request.user
        )
