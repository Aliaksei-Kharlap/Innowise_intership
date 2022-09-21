from rest_framework import serializers

from myuser.models import User
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    #token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'image_s3_path', 'role', 'title', 'is_blocked']


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):

        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if user.is_blocked:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        if user.check_password(password):
            return {
                'email': user.email,
                'token': user.token
            }
        else:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )