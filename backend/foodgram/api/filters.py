from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from core.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter_cart_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_cart_favorite'
    )
    tags = filters.Filter(method='filter_tags')

    def filter_cart_favorite(self, queryset, field, value):
        field_map = {'is_in_shopping_cart': 'recipe_in_cart__user',
                     'is_favorited': 'favorites__user'}
        if field:
            if value:
                return queryset.filter(**{
                    field_map.get(field): self.request.user}
                                       )
        return queryset

    def filter_tags(self, queryset, field, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    class Meta:
        model = Recipe
        fields = ['author',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'tags']


class IngredientSearchField(SearchFilter):
    search_param = 'name'
