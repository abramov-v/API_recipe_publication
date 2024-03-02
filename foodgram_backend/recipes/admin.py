from django.contrib import admin

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingCart,
    RecipeIngredient
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin setup for the Recipe model."""

    list_display_links = ('name',)
    list_display = (
        'name',
        'author',
        'image',
        'text',
        'get_ingredients',
        'get_tags',
        'cooking_time',
        'pub_date',
        'favorites_count',
    )
    list_editable = (
        'text',
    )
    search_fields = (
        'name',
        'author',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = (
        'Number of times this recipe has been favorited.'
    )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ', '.join(
            [f'\n{ingredient.ingredient.name} '
             f'- {ingredient.amount} '
             f'{ingredient.ingredient.measurement_unit}\n'
             for ingredient in ingredients]
        )
    get_ingredients.short_description = (
        'List of ingredients')

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'List of tags'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin setup for the Ingredient model."""

    list_display = (
        'name',
        'measurement_unit'
    )
    list_display_links = ('name',)
    list_editable = (
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin setup for the Tag model."""

    list_display_links = ('name',)
    list_display = (
        'name',
        'color',
        'slug'
    )
    list_editable = (
        'color',
        'slug'
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin setup for favorite recipes."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin setup for recipes in the shopping list model."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Admin setup for the RecipeIngredient model."""

    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )
