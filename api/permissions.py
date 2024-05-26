from rest_framework import permissions

class IsCoordinator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='coordinator').exists()
    
class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='student').exists()