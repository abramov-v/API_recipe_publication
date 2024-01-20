from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS



class AdminOrReadOnly(BasePermission):
    """Пермишн с правами доступа для администраторов."""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user and request.user.is_superuser)