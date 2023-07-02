from rest_framework.permissions import BasePermission


class IsSameGuest(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.guest)
