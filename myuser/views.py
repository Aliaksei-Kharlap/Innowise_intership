from rest_framework import viewsets

from myuser.models import User
from myuser.serializers import UserSerializer


class UsersViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer