from django.contrib import admin

from facebookk.models import Post, Page, Tag, Like, UnLike

admin.site.register(Post)
admin.site.register(Page)
admin.site.register(Tag)
admin.site.register(Like)