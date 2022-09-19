from django.contrib.auth.models import AbstractUser
from django.db import models

from myuser.models import User


class Tag(models.Model):
   name = models.CharField(max_length=30, unique=True)


class Page(models.Model):
   name = models.CharField(max_length=80)
   uuid = models.CharField(max_length=30, unique=True)
   description = models.TextField()
   tags = models.ManyToManyField('facebookk.Tag', related_name='pages')
   owner = models.ForeignKey('myuser.User', on_delete=models.CASCADE, related_name='relpages')
   followers = models.ManyToManyField('myuser.User', related_name='follows')
   image = models.URLField(null=True, blank=True)
   is_private = models.BooleanField(default=False)
   follow_requests = models.ManyToManyField('myuser.User', related_name='requests')
   created_date = models.DateTimeField(auto_now_add=True)
   unblock_date = models.DateTimeField(null=True, blank=True)


class Post(models.Model):
   page = models.ForeignKey('facebookk.Page', on_delete=models.CASCADE, related_name='posts')
   content = models.CharField(max_length=180)
   reply_to = models.ForeignKey('facebookk.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      ordering = ['created_at']