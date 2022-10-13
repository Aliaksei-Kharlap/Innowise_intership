import boto3
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status, exceptions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated

from business_logic import permissions
from facebookk.models import Page, Post, Tag, Like, UnLike
from facebookk.serializers import PageSerializer, TagSerializer, PostSerializer, LikeSerializer, \
    UnLikeSerializer, SearchSerializers, PageAddImageSerializer
from facebookk.services import send
from mysite import settings
from myuser.models import User
from myuser.serializers import UserSerializer, UserBlockSerializer


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

    # serializer_classes_by_action = {
    #     "list": UserSerializer,
    #     "default": UserSerializer,
    #     "create": UserSerializer,
    #     "retrieve": UserSerializer,
    #     "update": UserSerializer,
    #     "delete": UserSerializer,
    #     "add_image": UserAddImageSerializer,
    # }
    #
    # def get_serializer_class(self):
    #     print(self.action)
    #     return self.serializer_classes_by_action[self.action]


    @action(detail=True, methods=['post'], serializer_class=PageAddImageSerializer)
    def add_page_image(self, request, pk):
        file = request.FILES['image']
        page = get_object_or_404(Page, pk=pk)
        user = request.user
        file_name = page.name + user.username

        if page not in user.relpages.all():
            return Response("you do not have access")

        FILE_FORMAT = ('image/jpeg', 'image/png')

        if file.content_type in FILE_FORMAT:
            try:
                client_s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                )

                client_s3.upload_fileobj(
                    file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    file_name,
                )
                url = f's3://{settings.AWS_STORAGE_BUCKET_NAME}/{file_name}'
                page.image = url
                page.save()
                return Response("Success")
            except Exception as err:
                return Response(f"{err}")
        else:
            return Response("This format is not allowed")

    @action(detail=False, methods=['get'])
    def get_block_pages(self, request, pk):
        pages = Page.objects.filter(is_block=True)
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_all_pages_tags(self, request, pk):
        tags = get_object_or_404(Page, pk=pk, is_block=False).tags.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=TagSerializer)
    def create_tag(self, request, pk):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            page = get_object_or_404(Page, pk=pk, is_block=False)
            pages = get_object_or_404(User, pk=request.user.pk).relpages.all()
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
            tag = get_object_or_404(Tag, pk=serializer.id)
            page = get_object_or_404(Page, pk=pk, is_block=False)
            page.tags.remove(tag)
            page.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("do ont have acсess")
    @action(detail=True, methods=['get', 'head', 'delete'])
    def follows_request(self, request, pk):
        if request.method == "GET":
            pages = request.user.relpages.all()
            page = get_object_or_404(Page, pk=pk)
            if page in pages:
                subs = get_object_or_404(Page, pk=pk, is_block=False).follow_requests.all()
                serializer = UserSerializer(subs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("You do not have acces")

        if request.method == "HEAD":
            pages = request.user.relpages.all()
            page = get_object_or_404(Page, pk=pk, is_block=False)
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
            page = get_object_or_404(Page, pk=pk)
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
        page = get_object_or_404(Page, pk=pk, is_block=False)
        if page in pages:
            user_id = UserBlockSerializer(data=request.data)
            if user_id.is_valid():
                user_id = user_id.validated_data["id"]
                user = get_object_or_404(User, pk=user_id)
                if user in page.follow_requests.all():
                    page.follow_requests.remove(user)
                    page.followers.add(user)
                    page.save()
                    return Response(status=status.HTTP_200_OK)
            return Response("You are wrong")

    @action(detail=True, methods=['post'])
    def del_folowwer(self, request, pk):
        pages = request.user.relpages.all()
        page = get_object_or_404(Page, pk=pk, is_block=False)
        if page in pages:
            user_id = UserBlockSerializer(data=request.data)
            if user_id.is_valid():
                user_id = user_id.validated_data["id"]
                user = get_object_or_404(User, pk=user_id)
                if user in page.follow_requests.all():
                    page.follow_requests.remove(user)
                    page.save()
                    return Response(status=status.HTTP_200_OK)
            return Response("You are wrong")





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

    def create(self, request):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            send.delay(serializer.validated_data["page"].id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        user = request.user
        posts = Post.objects.filter(Q(page__is_block=False), Q(page__followers=user) | Q(page__owner=user))
        objs = self.get_serializer(posts, many=True)
        return Response(objs.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def create_like(self, request, pk):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            post = get_object_or_404(Post, pk=pk)
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
            post = get_object_or_404(Post, pk=pk)
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


