from rest_framework import serializers

from facebookk.models import Tag, Page, Post


class TagSerializer(serializers.ModelSerializer):
    pages = serializers.PrimaryKeyRelatedField(many=True)
    class Meta:
        model = Tag
        fields = ['id', 'name', 'pages']


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'name', 'uuid', 'description', 'tags', 'owner', 'followers', 'image', 'is_private',
                  'follow_requests', 'created_date', 'unblock_date']


class PostSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(many=True)
    replies = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Post
        fields = ['id', 'page', 'content', 'reply_to', 'created_at', 'updated_at', 'posts', 'replies']