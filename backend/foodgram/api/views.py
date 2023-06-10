from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ValidationError

from core.models import (Ingredient,
                         Tag,
                         Recipe,
                         Favorite,
                         ShoppingCart)
from core.pdfgen import pdf_dw
from .filters import (
    RecipeFilter,
    IngredientSearchField
)
from .paginators import PageLimitPagination
from .permissions import (
    IsAdminOrReadOnly,
    IsOwnerOrReadOnly
)
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    CropRecipeSerializer
)

User = get_user_model()


def get_model_object(model, data):
    """Получает объект модели или возвращает ошибку 404"""
    return get_object_or_404(
        model, **data
    )


def get_filter_set(model, data):
    return model.objects.filter(**data)


class IngredientsView(ModelViewSet):
    """Представление для Ингредиентов"""

    queryset = Ingredient.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchField,)
    search_fields = ['^name']


class TagView(ModelViewSet):
    """Представление Тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class RecipeView(ModelViewSet):
    """Представление Рецептов с фильтрацией по тегам
    Включая методы для добавления рецепта в избранное и корзину."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def cart_favorite_add(self, data):
        """Метод принимает словарь из моделей,
        выполняет запись в БД и
        возвращает сериализованные данные."""
        relate = data.pop('relate')
        query = get_filter_set(relate, data)
        if query.exists():
            raise ValidationError({'errors': 'Уже в избранном.'})
        relate.objects.create(**data)
        serializer = CropRecipeSerializer(
            data.get('recipe'),
            many=False,
            context={'request': self.request}
        )
        return Response(serializer.data,
                        status=HTTPStatus.CREATED)

    def cart_favorite_del(self, data):
        """Метод принимает словарь из моделей,
        выполняет удаление из БД и
        возвращает сериализованные данные."""
        relate = data.pop('relate')
        query = get_filter_set(relate, data)
        if not query.exists():
            raise ValidationError({'errors': 'У вас нет такого рецепта.'})
        query.delete()
        return Response({'detail': 'Удалено'},
                        status=HTTPStatus.NO_CONTENT)

    def get_queryset(self):
        """Выполняет фильтрацию по тегам."""
        if 'tags' in self.request.GET:
            tags = self.request.GET.getlist('tags')
            data = {'tags__slug__in': tags}
            return get_filter_set(Recipe, data).distinct()
        return self.queryset

    def perform_create(self, serializer):
        serializer.validated_data['author'] = self.request.user
        serializer.save()

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='favorite')
    def favorite(self, *args, **kwargs):
        data = {
            'relate': Favorite,
            'user': self.request.user,
            'recipe': get_model_object(Recipe, kwargs)
        }
        if self.request.method == 'POST':
            return self.cart_favorite_add(data)

        if self.request.method == 'DELETE':
            return self.cart_favorite_del(data)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='shopping_cart')
    def shopping_cart(self, *args, **kwargs):
        data = {
            'relate': ShoppingCart,
            'user': self.request.user,
            'recipe': get_model_object(Recipe, kwargs)
        }
        if self.request.method == 'POST':
            return self.cart_favorite_add(data)

        if self.request.method == 'DELETE':
            return self.cart_favorite_del(data)

    @action(methods=['GET'],
            detail=False,
            url_path='download_shopping_cart')
    def download_cart(self, *args, **kwargs):
        if not self.request.user.cart.all():
            raise ValidationError({'errors': 'Корзина пуста.'})
        content = pdf_dw(self.request)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'

        return response
