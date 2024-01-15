from django.conf import settings
from typing import Optional

from django.db import models
from django.db.models import Exists, OuterRef
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель представляет тег блюда."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=settings.MAX_COLOR_LENGTH,
        null=True,
        unique=True,
        verbose_name='Цвет тега в HEX'
    )
    slug = models.CharField(
        max_length=settings.MAX_SLUG_LENGTH,
        unique=True,
        null=True,
        verbose_name='Cлаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель представляет данные об ингредиентах."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_MEASURING_UNIT,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель представляет рецепт блюда."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Название блюда',
    )
    image = models.ImageField(
        upload_to='food_image/',
        verbose_name='Картинка блюда'
    )
    text = models.TextField(
        max_length=settings.MAX_LENGTH_RECIPE_TEXT,
        verbose_name='Описание блюда'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Список ингредиентов'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=settings.MIN_COOK_TIME,
        verbose_name='Время приготовления'
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'Блюдо {self.name}. Автор {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts',
        verbose_name='Рецепты в списке покупок',
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart_user_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} в корзине {self.user}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, 
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        default=settings.MIN_AMOUNT_VALUE,
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self) -> str:
        return f'{self.ingredient} для {self.recipe}'


class RecipeQuerySet(models.QuerySet):

    def add_user_annotations(self, user_id: Optional[int]):
        return self.annotate(
            is_favorite=Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
        )
