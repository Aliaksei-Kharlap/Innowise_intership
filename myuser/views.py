from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from facebookk.models import Post
from myuser.models import User
from myuser.serializers import UserSerializer, LoginSerializer, UserBlockSerializer


class UsersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer



class LoginViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def create(self, request):
        user = request.data
        serializer = self.get_serializer(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserBlockViewSet(viewsets.GenericViewSet):

    serializer_class = UserBlockSerializer
    @action(detail=False, methods=['post'])
    def block(self, request):
        user_id = self.get_serializer(data=request.data).id
        user = User.objects.get(pk=user_id)
        user.is_blocked = True
        user.save()
        pages = user.relpages.all()
        for page in pages:
            page.is_block = True
            page.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def unblock(self, request):
        user_id = self.get_serializer(data=request.data).id
        user = User.objects.get(pk=user_id)
        user.is_blocked = False
        user.save()
        pages = user.relpages.all()
        for page in pages:
            page.is_block = False
            page.save()
        return Response(status=status.HTTP_200_OK)


