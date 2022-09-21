from rest_framework import serializers
from django.contrib.admin import helpers

from facebookk.models import Tag, Page, Post, Subscription


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

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'user_from', 'user_to', 'status')