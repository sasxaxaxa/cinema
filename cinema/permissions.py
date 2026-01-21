from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Разрешение только для администраторов и суперпользователей.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Проверяем суперпользователя
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Проверяем профиль пользователя
        if hasattr(request.user, 'profile'):
            return request.user.profile.is_admin()
        
        return False


class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение для модераторов и администраторов.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Проверяем суперпользователя
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Проверяем профиль пользователя
        if hasattr(request.user, 'profile'):
            return request.user.profile.is_moderator()
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для администраторов.
    Чтение доступно всем.
    """
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверяем авторизацию
        if not request.user.is_authenticated:
            return False
        
        # Проверяем суперпользователя
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Проверяем профиль пользователя
        if hasattr(request.user, 'profile'):
            return request.user.profile.is_admin()
        
        return False