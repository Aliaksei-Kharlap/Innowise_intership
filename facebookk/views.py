import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated

from business_logic import permissions
from facebookk.facebookk_services import add_page_image_and_return_answer, create_tag_and_return_answer, \
    delete_tag_and_return_answer, modify_follows_requests_and_return_answer, add_or_del_follower_and_return_answer, \
    create_and_send_mail_and_return_answer, create_like_or_unlike, search_and_return_answer, \
    get_statistics_and_return_answer
from facebookk.models import Page, Post, Like, UnLike
from facebookk.serializers import PageSerializer, TagSerializer, PostSerializer, SearchSerializers, \
    PageAddImageSerializer, StatisticSerializer, LikeSerializer, UnLikeSerializer


class PagesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = Page.objects.filter(is_block=False)
    serializer_class = PageSerializer

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAuthenticated],
        "retrieve": [AllowAny],
        "update": [permissions.OwnerOnlyPage],
        "delete": [permissions.OwnerOnlyPage],
        "delete_tag": [permissions.OwnerOnlyPage],
        "get_block_pages": [permissions.AdminModerOnly],
        "get_all_pages_tags": [IsAuthenticated],
        "create_tag": [IsAuthenticated],
        "follows_request": [IsAuthenticated],
        "default": [IsAuthenticated],
        'get_statistics': [permissions.OwnerOnlyPage]
    }

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

    serializer_classes_by_action = {
        "list": PageSerializer,
        "create": PageSerializer,
        "retrieve": PageSerializer,
        "update": PageSerializer,
        "delete": PageSerializer,
        "get_block_pages": PageSerializer,
        "get_all_pages_tags": TagSerializer,
        "get_statistics": StatisticSerializer,
        "partial_update": PageSerializer,

    }

    def get_serializer_class(self):
        print(self.action)
        return self.serializer_classes_by_action[self.action]


    @action(detail=True, methods=['post'], serializer_class=PageAddImageSerializer)
    def add_page_image(self, request, pk):
        return add_page_image_and_return_answer(request, pk)


    @action(detail=False, methods=['get'])
    def get_block_pages(self, request, pk):
        pages = Page.objects.filter(is_block=True)
        serializer = self.get_serializer(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_all_pages_tags(self, request, pk):
        tags = get_object_or_404(Page, pk=pk, is_block=False).tags.all()
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=TagSerializer)
    def create_tag(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        return create_tag_and_return_answer(request, pk, serializer)


    @action(detail=True, methods=['post'], serializer_class=TagSerializer)
    def delete_tag(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        return delete_tag_and_return_answer(serializer, pk)

    @action(detail=True, methods=['get', 'head', 'delete'])
    def follows_request(self, request, pk):
        return modify_follows_requests_and_return_answer(request, pk)


    @action(detail=True, methods=['post'])
    def add_follower(self, request, pk):
        return add_or_del_follower_and_return_answer(request, pk, True)

    @action(detail=True, methods=['post'])
    def del_follower(self, request, pk):
        return add_or_del_follower_and_return_answer(request, pk, False)

    @action(detail=True, methods=['get'])
    def get_statistics(self, request, pk):
        return get_statistics_and_return_answer(pk)

class PostsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = Post.objects.filter(page__is_block=False)
    serializer_class = PostSerializer

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAuthenticated],
        "retrieve": [AllowAny],
        "update": [permissions.OwnerOnlyPost],
        "delete": [permissions.AdminModerOwnerOnly],
        "create_like": [permissions.OwnerOnlyPage],
        "create_unlike": [IsAuthenticated],
        "default": [IsAuthenticated]
    }

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

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        return create_and_send_mail_and_return_answer(serializer)

    def list(self, request):
        user = request.user
        posts = Post.objects.filter(Q(page__is_block=False), Q(page__followers=user) | Q(page__owner=user))
        objs = self.get_serializer(posts, many=True)
        return Response(objs.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], serializer_class=LikeSerializer)
    def create_like(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        return create_like_or_unlike(request, serializer, pk, True)

    @action(detail=True, methods=['post'], serializer_class=UnLikeSerializer)
    def create_unlike(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        return create_like_or_unlike(request, serializer, pk, False)


class LikeViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin,
                  mixins.ListModelMixin):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    permission_classes_by_action = {
        "delete": [permissions.OwnerOnlyLikeUnlike],
        "default": [IsAuthenticated]
    }

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


    def list(self, request):
        posts = Post.objects.filter(like_fil__user_from=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UnLikeViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):

    queryset = UnLike.objects.all()
    serializer_class = UnLikeSerializer

    permission_classes_by_action = {
        "delete": [permissions.OwnerOnlyLikeUnlike],
        "default": [IsAuthenticated]
    }

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

class SearchViewSet(viewsets.GenericViewSet):
    serializer_class = SearchSerializers
    permission_classes = (IsAuthenticated,)
    @action(detail=False, methods=['post'])
    def search(self, request):
        search = self.get_serializer(data=request.data)
        return search_and_return_answer(search)
