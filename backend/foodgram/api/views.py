from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer, FollowSerializer, UserCustomSerializer
from core.models import Ingredient, Tag, Recipe, Follow
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .paginators import PageLimitPagination
from .filters import RecipeFilter, IngredientSearchField
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

User = get_user_model()


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageLimitPagination
    serializer_class = UserCustomSerializer

    def get_author(self, **kwargs):
        author_id = kwargs.get('id')
        author = Follow.objects.filter(user=self.request.user,
                                       following=User.objects.get(pk=author_id))
        return author

    @action(methods=['get'],
            detail=False,
            url_path='subscriptions')
    def subscriptions(self, *args, **kwargs):
        queryset = Follow.objects.filter(user=self.request.user)
        pagination = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pagination,
            many=True,
            context={'request': self.request}
        )
        return self.get_paginated_response(serializer.data)



class IngredientsView(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchField,)
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


# @api_view(['POST'])
# def subscribe_to_user(request, user_pk):
#     following = get_object_or_404(User, id=user_pk)
#     Follow.objects.create(
#         user=request.user,
#         following=following
#     )
#     return Response({'message': 'Successfully subscribed to user.'})
#
# @api_view('DELETE')
# def unsubscribe(request, user_pk):
#     following = get_object_or_404(User, id=user_pk)
#     Follow.objects.filter(user=request.user, following=following).delete()
#     return Response({'message': 'Successfully unsubscribed from user.'})