from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myuser import views

router = DefaultRouter()
router.register(r'users', views.UsersViewSet, basename="users")

urlpatterns = [
    path('', include(router.urls)),
]