from rest_framework import serializers
from django.contrib.admin import helpers

from facebookk.models import Tag, Page, Post, Like, UnLike


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags', 'owner', 'followers', 'image', 'is_private',
                  'follow_requests', 'created_date', 'unblock_date')


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'page', 'content', 'reply_to', 'created_at', 'updated_at')


class LikeSerializer(serializers.Serializer):
    class Meta:
        model = Like
        fields = ('id', 'user_from', 'post_to')

class UnLikeSerializer(serializers.Serializer):
    class Meta:
        model = UnLike
        fields = ('id', 'user_from', 'post_to')



class SearchSerializers(serializers.Serializer):
    search = serializers.CharField(max_length=80)

class PageAddImageSerializer(serializers.Serializer):
    image = serializers.FileField()

class StatisticSerializer(serializers.Serializer):
    posts_count = serializers.IntegerField()
    followers_count = serializers.IntegerField()
    likes_count = serializers.IntegerField()
