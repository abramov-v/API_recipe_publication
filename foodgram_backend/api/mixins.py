from django.conf import settings
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    ingredients_for_create = IngredientCreateSerializer(many=True)
    tags_for_create = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)

    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set',
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'tags_for_create',
            'author',
            'ingredients',
            'ingredients_for_create',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        extra_kwargs = {'tags': {'write_only': True}, 'ingredients': {'write_only': True}}

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart_recipes.filter(recipe=obj).exists()

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        return value

    def validate_tags(self, tags):
        tag_list = []

        for tag in tags:
            query_set = Tag.objects.filter(id=tag.id)
            if not query_set.exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует')

        for tag in tags:
            if tag in tag_list:
                raise serializers.ValidationError(
                    'Теги должны быть уникальны.'
                )
            tag_list.append(tag)

        if len(tag_list) < 1:
            raise serializers.ValidationError('Отсутвуют теги.')
        return tags

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходима картинка для создания рецепта'
            )
        return value

    def validate(self, data):
        request_method = self.context['request'].method
        if request_method == 'PATCH':
            if 'tags' not in data:
                raise serializers.ValidationError(
                    {'tags': 'Это поле необходимо заполнить'}
                )

            if 'ingredients' not in data:
                raise serializers.ValidationError(
                    {'ingredients': 'Это поле необходимо заполнить'}
                )

            ingredient_ids = [item.get('id') for item in data.get(
                'ingredients', []
            )]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise serializers.ValidationError(
                    {'ingredients': 'Присутсвуют одинаковые ингредиенты'}
                )

        return data

    def create_ingredients(self, recipe, ingredients_for_create):
        seen_ingredients = set()
        create_ingredients = []

        for ingredient_data in ingredients_for_create:
            ingredient_id = ingredient_data['ingredient'].id
            if ingredient_id in seen_ingredients:
                raise serializers.ValidationError(
                    'Присутсвуют одинаковые ингредиенты'
                )
            seen_ingredients.add(ingredient_id)

            create_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )
            )

        RecipeIngredient.objects.bulk_create(create_ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()

            create_ingredients = [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
            RecipeIngredient.objects.bulk_create(
                create_ingredients
            )
        return super().update(instance, validated_data)