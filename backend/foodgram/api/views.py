from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from core.models import Ingredient, Tag, Recipe

User = get_user_model()


class IngredientsView(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagView(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeView(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.validated_data['author'] = self.request.user
        serializer.save()


class UsersViewSet(UserViewSet):
    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)


