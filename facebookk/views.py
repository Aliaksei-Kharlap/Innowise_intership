import json
from datetime import datetime

from django.shortcuts import get_object_or_404
from kafka import KafkaConsumer, KafkaProducer
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated

from business_logic import permissions
from business_logic.facebookk_services import add_page_image_and_return_answer, create_tag_and_return_answer, \
    delete_tag_and_return_answer, modify_follows_requests_and_return_answer, add_or_del_follower_and_return_answer, \
    create_and_send_mail_and_return_answer, create_like_or_unlike, search_and_return_answer
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
        producer = KafkaProducer(
            bootstrap_servers=["kafka:9092"],
            value_serializer=lambda x: json.dumps(x).encode("utf-8")
        )
        producer.send("req", value={'id':pk})

        concumer = KafkaConsumer(
            "res",
            bootstrap_servers=["kafka:9092"],
            auto_offset_reser="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )

        time = datetime.now()
        while True:
            for mess in concumer:
                if mess.value["id"] == pk:
                    res = mess.value
                    return Response(res.data, status=status.HTTP_200_OK)
                    break
            time2 = datetime.now()
            if time2.second - time.second > 5:
                break
        return Response("Something wrong, try again")

        #res = json.loads(requests.get(f'http://127.0.0.1:8001/{pk}').content)
        #res = self.get_serializer(res)
        #return Response(res.data, status=status.HTTP_200_OK)

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
