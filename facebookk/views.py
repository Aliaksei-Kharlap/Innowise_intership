from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from facebookk.models import Page, Post, Tag, Subscription
from facebookk.serializers import PageSerializer, TagSerializer, PostSerializer, SubscriptionSerializer
from myuser.models import User



class PagesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    queryset = Page.objects.all()
    serializer_class = PageSerializer

    @action(detail=True, methods=['get'])
    def get_all_pages_tags(self, request, pk):
        tags = Page.objects.get(pk=pk).tags.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=TagSerializer)
    def create_tag(self, request, pk):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            page = Page.objects.get(pk=pk)
            pages = User.objects.get(pk=request.user.pk).relpages.all()
            if page in pages:
                obj = serializer.save()
                page.tags.add(obj)
                page.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'head', 'delete'])
    def subscriptions_to_me(self, request, pk):
        if request.method == "GET":
            subs = Page.objects.get(pk=pk).pages_to.all()
            serializer = SubscriptionSerializer(subs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "HEAD":
            page = Page.objects.get(pk=pk)
            subs = page.pages_to.all()
            for sub in subs:
                sub.status = True
                sub.save()
                page.followers.add(sub.user_from)
                page.save()
            return Response(status=status.HTTP_200_OK)
        if request.method == "DELETE":
            page = Page.objects.get(pk=pk)
            subs = page.pages_to.all()
            for sub in subs:
                sub.status = False
                sub.save()

    @action(detail=True, methods=['post'])
    def create_subscription(self, request, pk):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            page = Page.objects.get(pk=pk)
            user = User.objects.get(pk=request.user.pk)
            if page.is_private:
                obj = serializer.save(page_to=page, user_from=user, status=None)
                return Response(obj.data, status=status.HTTP_201_CREATED)
            else:
                obj = serializer.save(page_to=page, user_from=user, status=True)
                page.followers.add(user)
                page.save()
                return Response(obj.data, status=status.HTTP_201_CREATED)



class PostsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

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

class SubscriptionViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin):

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


    @action(detail=True, methods=['get'])
    def agree_subscription(self, request, pk):
        user = request.user
        sub = Subscription.objects.get(pk=pk)
        user_have = sub.page_to.owner
        if user == user_have:
            sub.status = True
            sub.save()
            page = sub.page_to
            page.followers.add(sub.user_from)
            page.save()
            Response(status=status.HTTP_200_OK)
        else:
            Response(status=status.HTTP_423_LOCKED)

    @action(detail=True, methods=['head'])
    def disagree_subscription(self, request, pk):
        user = request.user
        sub = Subscription.objects.get(pk=pk)
        user_have = sub.page_to.owner
        if user == user_have:
            sub.status = False
            sub.save()
            Response(status=status.HTTP_200_OK)
        else:
            Response(status=status.HTTP_423_LOCKED)