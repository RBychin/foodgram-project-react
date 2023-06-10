import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import (
    UserCreateSerializer as DUCreateSerializer,
    UserSerializer
)
from rest_framework import serializers

from core.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Follow,
    Favorite,
    ShoppingCart
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Кодирование в битную строку для использования с JSON"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCustomSerializer(UserSerializer):
    """Сериализация полей объекта модели Пользователя и
    получение поля Подписки на пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user, author=obj
            ).exists()
        return False


class UserCreateSerializer(DUCreateSerializer):
    """Сериализатор для создания объекта модели Пользователя
    с проверкой обязательных полей при POST запросе."""

    class Meta(DUCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'first_name',
            'last_name',
            'username',
            'password'
        )
        extra_kwargs = {'first_name': {'required': True},
                        'last_name': {'required': True},
                        'email': {'required': True}}


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор объекта модели Ингредиенты."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор объекта модели Теги."""
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели Рецепт-Ингредиент,
    связывает Ингредиент с Рецептом, добавляя поле Amount."""

    id = serializers.IntegerField(
        source='ingredient.id'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
            'measurement_unit',
            'name'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализация объекта модели Рецепт.
    В Сериализаторе происходит валидация Тегов и Ингредиентов,
    Организованы методы для POST и PATCH запросов,
    Включены методы для генерации полей Избранное и Корзина."""

    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set'
    )
    author = UserCustomSerializer(
        read_only=True
    )
    image = Base64ImageField()
    tags = serializers.ListSerializer(
        child=serializers.CharField()
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, attrs):
        ingredients = self.initial_data.get('ingredients')
        ingredient_list = []
        for ingredient in ingredients:
            if ingredient.get('id') in ingredient_list:
                raise serializers.ValidationError({
                    'errors': 'Проверьте добавленные ингредиенты.'
                })
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError({
                    'errors': 'значение не может быть меньше 1.'
                })
            ingredient_list.append(ingredient.get('id'))

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'errors': 'не указан не один тег'
            })
        return attrs

    def get_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        self.is_valid()
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        ingredients_data = validated_data.pop('recipeingredient_set')
        self.create_ingredients(ingredients_data, instance)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        if self.get_user().is_anonymous:
            return False
        if Favorite.objects.filter(
                user=self.get_user(),
                recipe=obj
        ).exists():
            return True

    def get_is_in_shopping_cart(self, obj):
        if self.get_user().is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=self.get_user(),
            recipe=obj
        ).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        tags = TagSerializer(instance.tags.all(), many=True).data
        data['tags'] = tags
        return data


class CropRecipeSerializer(serializers.ModelSerializer):
    """Урезанный сериализатор для объекта модели Рецепта,
    для представления во вложенных словарях."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор объекта модели Подписки."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return CropRecipeSerializer(queryset, many=True).data

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
