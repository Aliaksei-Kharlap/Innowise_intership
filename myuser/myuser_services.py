import datetime
import logging

import boto3
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from mysite import settings
from myuser.models import User


logger = logging.getLogger(__name__)

def upload_file_to_s3_and_return_answer(request):
    file = request.FILES['image']
    user = request.user
    file_name = user.username
    FILE_FORMAT = ('image/jpeg', 'image/png',)

    if file.content_type in FILE_FORMAT:
        logger.info("Trying to upload file")

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
            user.save(update_fields=['image_s3_path'])

            logger.info("File uploaded successfully", extra={"file_url": url})
            return Response("Success")

        except Exception as err:
            logger.exception(err)       #logging.error(err, exc_info=True)
            return Response(f"{err}")

    logger.info("Attempt to upload wrong file's format", extra={"user_id": user.id})
    return Response("This format is not allowed")


def block_unblock_user_and_return_answer(user, status):
    if user.is_valid():
        user.save()
        user_id = user.id
        user = get_object_or_404(User, pk=user_id.id)
        user.is_blocked = status
        user.save(update_fields=['is_blocked'])
        pages = user.relpages.all()
        for page in pages:
            page.is_block = status
            if not status:
                page.unblock_date = datetime.datetime.now()
            page.save(update_fields=['is_block', 'unblock_date'])
        return Response(status=status.HTTP_200_OK)
    return Response('Something wrong')
