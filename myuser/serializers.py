from rest_framework import serializers

from myuser.models import User


class UserSerializer(serializers.ModelSerializer):
    relpages = serializers.PrimaryKeyRelatedField(many=True)
    follows = serializers.PrimaryKeyRelatedField(many=True)
    requests = serializers.PrimaryKeyRelatedField(many=True)


    class Meta:
        model = User
        fields = ['id', 'email', 'image_s3_path', 'role', 'title', 'is_blocked', 'relpages', 'follows', 'requests']