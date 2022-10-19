import boto3
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from facebookk.serializers import PageSerializer
from facebookk.tasks import send
from facebookk.models import Page, Tag, Post
from mysite import settings
from myuser.models import User
from myuser.serializers import UserSerializer, UserBlockOrUnblockSerializer


def add_page_image_and_return_answer(request, pk):
    file = request.FILES['image']
    page = get_object_or_404(Page, pk=pk)
    user = request.user
    file_name = page.name + user.username

    if page not in user.relpages.all():
        return Response("You do not have access")

    FILE_FORMAT = ('image/jpeg', 'image/png')

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
            page.image = url
            page.save(update_fields=['image'])
            return Response("Success")
        except Exception as err:
            return Response(f"{err}")
    else:
        return Response("This format is not allowed")


def create_tag_and_return_answer(request, pk, serializer):
    if serializer.is_valid():
        page = get_object_or_404(Page, pk=pk, is_block=False)
        pages = get_object_or_404(User, pk=request.user.pk).relpages.all()
        if page in pages:
            obj = serializer.save()
            page.tags.add(obj)
            page.save(update_fields=['tags'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response("Do not have acсess")
    return Response("Something wrong")

def delete_tag_and_return_answer(serializer, pk):
    if serializer.is_valid():
        serializer.save()
        tag = get_object_or_404(Tag, pk=serializer.id)
        page = get_object_or_404(Page, pk=pk, is_block=False)
        page.tags.remove(tag)
        page.save(update_fields=['tags'])
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response("Something wrong")


def modify_follows_requests_and_return_answer(request, pk):
    if request.method == "GET":
        pages = request.user.relpages.all()
        page = get_object_or_404(Page, pk=pk)
        if page in pages:
            subs = get_object_or_404(Page, pk=pk, is_block=False).follow_requests.all()
            serializer = UserSerializer(subs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("You do not have access")

    if request.method == "HEAD":
        pages = request.user.relpages.all()
        page = get_object_or_404(Page, pk=pk, is_block=False)
        if page in pages:
            subs = page.follow_requests.all()
            page.followers.add(subs)
            page.follow_requests.clear()
            page.save(update_fields=['followers', 'follow_requests'])
            return Response(status=status.HTTP_200_OK)
        else:
            return Response("You do not have access")

    if request.method == "DELETE":
        page = get_object_or_404(Page, pk=pk)
        pages = request.user.relpages.all()
        if page in pages:
            page.follow_requests.clear()
            page.save(update_fields=['follow_requests'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("You do not have access")
    return Response("Something wrong")


def add_or_del_follower_and_return_answer(request, pk, mod):
    pages = request.user.relpages.all()
    page = get_object_or_404(Page, pk=pk, is_block=False)
    if page in pages:
        user_id = UserBlockOrUnblockSerializer(data=request.data)
        if user_id.is_valid():
            user_id = user_id.validated_data["id"]
            user = get_object_or_404(User, pk=user_id)
            if user in page.follow_requests.all():
                page.follow_requests.remove(user)
                if mod:
                    page.followers.add(user)
                page.save(update_fields=['followers', 'follow_requests'])
                return Response(status=status.HTTP_200_OK)
        return Response("You are wrong")
    return Response("Do not have access")

def create_and_send_mail_and_return_answer(serializer):
    if serializer.is_valid():
        serializer.save()
        send.delay(serializer.validated_data["page"].id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response("Something wrong")


def create_like_or_unlike(request, serializer, pk, mod):
    if serializer.is_valid():
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        if mod:
            posts = Post.objects.filter(like_fil__user_from=request.user)
        else:
            posts = Post.objects.filter(unlike_fil__user_from=request.user)
        if post in posts:
            return Response("You already created this for this post")
        else:
            serializer.save(post_to=post, user_from=user)
            return Response(status=status.HTTP_201_CREATED)
    return Response("Something wrong, try again")

def search_and_return_answer(value):
    if value.is_valid():
        search = value.validated_data["search"]
        user_vector = SearchVector('username')
        pages_vector = SearchVector('name', 'uuid', 'tags__name')
        query = SearchQuery(search)
        users = User.objects.annotate(rank=SearchRank(user_vector, query)).filter(rank__gte=0.001, is_blocked=False).\
            order_by('-rank')
        pages = Page.objects.annotate(rank=SearchRank(pages_vector, query)).filter(rank__gte=0.001, is_blocked=False). \
            order_by('-rank')
        users = UserSerializer(users, many=True)
        pages = PageSerializer(pages, many=True)
        return Response({
            'users': users.data,
            'pages': pages.data
        })
    return Response("Something wrong")
