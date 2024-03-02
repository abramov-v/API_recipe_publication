from django.conf import settings
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
from django.db import models


class Tag(models.Model):
    """Model representing a tag."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Tag name'
    )
    color = models.CharField(
        max_length=settings.MAX_COLOR_LENGTH,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                message='Enter a valid color in HEX format'
            )
        ],
        verbose_name='Tag color in HEX format'
    )
    slug = models.CharField(
        max_length=settings.MAX_SLUG_LENGTH,
        unique=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='The slug field contains forbidden characters'
            )
        ],
        verbose_name='Tag slug'
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredient(models.Model):
    """Model representing ingredients."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Ingredient name'
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_MEASURING_UNIT,
        verbose_name='Measurement unit'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} in ({self.measurement_unit})'


class Recipe(models.Model):
    """Model representing a recipe."""

    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe author',
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Recipe name',
    )
    image = models.ImageField(
        upload_to='recipes_images/',
        verbose_name='Image encoded in Base64 format',
    )
    text = models.TextField(
        max_length=settings.MAX_LENGTH_RECIPE_TEXT,
        verbose_name='Recipe description'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='List of ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='List of tag IDs'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                settings.MIN_COOK_TIME,
                message='Value should be greater than one minute'
            ),
            MaxValueValidator(
                settings.MAX_COOK_TIME,
                message='Value should be less than 32000 minutes'

            )
        ],
        verbose_name='Cooking time (in minutes)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'Recipe {self.name} from author {self.author}'


class Favorite(models.Model):
    """Model representing favorites."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recipe',
    )

    class Meta:
        verbose_name = 'Recipe in favorites'
        verbose_name_plural = 'Recipes in favorites'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'Recipe {self.recipe} in {self.user}'


class ShoppingCart(models.Model):
    """Model representing a shopping cart."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
        verbose_name='Recipes in shopping cart',
    )

    class Meta:
        verbose_name = 'Recipe in shopping cart'
        verbose_name_plural = 'Recipes in shopping cart'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} in shopping cart of {self.user}'


class RecipeIngredient(models.Model):
    """Model for linking recipes and ingredients."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                settings.MIN_AMOUNT_VALUE,
                message='Add at least one ingredient'
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT_VALUE,
                message='Too many ingredients'
            )
        ],
        verbose_name='Amount',
    )

    class Meta:
        verbose_name = 'Recipe ingredient'
        verbose_name_plural = 'Recipe ingredients'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.ingredient} for {self.recipe}'
