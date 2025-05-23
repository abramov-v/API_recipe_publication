from django.conf import settings

from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user model."""

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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and user.subscriptions.filter(
            author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

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
    """Serializer for the tag model."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the ingredient model."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for the recipe-ingredient relationship model."""

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
    """Serializer for retrieving recipes."""

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
    """Serializer for the ingredient when creating a recipe."""

    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True,
        min_value=settings.MIN_AMOUNT_VALUE,
        max_value=settings.MAX_AMOUNT_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'recipe',
            'id',
            'amount'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a recipe."""

    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        min_value=settings.MIN_COOK_TIME,
        max_value=settings.MAX_COOK_TIME
    )

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
        if not value:
            raise serializers.ValidationError(
                'Add at least one ingredient.'
            )
        return value

    def validate_tags(self, tags):
        tag_list = []

        for tag in tags:
            query_set = Tag.objects.filter(id=tag.id)
            if not query_set.exists():
                raise serializers.ValidationError(
                    'The specified tag does not exist.')

        for tag in tags:
            if tag in tag_list:
                raise serializers.ValidationError(
                    'Tags must be unique.'
                )
            tag_list.append(tag)

        if not tag_list:
            raise serializers.ValidationError('No tags are present.')
        return tags

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'An image is required to create a recipe.'
            )
        return value

    def validate(self, data):
        request_method = self.context['request'].method
        if request_method == 'PATCH':
            if 'tags' not in data:
                raise serializers.ValidationError(
                    {'tags': 'This field is required.'}
                )

            if 'ingredients' not in data:
                raise serializers.ValidationError(
                    {'ingredients': 'This field is required.'}
                )

            ingredient_ids = [item.get('id') for item in data.get(
                'ingredients', []
            )]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise serializers.ValidationError(
                    {'ingredients': 'Duplicate ingredients are present.'}
                )

        return data

    def create_ingredients(self, recipe, ingredients_data):
        seen_ingredients = set()
        create_ingredients = []

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient'].id
            if ingredient_id in seen_ingredients:
                raise serializers.ValidationError(
                    'Duplicate ingredients are present.'
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
            self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context={
            'request': self.context['request']
        }).data


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for recipes in favorites and shopping list."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Serializer for displaying user subscriptions."""

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
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
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
        user = self.context['request'].user
        return user.is_authenticated and user.subscriptions.filter(
            author=obj).exists()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and deleting subscriptions."""

    class Meta:
        model = Subscription
        fields = ['author']

    def validate(self, data):
        user = self.context['request'].user
        author = data.get('author')

        if user == author:
            raise serializers.ValidationError(
                'Cannot subscribe to oneself.'
            )

        if user.subscriptions.filter(author=author).exists():
            raise serializers.ValidationError(
                {'detail': 'You are already subscribed to this user.'}
            )

        return data
