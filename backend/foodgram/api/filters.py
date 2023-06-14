from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from core.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter_cart_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_cart_favorite'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def filter_cart_favorite(self, queryset, field, value):
        field_map = {'is_in_shopping_cart': 'recipe_in_cart__user',
                     'is_favorited': 'favorites__user'}
        if field:
            if value:
                return queryset.filter(**{
                    field_map.get(field): self.request.user}
                                       )
        return queryset

    class Meta:
        model = Recipe
        fields = ['author',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'tags']


class IngredientSearchField(SearchFilter):
    search_param = 'name'
