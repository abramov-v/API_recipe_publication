from django.conf import settings
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
from django.db import models


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
        validators=[
            RegexValidator(
                regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                message='Введите корректный цвет в формате HEX'
            )
        ],
        verbose_name='Цвет тега в HEX формате'
    )
    slug = models.CharField(
        max_length=settings.MAX_SLUG_LENGTH,
        unique=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Поле slug содержит запрещенные символы'
            )
        ],
        verbose_name='slug тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель представляет ингредиенты блюда."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_MEASURING_UNIT,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} в ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель представляет рецепт блюда."""

    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название блюда',
    )
    image = models.ImageField(
        upload_to='recipes_images/',
        verbose_name='Картинка, закодированная в формат Base64',
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
        verbose_name='Список id тегов'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                settings.MIN_COOK_TIME,
                message='Значение должно быть больше чем одна минута'
            ),
            MaxValueValidator(
                settings.MAX_COOK_TIME,
                message='Значение должно быть меньше 32000 минут'

            )
        ],
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'Блюдо {self.name} от автора {self.author}'


class Favorite(models.Model):
    """Модель для добавки рецепта в избранное."""

    user = models.ForeignKey(
        'users.User',
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
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
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
    """Модель для добавления рецепта в список покупок."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
        verbose_name='Рецепты в списке покупок',
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} в списке покупок у {self.user}'


class RecipeIngredient(models.Model):
    """Модель для связи рецепта и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                settings.MIN_AMOUNT_VALUE,
                message='Добавьте хотябы один ингредиент'
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT_VALUE,
                message='Слишком много ингредиентов'
            )
        ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.ingredient} для {self.recipe}'
