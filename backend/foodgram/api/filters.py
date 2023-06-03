from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from core.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    # author = filters.

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientSearchField(SearchFilter):
    search_param = 'name'
