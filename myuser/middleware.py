from datetime import datetime

import jwt
from rest_framework import exceptions
from rest_framework.response import Response

from mysite import settings
from myuser.models import User

from django.contrib.auth.models import AnonymousUser

def jwt_auth_middleware(get_response):
    def middleware(request):
        header = request.headers.get('Authorization')

        if not header:
            request.user = User.objects.get(pk=1) #AnonymousUser()
        else:
            try:
                access_token = header.split(' ')[1]
                payload = jwt.decode(
                    access_token, settings.SECRET_KEY, algorithms=['HS256'])

            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Access_token expired')
            except IndexError:
                raise exceptions.AuthenticationFailed('Token prefix missing')

            tm = int(payload['exp'])
            if tm < int(datetime.now().strftime('%s')):
                raise exceptions.AuthenticationFailed('Access_token is not valid, please, login')

            user = User.objects.get(id=payload['id'])

            if user is None:
                raise exceptions.AuthenticationFailed('User not found')

            if user.is_blocked:
                raise exceptions.AuthenticationFailed('User is blocked')


            request.user = user


        response = get_response(request)

        return response

    return middleware
