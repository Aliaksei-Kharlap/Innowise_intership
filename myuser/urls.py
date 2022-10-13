from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myuser import views

router = DefaultRouter()
router.register(r'users', views.UsersViewSet, basename="users")
router.register(r'auth', views.LoginViewSet, basename="auth")
router.register(r'block', views.UserBlockViewSet, basename="block")

urlpatterns = [
    path('', include(router.urls)),
]