from rest_framework import serializers

from myuser.models import User

class UserSerializer(serializers.ModelSerializer):
    is_blocked = serializers.BooleanField(default=False, read_only=True)
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username', 'image_s3_path', 'role', 'title', 'is_blocked',)

class UserBlockOrUnblockSerializer(serializers.Serializer):
    id = serializers.IntegerField()




class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):

        email = data.get('email', None)
        password = data.get('password', None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if user.is_blocked:
            raise serializers.ValidationError(
                'This user has been blocked.'
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


class UserAddImageSerializer(serializers.Serializer):
    image = serializers.FileField()
