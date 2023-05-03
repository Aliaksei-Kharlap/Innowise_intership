import logging

from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from business_logic import permissions
from myuser.myuser_services import upload_file_to_s3_and_return_answer, block_unblock_user_and_return_answer
from myuser.models import User
from myuser.serializers import UserSerializer, LoginSerializer, UserBlockOrUnblockSerializer, UserAddImageSerializer




class UsersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = User.objects.all()

    permission_classes_by_action = {
        "list": [permissions.AdminModerOnly],
        "default": [IsAuthenticated],
        "create": [AllowAny],
        "retrieve": [AllowAny],
        "update": [permissions.OwnerOnlyUser],
        "delete": [permissions.AdminModerOwnerOnly],
        "add_image": [AllowAny]
    }

    serializer_classes_by_action = {
        "list": UserSerializer,
        "default": UserSerializer,
        "create": UserSerializer,
        "retrieve": UserSerializer,
        "update": UserSerializer,
        "delete": UserSerializer,
        "add_image": UserAddImageSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes_by_action[self.action]

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except KeyError:
            return [
                permission()
                for permission in self.permission_classes_by_action["default"]
            ]

    @action(detail=False, methods=['post'])
    def add_image(self, request):
        return upload_file_to_s3_and_return_answer(request)




class LoginViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer


    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("Something Wrong")


class UserBlockViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AdminModerOnly,)
    serializer_class = UserBlockOrUnblockSerializer

    @action(detail=False, methods=['post'])
    def block(self, request):
        user = self.get_serializer(data=request.data)
        return block_unblock_user_and_return_answer(user, True)

    @action(detail=False, methods=['post'])
    def unblock(self, request):
        user = self.get_serializer(data=request.data)
        return block_unblock_user_and_return_answer(user, False)
