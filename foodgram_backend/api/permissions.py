from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Проверка, является ли пользователь администратором.
    Имеет ли пользователь роль 'admin' или статус 'is_superuser'."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
    
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user



class AllowAllUsers(BasePermission):
    """
    Custom permission to allow access to all users.
    """

    def has_permission(self, request, view):
        # Always return True to allow access to all users
        return True

class AdminRoleOrReadOnly(permissions.BasePermission):
    """
    Разрешение для предоставления доступа по роли 'admin'
    или 'is_superuser', или только чтения.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))


class IsAuthorModeratorAdmin(permissions.BasePermission):
    """
    Разрешение для предоставления доступа на основе авторства,
    роли 'admin' или 'moderator'.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)