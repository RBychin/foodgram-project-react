from django.urls import path, include, re_path
from rest_framework import routers

from .views import UsersViewSet

router = routers.DefaultRouter()

router.register('users', UsersViewSet)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

]
