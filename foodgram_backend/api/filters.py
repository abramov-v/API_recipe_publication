from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from recipes.models import Recipe

from users.models import User


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='recipe_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='recipe_is_in_shopping_cart')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def recipe_is_favorited():
        ...

    def recipe_is_in_shopping_cart():
        ...

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
