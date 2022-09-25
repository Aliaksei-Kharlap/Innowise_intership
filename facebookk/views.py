from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status, exceptions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated

from business_logic import permissions
from facebookk.models import Page, Post, Tag, Like, UnLike
from facebookk.serializers import PageSerializer, TagSerializer, PostSerializer, LikeSerializer, \
    UnLikeSerializer, SearchSerializers
from myuser.models import User
from myuser.serializers import UserSerializer, UserBlockSerializer


class PagesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = Page.objects.filter(is_block=False)
    serializer_class = PageSerializer



    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = (IsAuthenticated, )
        elif self.action == 'create':
            self.permission_classes = (IsAuthenticated,)
        elif self.action == 'retrieve':
            self.permission_classes = (AllowAny,)
        elif self.request.method == 'PUT':
            self.permission_classes = (permissions.OwnerOnlyPage,)
        elif self.action == 'delete' or self.action == 'delete_tag':
            self.permission_classes = (permissions.OwnerOnlyPage,)
        elif self.action == 'get_block_pages':
            self.permission_classes = (permissions.AdminModerOnly,)
        elif self.action == 'get_all_pages_tags' or self.action == 'create_tag' or \
            self.action == 'follows_request':
            self.permission_classes = (IsAuthenticated,)
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['get'])
    def get_block_pages(self, request, pk):
        pages = Page.objects.filter(is_block=True)
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_all_pages_tags(self, request, pk):
        tags = Page.objects.get(pk=pk, is_block=False).tags.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=TagSerializer)
    def create_tag(self, request, pk):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            page = Page.objects.get(pk=pk, is_block=False)
            pages = User.objects.get(pk=request.user.pk).relpages.all()
            if page in pages:
                obj = serializer.save()
                page.tags.add(obj)
                page.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else: return Response("do ont have acсess")

    @action(detail=True, methods=['post'], serializer_class=TagSerializer)
    def delete_tag(self, request, pk):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            tag = Tag.objects.get(pk=serializer.id)
            page = Page.objects.get(pk=pk, is_block=False)
            page.tags.remove(tag)
            page.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("do ont have acсess")
    @action(detail=True, methods=['get', 'head', 'delete'])
    def follows_request(self, request, pk):
        if request.method == "GET":
            pages = request.user.relpages.all()
            page = Page.objects.get(pk=pk)
            if page in pages:
                subs = Page.objects.get(pk=pk, is_block=False).follow_requests.all()
                serializer = UserSerializer(subs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("You do not have acces")

        if request.method == "HEAD":
            pages = request.user.relpages.all()
            page = Page.objects.get(pk=pk, is_block=False)
            if page in pages:
                subs = page.follow_requests.all()
                for sub in subs:
                    page.followers.add(subs)
                    page.follow_requests.remove()
                page.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response("You do not have acces")

        if request.method == "DELETE":
            page = Page.objects.get(pk=pk, is_block=False)
            pages = request.user.relpages.all()
            subs = page.follow_requests.all()
            if page in pages:
                page.follow_requests.clear()
                page.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response("You do not have acces")

    @action(detail=True, methods=['post'])
    def add_folowwer(self, request, pk):
        pages = request.user.relpages.all()
        page = Page.objects.get(pk=pk, is_block=False)
        if page in pages:
            user_id = UserBlockSerializer(data=request.data)
            if user_id.is_valid():
                user_id = user_id.validated_data["id"]
                user = User.objects.get(pk=user_id)
                if user in page.follow_requests.all():
                    page.follow_requests.remove(user)
                    page.followers.add(user)
                    page.save()
                    return Response(status=status.HTTP_200_OK)
            return Response("You are wrong")

    @action(detail=True, methods=['post'])
    def del_folowwer(self, request, pk):
        pages = request.user.relpages.all()
        page = Page.objects.get(pk=pk, is_block=False)
        if page in pages:
            user_id = UserBlockSerializer(data=request.data)
            if user_id.is_valid():
               user_id = user_id.validated_data["id"]
                user = User.objects.get(pk=user_id)
                if user in page.follow_requests.all():
                    page.follow_requests.remove(user)
                    page.save()
                    return Response(status=status.HTTP_200_OK)
            return Response("You are wrong")





class PostsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Post.objects.filter(page__is_block=False)
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = (IsAuthenticated,)
        elif self.action == 'create':
            self.permission_classes = (IsAuthenticated,)
        elif self.action == 'retrieve':
            self.permission_classes = (AllowAny,)
        elif self.action == 'update':
            self.permission_classes = (permissions.OwnerOnlyPost,)
        elif self.action == 'delete':
            self.permission_classes = (permissions.AdminModerOwnerOnly,)
        elif self.action == 'create_like' or self.action == 'create_unlike':
            self.permission_classes = (IsAuthenticated,)
        return [permission() for permission in self.permission_classes]

    def list(self, request):
        user = request.user
        posts = Post.objects.filter(Q(page__is_block=False), Q(page__followers=user) | Q(page__owner=user))
        objs = self.get_serializer(posts, many=True)
        return Response(objs.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def create_like(self, request, pk):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            post = Post.objects.get(pk=pk)
            user = request.user
            posts = Post.objects.filter(like_fil__user_from=request.user)
            if post in posts:
                return Response("You already created like for this post")
            else:
                obj = serializer.save(post_to=post, user_from=user)
            return Response(obj.data, status=status.HTTP_201_CREATED)
        else:
            return Response("Something wrong, try again")

    @action(detail=True, methods=['post'])
    def create_unlike(self, request, pk):
        serializer = UnLikeSerializer(data=request.data)
        if serializer.is_valid():
            post = Post.objects.get(pk=pk)
            user = request.user
            posts = Post.objects.filter(unlike_fil__user_from=request.user)
            if post in posts:
                return Response("You already created unlike for this post")
            else:
                obj = serializer.save(post_to=post, user_from=user)
            return Response(obj.data, status=status.HTTP_201_CREATED)
        else:
            return Response("Something wrong, try again")


    # def list(self, request):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # def retrieve(self, request, pk=None):
    #     queryset = self.get_queryset()
    #     user = get_object_or_404(queryset, pk=pk)
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # def create(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    #
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

class LikeViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin,
                  mixins.ListModelMixin):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def get_permissions(self):
        if self.action == 'delete':
            self.permissions_classes = (permissions.OwnerOnlyLikeUnlike,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return [permission() for permission in self.permission_classes]

    def list(self, request):
        posts = Post.objects.filter(like_fil__user_from=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UnLikeViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):

    queryset = UnLike.objects.all()
    serializer_class = UnLikeSerializer

    def get_permissions(self):
        if self.action == 'delete':
            self.permissions_classes = (permissions.OwnerOnlyLikeUnlike,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return [permission() for permission in self.permission_classes]


class SearchViewSet(viewsets.GenericViewSet):
    serializer_class = SearchSerializers
    permission_classes = (IsAuthenticated,)
    @action(detail=False, methods=['post'])
    def search(self, request):
        search = self.get_serializer(data=request.data)
        if search.is_valid():
            search = search.validated_data["search"]
            users = User.objects.filter(Q(username__icontains=search) & Q(is_blocked=False))
            pages = Page.objects.filter(Q(is_block=False), Q(name__icontains=search) | Q(uuid__icontains=search) |
                                    Q(tags__name=search)).distinct()

            users = UserSerializer(users, many=True)
            pages = PageSerializer(pages, many=True)


            return Response({
                'users': users.data,
                'pages': pages.data
            })
        else: return Response("Something wrong")


