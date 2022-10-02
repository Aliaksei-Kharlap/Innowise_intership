from rest_framework.permissions import BasePermission, SAFE_METHODS


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
        return request.user.role == "admin" or request.user.role == "moderator"




class AdminModerOwnerOnly(BasePermission):

    def has_permission(self, request, view):

        return request.user.role == "admin" or request.user.role == "moderator"


    def has_object_permission(self, request, view, obj):
        return request.user.role == "admin" or request.user.role == "moderator" or obj == request.user