from django.conf import settings
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, value):
        user = self.context['request'].user
        return user.is_authenticated and Subscription.objects.filter(
            user=user,
            author=value
        ).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи рецепта и ингредиентов."""

    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатора для получения рецептов."""

    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

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


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента при создании рецепта."""

    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = (
            'recipe',
            'id',
            'amount'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализаторя для создания рецепта."""

    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

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

    def create_ingredients(self, recipe, ingredients_data):
        seen_ingredients = set()
        create_ingredients = []

        for ingredient_data in ingredients_data:
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

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в избранном и в списке покупок."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователей."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get(
            'recipes_limit',
            settings.DEFAULT_RECIPES_LIMIT)
        recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipeForSubscriptionSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()
