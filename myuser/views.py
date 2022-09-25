import datetime

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from business_logic import permissions
from facebookk.models import Post
from myuser.models import User
from myuser.serializers import UserSerializer, LoginSerializer, UserBlockSerializer


class UsersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = (permissions.AdminModerOnly,)
        elif self.action == 'create':
            self.permission_classes = (AllowAny,)
        elif self.action == 'retrieve':
            self.permission_classes = (AllowAny,)
        elif self.action == 'update':
            self.permission_classes = (permissions.OwnerOnlyUser,)
        elif self.action == 'delete':
            self.permission_classes = (permissions.AdminModerOwnerOnly,)
        return [permission() for permission in self.permission_classes]



class LoginViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def create(self, request):
        user = request.data
        serializer = self.get_serializer(data=user)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("Something Wrong")


class UserBlockViewSet(viewsets.GenericViewSet):

    permission_classes = (permissions.AdminModerOnly,)
    serializer_class = UserBlockSerializer
    @action(detail=False, methods=['post'])
    def block(self, request):
        user = self.get_serializer(data=request.data)
        if user.is_valid():
            user.save()
            user_id=user.id
            user = User.objects.get(pk=user_id)
            user.is_blocked = True
            user.save()
            pages = user.relpages.all()
            for page in pages:
                page.is_block = True
                page.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response("Something wrong")

    @action(detail=False, methods=['post'])
    def unblock(self, request):
        user_id = self.get_serializer(data=request.data)
        if user_id.is_valid():
            user_id.save()
            user = User.objects.get(pk=user_id.id)
            user.is_blocked = False
            user.save()
            pages = user.relpages.all()
            for page in pages:
                page.is_block = False
                page.unblock_date = datetime.datetime.now()
                page.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response('Something wrong')


