from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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

    def get_queryset(self):
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
            'user': self.request.user,
            'recipe': get_model_object(Recipe, kwargs)
        }
        favorite = get_filter_set(Favorite, data)

        if self.request.method == 'POST':
            if favorite.exists():
                return Response({'errors': 'Уже в избранном.'},
                                HTTPStatus.BAD_REQUEST)
            Favorite.objects.create(**data)
            serializer = CropRecipeSerializer(
                data.get('recipe'),
                many=False,
                context={'request': self.request}
            )
            return Response(serializer.data,
                            status=HTTPStatus.CREATED)

        if self.request.method == 'DELETE':
            if not favorite.exists():
                return Response({'error': 'Нет такого'},
                                status=HTTPStatus.BAD_REQUEST)
            favorite.delete()
            return Response({'detail': 'Удалено'},
                            status=HTTPStatus.NO_CONTENT)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='shopping_cart')
    def shopping_cart(self, *args, **kwargs):
        data = {
            'user': self.request.user,
            'recipe': get_model_object(Recipe, kwargs)
        }
        cart = ShoppingCart.objects.filter(**data)

        if self.request.method == 'POST':
            if cart.exists():
                return Response(HTTPStatus.BAD_REQUEST)
            ShoppingCart.objects.create(**data)
            return Response({'detail': 'OK'},
                            status=HTTPStatus.CREATED)

        if self.request.method == 'DELETE':
            if not cart.exists():
                return Response({'error': 'такого нету'},
                                status=HTTPStatus.BAD_REQUEST)
            cart.delete()
            return Response({'detail': 'Удаляем'},
                            status=HTTPStatus.NO_CONTENT)

    @action(methods=['GET'],
            detail=False,
            url_path='download_shopping_cart')
    def download_cart(self, *args, **kwargs):
        content = pdf_dw(self.request)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=f"list.txt"'

        return response
