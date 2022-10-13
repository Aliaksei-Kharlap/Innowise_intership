import datetime

import boto3
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from mysite import settings
from myuser.models import User


def upload_file_to_s3_and_return_answer(request):
    file = request.FILES['image']
    user = request.user
    file_name = str(user.username)

    FILE_FORMAT = ('image/jpeg', 'image/png',)

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

            user.image_s3_path = url
            user.save()
            return Response("Success")
        except Exception as err:

            return Response(f"{err}")
    else:
        return Response("This format is not allowed")


def block_unblock_user_and_return_answer(user, status):
    if user.is_valid():
        user.save()
        user_id = user.id
        user = get_object_or_404(User, pk=user_id.id)
        user.is_blocked = status
        user.save()
        pages = user.relpages.all()
        for page in pages:
            page.is_block = status
            if not status:
                page.unblock_date = datetime.datetime.now()
            page.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response('Something wrong')
