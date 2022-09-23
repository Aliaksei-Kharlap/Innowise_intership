from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from facebookk.models import Page, Post, Tag, Like, UnLike
from facebookk.serializers import PageSerializer, TagSerializer, PostSerializer, LikeSerializer, \
    UnLikeSerializer, SearchSerializers
from myuser.models import User
from myuser.serializers import UserSerializer, UserBlockSerializer


class PagesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = Page.objects.filter(is_block=False)
    serializer_class = PageSerializer

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
            user_id = UserBlockSerializer(data=request.data).id
            user = User.objects.get(pk=user_id)
            if user in page.follow_requests.all():
                page.follow_requests.remove(user)
                page.followers.add(user)
                page.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response("You are wrong")

    @action(detail=True, methods=['post'])
    def del_folowwer(self, request, pk):
        pages = request.user.relpages.all()
        page = Page.objects.get(pk=pk, is_block=False)
        if page in pages:
            user_id = UserBlockSerializer(data=request.data).id
            user = User.objects.get(pk=user_id)
            if user in page.follow_requests.all():
                page.follow_requests.remove(user)
                page.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response("You are wrong")





class PostsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


    def list(self, request):
        user = request.user
        posts = Post.objects.filter(Q(page__followers=user) | Q(page__owner=user))
        objs = self.get_serializer(posts, many=True)
        return Response(objs.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def create_like(self, request, pk):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            post = Post.objects.get(pk=pk)
            user = User.objects.get(pk=request.user.pk)
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
            user = User.objects.get(pk=request.user.pk)
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


class TagsViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class LikeViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                  mixins.ListModelMixin):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def list(self, request):
        posts = Post.objects.filter(like_fil__user_from=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class UnLikeViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):

    queryset = UnLike.objects.all()
    serializer_class = UnLikeSerializer

class SearchViewSet(viewsets.GenericViewSet):
    serializer_class = SearchSerializers
    @action(detail=False, methods=['post'])
    def search(self, request):
        search = self.get_serializer(data=request.data).search
        users = User.objects.filter(Q(username__icontains=search) & Q(is_blocked=False))
        pages = Page.objects.filter(Q(is_block=False), Q(name__icontains=search) | Q(uuid__icontains=search) |
                                    Q(tags__name=search).distinct())
        users = UserSerializer(users, many=True)
        pages = PageSerializer(pages, many=True)

        return Response({
            'users': users,
            'pages': pages
        })


