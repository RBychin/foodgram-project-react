from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.constraints import UniqueConstraint

from foodgram import settings

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Тег', max_length=settings.MAX_LENGTH,
        unique=True,
    )
    color = ColorField(format='hexa',
                       verbose_name='цвет',
                       unique=True)
    slug = models.SlugField(
        'Slug', max_length=settings.MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=settings.MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=settings.MAX_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент',
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag, verbose_name='Тег',
        related_name='tags'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LENGTH
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='core/images/'
    )
    text = models.CharField(
        'Описание рецепта',
        max_length=settings.MAX_LENGTH
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True)

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'http://{settings.HOST}/recipes/{self.pk}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, message='не может быть меньше 1')]
    )

    class Meta:
        UniqueConstraint(fields=['recipe', 'ingredient'],
                         name='unique_ingredient')

    def __str__(self):
        return str(self.amount)


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        UniqueConstraint(fields=['user', 'recipe'], name='unique_favorites')


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ['user__id']
        UniqueConstraint(fields=['user', 'author'], name='unique_follow')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_in_cart'
    )

    class Meta:
        UniqueConstraint(fields=['user', 'recipe'], name='unique_cart')
