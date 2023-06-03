from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from core.models import Ingredient, Tag, Recipe
from django_filters.rest_framework import DjangoFilterBackend
from .paginators import PageLimitPagination
from .filters import RecipeFilter, IngredientSearchField


User = get_user_model()


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination


class IngredientsView(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchField, )
    search_fields = ['^name']


class TagView(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeView(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.validated_data['author'] = self.request.user
        serializer.save()