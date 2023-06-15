from django.urls import include, path, re_path
from rest_framework import routers

from users.views import UsersViewSet

from .views import IngredientsView, RecipeView, TagView

router = routers.DefaultRouter()

router.register('users', UsersViewSet)
router.register('ingredients', IngredientsView)
router.register('tags', TagView)
router.register('recipes', RecipeView)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

]
