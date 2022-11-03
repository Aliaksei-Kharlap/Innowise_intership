from enum import Enum
from rest_framework.permissions import BasePermission, SAFE_METHODS

class Administrators(Enum):
    admin = "admin"
    moderator = "moderator"
    administrators = ["admin", "moderator"]

class OwnerOnlyUser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj


class OwnerOnlyPage(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner

class OwnerOnlyPost(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.page.owner


class OwnerOnlyLikeUnlike(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user_from



class AdminModerOnly(BasePermission):

    def has_permission(self, request, view):
        return request.user.role in Administrators.administrators.value

    def has_object_permission(self, request, view, obj):
        return request.user.role in Administrators.administrators.value




class AdminModerOwnerOnly(BasePermission):

    def has_permission(self, request, view):
        return request.user.role in Administrators.administrators.value

    def has_object_permission(self, request, view, obj):
        return request.user.role in Administrators.administrators.value or obj == request.user

class AdminOnly(BasePermission):

    def has_permission(self, request, view):
        return request.user.role in Administrators.admin.value

    def has_object_permission(self, request, view, obj):
        return request.user.role in Administrators.admin.value
