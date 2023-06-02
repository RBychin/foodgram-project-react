from djoser.serializers import UserCreateSerializer as DUCreateSerializer, UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Tag, Ingredient, Recipe, RecipeIngredient
import base64
from django.core.files.base import ContentFile
from django.db.transaction import atomic

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCreateSerializer(DUCreateSerializer):
    class Meta(DUCreateSerializer.Meta):
        model = User
        fields = '__all__'
        extra_kwargs = {'first_name': {'required': True},
                        'last_name': {'required': True},
                        'email': {'required': True}}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'email': representation['email'],
            'id': representation['id'],
            'username': representation['username'],
            'first_name': representation['first_name'],
            'last_name': representation['last_name'],
        }

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        password = validated_data.get('password')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')

        user = User.objects.create_user(email=email,
                                        username=username,
                                        password=password,
                                        first_name=first_name,
                                        last_name=last_name)

        return user


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    measurement_unit = serializers.CharField(read_only=True, source='ingredient.measurement_unit')
    name = serializers.CharField(read_only=True, source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'measurement_unit', 'name')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, source='recipeingredient_set')
    author = UserCreateSerializer(read_only=True)
    image = Base64ImageField()
    # При добавлении tags - из validated_data исчезает ключ 'tags'.
    # tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['ingredient']['id'])
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=ingredient_data['amount'])
        return recipe