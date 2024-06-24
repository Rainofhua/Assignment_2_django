from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return True
        return obj.Administrators == request.user


class IsLecturerReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET"]:
            return True
        return obj.Lecturers == request.user


class IsStudentReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET"]:
            return True
        return obj.Students == request.user
