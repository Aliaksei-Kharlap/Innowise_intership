from django.urls import path, include
from rest_framework.routers import DefaultRouter
from facebookk import views


router = DefaultRouter()
router.register(r'pages', views.PagesViewSet, basename="pages")
router.register(r'posts', views.PostsViewSet, basename="posts")
router.register(r'search', views.SearchViewSet, basename="search")


urlpatterns = [
    path('', include(router.urls)),

]
