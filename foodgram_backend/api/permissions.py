from rest_framework.permissions import SAFE_METHODS
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет только авторам объекта редактировать его.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or obj.author == request.user)
