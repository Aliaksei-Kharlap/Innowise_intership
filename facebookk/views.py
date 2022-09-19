
from rest_framework import viewsets

from facebookk.models import Page, Post, Tag
from facebookk.serializers import PageSerializer, TagSerializer, PostSerializer


# Create your views here.


class PagesViewSet(viewsets.ModelViewSet):

    queryset = Page.objects.all()
    serializer_class = PageSerializer


class PostsViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer