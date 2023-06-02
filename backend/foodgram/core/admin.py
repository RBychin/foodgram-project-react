from django.contrib import admin
from .models import Tag, Recipe, Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    extra = 1
    model = RecipeIngredient

    fields = ('ingredient', 'amount')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'author')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')