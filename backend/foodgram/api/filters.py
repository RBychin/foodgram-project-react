from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from core.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )

    def filter_is_favorited(self, queryset, field, value):
        if not value and self.request.user.is_annonymous:
            return queryset
        return queryset.filter(
            favorites__user=self.request.user
        )

    class Meta:
        model = Recipe
        fields = ['author']


class IngredientSearchField(SearchFilter):
    search_param = 'name'
