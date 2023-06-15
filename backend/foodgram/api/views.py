from core.helpers import CustomModelViewSet
from core.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from core.pdfgen import pdf_dw
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import IngredientSearchField, RecipeFilter
from .paginators import PageLimitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer)

User = get_user_model()


class IngredientsView(ReadOnlyModelViewSet):
    """Представление для Ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchField,)
    search_fields = ['^name']


class TagView(ReadOnlyModelViewSet):
    """Представление Тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeView(CustomModelViewSet):
    """Представление Рецептов с фильтрацией по тегам
    Включая методы для добавления рецепта в избранное и корзину."""

    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='favorite')
    def favorite(self, request, *args, **kwargs):
        return self.manage_favorite_cart(Favorite)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='shopping_cart',
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, *args, **kwargs):
        return self.manage_favorite_cart(ShoppingCart)

    @action(methods=['GET'], detail=False, url_path='download_shopping_cart')
    def download_cart(self, *args, **kwargs):
        if not self.request.user.cart.all():
            raise ValidationError({'errors': 'Корзина пуста.'})
        content = pdf_dw(self.request)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response
