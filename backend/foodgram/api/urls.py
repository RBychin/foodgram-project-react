from django.urls import path, include, re_path
from rest_framework import routers

from .views import IngredientsView, TagView, RecipeView
from users.views import UsersViewSet

router = routers.DefaultRouter()

router.register('users', UsersViewSet)
router.register('ingredients', IngredientsView)
router.register('tags', TagView)
router.register('recipes', RecipeView)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

]
