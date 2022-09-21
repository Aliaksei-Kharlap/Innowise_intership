from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from myuser.models import User
from myuser.serializers import UserSerializer, LoginSerializer


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


