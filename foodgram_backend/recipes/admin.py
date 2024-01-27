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
    """Настройка админ зоны для модели Рецептов."""

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
        'Число добавлений этого рецепта в избранное'
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
        'Список ингредиентов')

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Список тегов'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка админ зоны для модели Ингредиентов."""

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
    """Настройка админ зоны для модели Тегов."""

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
    """Настройка админ зоны для рецептов в избранном."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройка админ зоны для модели рецептов в списке покупок."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройка админ зоны для модели Ингредиентов рецепта."""

    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )
