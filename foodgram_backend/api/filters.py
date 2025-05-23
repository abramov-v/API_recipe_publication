from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag
from users.models import User


class IngredientSearchFilter(SearchFilter):
    """
    Filter class for ingredient search.
    Uses the 'name' parameter for searching.
    """

    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """
    Class for filtering recipes.
    Allows filtering recipes by favorites,
    presence in shopping cart, author, and tags.
    """

    is_favorited = filters.BooleanFilter(
        method='recipe_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='recipe_is_in_shopping_cart'
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def recipe_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def recipe_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(is_in_shopping_cart__user=self.request.user)
        return queryset
