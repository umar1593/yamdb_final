from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorAdminModeratorOrReadOnly(BasePermission):
    """
    Права доступа для автора, админа, модератора и только для чтения.
    """

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)


class AdminOrReadOnly(BasePermission):
    """
    Права доступа для админа и только для чтения.
    """

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser)))


class Admin(BasePermission):
    """
    Права доступа для админа.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_admin
        )


class Moderator(BasePermission):
    """
    Права доступа для модератора.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_moderator
        )


class SuperUser(BasePermission):
    """
    Права доступа для superuser.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
            or request.user.is_admin
        )
